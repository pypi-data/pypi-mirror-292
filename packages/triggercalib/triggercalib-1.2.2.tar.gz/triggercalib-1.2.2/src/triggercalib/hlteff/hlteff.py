###############################################################################
# (c) Copyright 2024 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

from array import array
import itertools as it
import logging
import json
import numpy as np
import os
from ROOT import (
    RDataFrame,
    RooAbsPdf,
    RooAbsReal,
    RooArgSet,
    RooDataSetHelper,
    RooRealVar,
    std,
    TFile,
    TH1D,
    TH2,
    TH2D,
)
from ROOT.RooStats import SPlot
from ROOT.RDF import RunGraphs
from typing import Dict, List, Literal, Union
from uncertainties import ufloat

from .objects import Plot, Sideband


class HltEff:

    # Magic methods #

    def __init__(  # <- TODO: order the arguments!
        self,
        name: str,
        path: Union[str, List[str]],  # <- TODO: add direct passing of RDataFrame object
        tag: Union[str, List[str]],  # <- line(s) to be used as the tag
        probe: Union[str, List[str]],  # <- line(s) to be used as the probe
        particle: str,
        binning: Union[
            str, Dict[str, Dict[str, Union[List[float], str]]]
        ] = {},  # <- provide binning directly as dict or as path to .json/.yaml file
        cut: Union[str, List[str]] = "",
        observable: RooAbsReal = None,
        pdf: RooAbsPdf = None,
        sideband: Dict[str, List[float]] = None,
        sweights: Union[bool, str] = False,
        expert_mode: bool = False,
        lazy: bool = False,
        plots: bool = True,
        prefix: str = "",
        output_path: str = "",
        threads: int = 1,
        verbose: bool = False,
    ):

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
        self.logger.info(f"Initialising HltEff object {name}")

        self.name = name
        self.particle = particle
        self.tag = self._parse_selection(tag, "TIS")
        self.probe = self._parse_selection(probe, "TOS")
        self.selection = self._parse_selection(probe)

        if isinstance(path, str):
            path = [path]

        self.tree = ""
        self.path = []
        for path_i in path:
            p_i, t_i = path_i.rsplit(":", 1)
            assert t_i == self.tree or not (self.tree), ValueError(
                "Paths provided must all refer to the same tree"
            )
            self.tree = t_i
            self.path.append(p_i)
        # ^- TODO: move into _validate_paths
        self.cut = [cut] if isinstance(cut, str) and len(cut) > 0 else cut
        self.rdf = self._load_rdf()

        if isinstance(binning, str):
            with open(binning, "r") as binning_file:
                binning = json.load(binning_file)
        self.set_binning(binning)

        self.observable = observable
        self.pdf = pdf
        assert bool(observable) == bool(pdf), ValueError(
            "If observable is provided, then pdf must also be provided (and vice versa)"
        )

        self.sweights = sweights
        self.output_path = output_path
        if output_path and not os.path.exists(output_path):
            os.makedirs(output_path)
        self.fit_path = os.path.join(output_path, "fits")
        if not os.path.exists(self.fit_path):
            os.makedirs(self.fit_path)

        self.plot_path = os.path.join(output_path, "plots") if plots else None
        self.threads = threads
        self.expert_mode = expert_mode

        self.method = "raw"

        assert not (bool(sideband) and bool(pdf)), ValueError(
            "Sideband and fit model cannot both be provided"
        )

        self._min_entries_for_fit = 20  # <- TODO: configure this from an argument

        if sideband:
            assert len(sideband.keys()) == 1, ValueError(
                "Sideband should be provided as a single-entry dictionary"
            )
            self.method = "sideband"
            sideband_var = list(sideband.keys())[0]
            sideband_range = sideband[sideband_var]
            assert "range" in sideband_range and "sideband" in sideband_range
            if (
                "signal" not in sideband_range
            ):  # If no signal range given, assume that the range between the sidebands is the signal range
                sideband_range["signal"] = sideband_range["sideband"]

            self.sideband = Sideband(
                sideband_var,
                sideband_range["range"],
                sideband_range["sideband"],
                sideband_range["signal"],
            )
            self.logger.info(f"Count mode '{self.method}' chosen")
        else:
            self.sideband = None
            if pdf:
                self.method = "sweights" if self.sweights else "fit_count"
                self.logger.warning(f"Count mode '{self.method}' chosen")
            else:
                assert expert_mode, RuntimeError(
                    "Expert mode must be enabled to use 'raw' count mode"
                )

        self.verbose = verbose
        if lazy:
            self._counts = {}
            self._efficiencies = {}
            self._sweights = {}
        else:
            assert self.binning, RuntimeError(
                "Binning must be provided at initialisation unless running in lazy mode, i.e. lazy = True"
            )
            self.counts(prefix)
            self.efficiencies(prefix)

    def __getitem__(self, key):

        assert key in ("counts", "efficiencies"), ValueError(
            "Can only obtain 'counts' or 'efficiencies' objects"
        )
        if key == "counts":
            return self._counts
        return self._efficiencies

    def set_binning(
        self,
        scheme: Dict[str, Union[List[float], float, str]],
        compute_bins: bool = False,
        cut: Union[
            str, List[str]
        ] = "",  # Only applied when binning is being generated (i.e., scheme["bins"] is not a Dict)
    ):

        assert all("bins" in entry for entry in scheme.values()), ValueError(
            "Binning scheme does not contain argument 'bins'"
        )
        if compute_bins:
            self.binning_scheme = {}
            # Compute bins if a list of bins is given instead of the bins themselves
            rdf = self.rdf

            if cut and len(cut) > 0:
                if isinstance(cut, str):
                    cut = [cut]
                for cut_i in cut:
                    rdf = rdf.Filter(cut_i)

            # Before computing bins, apply cuts on each dimension
            for var, entry in scheme.items():
                if isinstance(entry["bins"], List):
                    _, lower, upper = entry["bins"]
                    rdf = rdf.Filter(f"({var} > {lower}) & ({var} < {upper})")

            df = rdf.AsNumpy((var for var in scheme.keys()))
            for var, entry in scheme.items():
                if isinstance(entry["bins"], float):
                    nbins = entry["bins"]
                    lower = np.min(df[var])
                    upper = np.max(df[var])
                else:
                    nbins, lower, upper = entry["bins"]

                edges = np.quantile(df[var], np.arange(1, nbins) / nbins)
                edges = np.append((lower,), np.append(edges, (upper,)))
                self.binning_scheme[var] = {
                    "bins": list(edges),
                    "label": entry["label"] if "label" in scheme else var,
                }

            self.set_binning(self.binning_scheme)
        else:
            self.binning_scheme = scheme
            self.binning = {
                var: entry["bins"] for var, entry in self.binning_scheme.items()
            }
            assert all(
                bins[n + 1] > bins[n]
                for bins in self.binning.values()
                for n in range(len(bins) - 1)
            ), ValueError("Bins must be increasing")
            self.variables = {
                var: entry["label"] if "label" in entry else var
                for var, entry in self.binning_scheme.items()
            }
            self.midpoints = [
                (np.array(axis_bins[1:]) + np.array(axis_bins[:-1])) / 2
                for axis_bins in self.binning.values()
            ]
            self.nbins = np.prod([len(b) for b in self.midpoints])

        self.logger.info(
            f"Binning scheme set for variables '{', '.join(self.variables.keys())}'"
        )

    def counts(self, prefix=""):

        self._counts = {}
        assert self.binning and self.path and self.tree, ValueError(
            "Path, tree and binning must all be set before calculating counts"
        )

        self._counts = {}
        prefix = f"{prefix}_" if prefix else ""

        if self.method == "fit_count":  # <- TODO: require fit model
            _counts = self._fit_count(prefix)
        else:
            _counts = self._hist_count(prefix)

        for category in ("tis", "tos"):
            _counts[
                f"{prefix}{category}_only_count_{'_'.join(self.variables.keys())}"
            ] = _counts[
                f"{prefix}{category}_count_{'_'.join(self.variables.keys())}"
            ].Clone(
                f"{prefix}{category}_only_count_{'_'.join(self.variables.keys())}"
            )
            _counts[
                f"{prefix}{category}_only_count_{'_'.join(self.variables.keys())}"
            ].Add(
                _counts[f"{prefix}tistos_count_{'_'.join(self.variables.keys())}"], -1
            )

        for count_label, count_hist in dict(_counts).items():
            if self._to_project(count_label):
                _counts[
                    count_label.replace(
                        "_".join(self.variables.keys()), list(self.variables.keys())[0]
                    )
                ] = count_hist.ProjectionX()
                _counts[
                    count_label.replace(
                        "_".join(self.variables.keys()), list(self.variables.keys())[1]
                    )
                ] = count_hist.ProjectionY()

        self._counts = _counts
        return self._counts

    def efficiencies(self, prefix=""):

        self.logger.info("Calculating TIS, TOS and Trig efficiencies")

        self._efficiencies = {}
        _counts = self._counts
        prefix = f"{prefix}_" if prefix else ""

        # Calculate efficiencies #
        # ---------------------- #
        _efficiencies = {}
        axes = [None, 0, 1]
        suffixes = (
            [
                "_".join(self.variables.keys()),
                list(self.variables.keys())[0],
                list(self.variables.keys())[1],
            ]
            if len(self.variables.keys()) > 1
            else ["_".join(self.variables.keys())]
        )

        for axis, suffix in zip(axes, suffixes):

            # TOS efficiencies #
            _efficiencies[f"{prefix}tos_efficiency_{suffix}"] = self._simple_eff(
                f"{prefix}tos_efficiency_{suffix}",
                _counts[f"{prefix}tistos_count_{suffix}"],
                _counts[f"{prefix}tis_count_{suffix}"],
                axis=axis,
            )
            _efficiencies[f"{prefix}tos_total_efficiency_{suffix}"] = self._simple_eff(
                f"{prefix}tos_total_efficiency_{suffix}",
                _counts[f"{prefix}tistos_count_{suffix}"],
                _counts[f"{prefix}tis_count_{suffix}"],
                axis=axis,
                integrated=True,
            )

            # TIS efficiencies #
            _efficiencies[f"{prefix}tis_efficiency_{suffix}"] = self._simple_eff(
                f"{prefix}tis_efficiency_{suffix}",
                _counts[f"{prefix}tistos_count_{suffix}"],
                _counts[f"{prefix}tos_count_{suffix}"],
                axis=axis,
            )
            _efficiencies[f"{prefix}tis_total_efficiency_{suffix}"] = self._simple_eff(
                f"{prefix}tis_total_efficiency_{suffix}",
                _counts[f"{prefix}tistos_count_{suffix}"],
                _counts[f"{prefix}tos_count_{suffix}"],
                axis=axis,
                integrated=True,
            )

            # Trig. efficiencies #
            _efficiencies[f"{prefix}trig_efficiency_{suffix}"] = self._full_eff(
                f"{prefix}trig_efficiency_{suffix}",
                _counts[f"{prefix}trig_count_{suffix}"],
                _counts[f"{prefix}tistos_count_{suffix}"],
                _counts[f"{prefix}tis_count_{suffix}"],
                _counts[f"{prefix}tos_count_{suffix}"],
                _counts[f"{prefix}tis_only_count_{suffix}"],
                _counts[f"{prefix}tos_only_count_{suffix}"],
                axis=axis,
            )
            _efficiencies[f"{prefix}trig_total_efficiency_{suffix}"] = self._full_eff(
                f"{prefix}trig_total_efficiency_{suffix}",
                _counts[f"{prefix}trig_count_{suffix}"],
                _counts[f"{prefix}tistos_count_{suffix}"],
                _counts[f"{prefix}tis_count_{suffix}"],
                _counts[f"{prefix}tos_count_{suffix}"],
                _counts[f"{prefix}tis_only_count_{suffix}"],
                _counts[f"{prefix}tos_only_count_{suffix}"],
                axis=axis,
                integrated=True,
            )

        # Save efficiencies in class #
        # -------------------------- #
        self._efficiencies = _efficiencies

    def write(self, path, mode="RECREATE", prefix=""):
        prefix = f"{prefix}_" if prefix else ""
        path = path if path.startswith("/") else os.path.join(self.output_path, path)

        output_file = TFile.Open(path, mode)
        _results = {
            f"{prefix}counts": self._counts,
            f"{prefix}efficiencies": self._efficiencies,
        }
        for name, results in _results.items():
            if results:
                output_dir = output_file.mkdir(name)
                output_dir.cd()
                for key, hist in results.items():
                    hist.Write(key)

        output_file.Close()

    def write_bins(self, path):
        # assert # Bins exist
        with open(path, "w") as output_file:
            json.dump(
                self.binning,
                output_file,
                indent=4,
            )

    def _load_rdf(self):

        self.logger.info(
            f"Creating RDF from tree '{self.tree}' in path(s) '{self.path}'"
        )
        rdf = RDataFrame(self.tree, self.path)
        if self.cut and len(self.cut) > 0:
            for cut in self.cut:
                rdf = rdf.Filter(cut)
        return rdf

    def _parse_selection(
        self, selection: Union[str, List[str]], category: Literal["", "TIS", "TOS"] = ""
    ):
        if isinstance(selection, str):
            selection = [selection]

        cuts = []
        for level in ("Hlt1", "Hlt2"):
            cut = " || ".join(
                (
                    f"{self.particle}_{line}Decision_{category}"
                    if category
                    else f"{line}Decision"
                )
                for line in selection
                if line.startswith(level)
            )
            if cut:
                cuts += [f"({cut})"]
        print(" && ".join(cuts))
        return " && ".join(cuts)

    def _empty_th1d(self, name, binning=None):
        if not (binning):
            binning = self.binning

        bin_vars = list(binning.keys())
        assert len(bin_vars) > 0
        assert len(bin_vars) < 3

        if len(bin_vars) == 1:
            return TH1D(
                name,
                name,
                len(binning[bin_vars[0]]) - 1,
                array("d", binning[bin_vars[0]]),
            )
        else:
            return TH2D(
                name,
                name,
                len(binning[bin_vars[0]]) - 1,
                array("d", binning[bin_vars[0]]),
                len(binning[bin_vars[1]]) - 1,
                array("d", binning[bin_vars[1]]),
            )

    def _rdf_histo(self, rdf, name, weight="", binning=None):
        if not (binning):
            binning = self.binning

        bin_vars = list(binning.keys())
        assert len(bin_vars) > 0
        assert len(bin_vars) < 3

        if len(bin_vars) == 1:
            args = [
                (
                    name,
                    name,
                    len(binning[bin_vars[0]]) - 1,
                    array("d", binning[bin_vars[0]]),
                ),
                bin_vars[0],
            ]
            if weight:
                args += [weight]

            return rdf.Histo1D(*args)
        else:
            args = [
                (
                    name,
                    name,
                    len(binning[bin_vars[0]]) - 1,
                    array("d", binning[bin_vars[0]]),
                    len(binning[bin_vars[1]]) - 1,
                    array("d", binning[bin_vars[1]]),
                ),
                bin_vars[0],
                bin_vars[1],
            ]
            if weight:
                args += [weight]

            return rdf.Histo2D(*args)

    def _trigger_cut(self, category):
        assert category in ("tis", "tos", "tistos", "trig"), ValueError(
            "Category must be one of 'tis', 'tos', 'tistos' or 'trig'"
        )
        if category == "tis":
            return self.tag
        elif category == "tos":
            return self.probe
        elif category == "tistos":
            return f"({self.tag}) && ({self.probe})"
        return self.selection

    def _to_project(self, key, bin_requirement=True, include_mass=True):
        test_parts = [f"_{var}" for var in self.variables.keys()]
        if include_mass:
            test_parts += ["mass"]
        return (len(self.variables.keys()) > 1 or not bin_requirement) and not any(
            k in key and "_".join(self.variables.keys()) not in key for k in test_parts
        )

    def _run_fit(self, pdf, data):
        fit_result = pdf.fitTo(
            data,
            Extended=True,
            NumCPU=self.threads,
            Save=True,
            PrintLevel=1 if self.verbose else 0,
        )
        attempts = 1
        max_attempts = 3
        while attempts < max_attempts:
            attempts += 1
            if fit_result.status() == 0 and fit_result.covQual() == 3:
                break
            fit_result = pdf.fitTo(
                data,
                Extended=True,
                NumCPU=self.threads,
                Save=True,
                PrintLevel=1 if self.verbose else 0,
            )
        assert (
            fit_result.status() == 0
            and fit_result.covQual() == 3
            and not self.expert_mode
        ), RuntimeError("Fit did not converge, please reconfigure fit and try again")
        return fit_result

    def _fit_count(self, prefix=""):

        rdf = self._load_rdf()

        obs = self.observable

        observables = RooArgSet(
            obs,
        )
        dataset_ptrs = {}
        pdfs = {}

        _counts = {}
        for category in ("tis", "tos", "tistos", "trig", "sel"):
            _counts[f"{prefix}{category}_count_{'_'.join(self.variables.keys())}"] = (
                self._empty_th1d(
                    f"{prefix}{category}_count_{'_'.join(self.variables.keys())}"
                )
            )

            count_rdf = (
                rdf.Filter(self._trigger_cut(category)) if category != "sel" else rdf
            )

            for midpoint_coords in it.product(*self.midpoints):
                xaxis = _counts[
                    f"{prefix}{category}_count_{'_'.join(self.variables.keys())}"
                ].GetXaxis()
                xbin = xaxis.FindBin(midpoint_coords[0])
                xlow = xaxis.GetBinLowEdge(xbin)
                xup = xaxis.GetBinUpEdge(xbin)

                bin_cut = f"({list(self.variables.keys())[0]}>{xlow} && {list(self.variables.keys())[0]}<{xup})"

                dataset_name = f"{prefix}{category}_dataset_bin_{xbin}"
                if len(midpoint_coords) > 1:
                    yaxis = _counts[
                        f"{prefix}{category}_count_{'_'.join(self.variables)}"
                    ].GetYaxis()
                    ybin = yaxis.FindBin(midpoint_coords[1])
                    ylow = yaxis.GetBinLowEdge(ybin)
                    yup = yaxis.GetBinUpEdge(ybin)

                    bin_cut = f"{bin_cut} && ({list(self.variables.keys())[1]} > {ylow} && {list(self.variables.keys())[1]} < {yup})"
                    dataset_name = f"{dataset_name}_{ybin}"

                bin_rdf = count_rdf.Filter(bin_cut)
                dataset_ptrs[dataset_name] = bin_rdf.Book(
                    std.move(RooDataSetHelper(dataset_name, dataset_name, observables)),
                    (self.observable.GetName(),),
                )

                pdf_name = dataset_name.replace("_dataset_", "_pdf_")
                pdfs[pdf_name] = self.pdf.cloneTree(pdf_name)

        RunGraphs(dataset_ptrs.values())

        for category in ("tis", "tos", "tistos", "trig", "sel"):
            hist = _counts[f"{prefix}{category}_count_{'_'.join(self.variables)}"]

            for midpoint_coords in it.product(*self.midpoints):
                nbin = hist.FindBin(*midpoint_coords)
                xaxis = hist.GetXaxis()
                xbin = xaxis.FindBin(midpoint_coords[0])
                dataset_name = f"{prefix}{category}_dataset_bin_{xbin}"
                if len(midpoint_coords) > 1:
                    yaxis = hist.GetYaxis()
                    ybin = yaxis.FindBin(midpoint_coords[1])
                    dataset_name = f"{dataset_name}_{ybin}"

                data = dataset_ptrs[dataset_name].GetValue()
                pdf = pdfs[dataset_name.replace("_dataset_", "_pdf_")]

                fit_result = self._run_fit(pdf, data)

                with open(
                    os.path.join(
                        self.fit_path,
                        dataset_name.replace("_dataset_", "_") + "_fit.txt",
                    ),
                    "w",
                ) as result_file:
                    for var in fit_result.floatParsFinal():
                        result_file.write(
                            f"{var.GetName()}: {var.getVal()} +/- {var.getError()}\n"
                        )
                    result_file.write("\n\n")
                    result_file.write(f"Covariance quality: {fit_result.covQual()}\n")
                    result_file.write(f"Fit status: {fit_result.status()}\n")

                if self.plot_path:
                    plot_name = dataset_name.replace("_dataset_", "_").replace(
                        ".root", "_plot"
                    )

                    plot = Plot(plot_name, obs, data, pdf)
                    plot.save(self.plot_path)

                for coef in pdf.coefList():
                    if (
                        f"{prefix}{category}_{coef.GetName()}_count_{'_'.join(self.variables)}"
                        not in _counts
                    ):
                        _counts[
                            f"{prefix}{category}_{coef.GetName()}_count_{'_'.join(self.variables)}"
                        ] = hist.Clone(
                            f"{prefix}{category}_{coef.GetName()}_count_{'_'.join(self.variables)}"
                        )
                    temp_hist = _counts[
                        f"{prefix}{category}_{coef.GetName()}_count_{'_'.join(self.variables)}"
                    ]
                    temp_hist.SetBinContent(nbin, coef.getVal())
                    temp_hist.SetBinError(nbin, np.abs(coef.getError()))

                signal_count = pdf.coefList()[0]
                hist.SetBinContent(nbin, signal_count.getVal())
                hist.SetBinError(nbin, np.abs(signal_count.getError()))

        for category in ("tis", "tos"):
            _counts[f"{prefix}{category}_only_count_{'_'.join(self.variables)}"] = (
                _counts[f"{prefix}{category}_count_{'_'.join(self.variables)}"].Clone(
                    f"{prefix}{category}_only_count_{'_'.join(self.variables)}"
                )
            )
            _counts[f"{prefix}{category}_only_count_{'_'.join(self.variables)}"].Add(
                _counts[f"{prefix}tistos_count_{'_'.join(self.variables)}"], -1
            )

        return _counts

    def _compute_sweights(self, rdf, prefix=""):

        obs_list = [self.observable] + [
            RooRealVar(var, var, bins[0], bins[-1])
            for var, bins in self.binning.items()
        ]
        observables = RooArgSet(*obs_list)

        dataset_ptrs = {}
        pdfs = {}
        for category in ("tis", "tos", "tistos", "trig", "sel"):
            category_rdf = (
                rdf.Filter(self._trigger_cut(category)) if category != "sel" else rdf
            )

            dataset_name = f"{prefix}{category}_dataset"
            pdf_name = f"{prefix}{category}_pdf"

            dataset_ptrs[dataset_name] = category_rdf.Book(
                std.move(RooDataSetHelper(dataset_name, dataset_name, observables)),
                [o.GetName() for o in obs_list],
            )
            pdfs[pdf_name] = self.pdf.cloneTree(pdf_name)

        RunGraphs(dataset_ptrs.values())

        sweight_trees = {}
        for category in ("tis", "tos", "tistos", "trig", "sel"):

            data = dataset_ptrs[f"{prefix}{category}_dataset"].GetValue()
            pdf = pdfs[f"{prefix}{category}_pdf"]

            assert data.sumEntries() > self._min_entries_for_fit, RuntimeError(
                f"Insufficient events in the '{category}' category to perform sWeight fit"
            )
            fit_result = self._run_fit(pdf, data)

            with open(
                os.path.join(
                    self.fit_path,
                    f"{prefix}{category}_fit.txt",
                ),
                "w",
            ) as result_file:
                for var in fit_result.floatParsFinal():
                    result_file.write(
                        f"{var.GetName()}: {var.getVal()} +/- {var.getError()}\n"
                    )
                result_file.write("\n\n")
                result_file.write(f"Covariance quality: {fit_result.covQual()}\n")
                result_file.write(f"Fit status: {fit_result.status()}\n")

            if self.plot_path:
                plot_name = f"{prefix}{category}_plot"

                plot = Plot(plot_name, self.observable, data, pdf)
                plot.save(self.plot_path)

            splot = SPlot(
                f"{prefix}{category}_sdata",
                f"{prefix}{category}_sdata",
                data,
                pdf,
                pdf.coefList(),
            )
            sdata = splot.GetSDataSet()
            sweight_trees[category] = sdata.GetClonedTree()
            sweight_trees[category].SetName(f"{prefix}{category.capitalize()}DecayTree")

        sweight_path = os.path.join(self.output_path, "sweighted_data.root")
        with TFile.Open(sweight_path, "RECREATE") as sweight_file:
            sweight_file.cd()
            for category in ("tis", "tos", "tistos", "trig", "sel"):
                sweight_trees[category].Write()

        return sweight_path

    def _hist_count(self, prefix=""):

        rdf = self._load_rdf()
        ptrs = {}

        if self.sweights:
            sweight_path = self._compute_sweights(rdf, prefix=prefix)

        for category in ("tis", "tos", "tistos", "trig", "sel"):
            if self.sweights:
                _count_rdf = RDataFrame(
                    f"{prefix}{category.capitalize()}DecayTree", sweight_path
                )
            else:
                _count_rdf = (
                    rdf.Filter(self._trigger_cut(category))
                    if category != "sel"
                    else rdf
                )

            if self.sideband:  # <- TODO make loop over cuts
                mass_binning = {
                    self.sideband.variable: np.linspace(
                        self.sideband.range[0], self.sideband.range[1], 200
                    )
                }
                for cut_label, cut in zip(
                    ("all", "signal", "sideband"),
                    (
                        self.sideband.range_cut(),
                        self.sideband.signal_cut(),
                        self.sideband.sideband_cut(),
                    ),
                ):
                    _temp_rdf = _count_rdf.Filter(cut)
                    ptrs[
                        f"{prefix}{category}_{cut_label}_count_{'_'.join(self.variables)}"
                    ] = self._rdf_histo(
                        _temp_rdf,
                        f"{prefix}{category}_{cut_label}_count_{'_'.join(self.variables)}",
                    )
                    ptrs[f"{prefix}{category}_{cut_label}_mass"] = self._rdf_histo(
                        _temp_rdf,
                        f"{prefix}{category}_{cut_label}_mass",
                        binning=mass_binning,
                    )
            else:
                ptrs[
                    f"{prefix}{category}_unweighted_count_{'_'.join(self.variables)}"
                ] = self._rdf_histo(
                    _count_rdf,
                    f"{prefix}{category}_unweighted_count_{'_'.join(self.variables)}",
                )
                ptrs[f"{prefix}{category}_count_{'_'.join(self.variables)}"] = (
                    self._rdf_histo(
                        _count_rdf,
                        f"{prefix}{category}_count_{'_'.join(self.variables)}",
                        weight=(
                            f"{self.pdf.coefList()[0].GetName()}_sw"
                            if self.sweights
                            else ""
                        ),
                    )
                )

        RunGraphs([ptr for ptr in ptrs.values()])

        _counts = {}
        for key, count in ptrs.items():
            hist = count.GetValue()
            _counts[key] = hist
            if self._to_project(key):
                _counts[
                    key.replace(
                        "_".join(self.variables), list(self.variables.keys())[0]
                    )
                ] = hist.ProjectionX()
                _counts[
                    key.replace(
                        "_".join(self.variables), list(self.variables.keys())[1]
                    )
                ] = hist.ProjectionY()

        if self.sideband:
            for key in list(_counts.keys()):
                if (
                    self._to_project(key, bin_requirement=False, include_mass=False)
                    and "_signal_" in key
                ):
                    new_key = key.replace("_signal_", "_")
                    _counts[new_key] = _counts[key].Clone(new_key)

                    _subtract_hist = _counts[
                        key.replace("_signal_", "_sideband_")
                    ].Clone(f"{new_key}_subtract_hist")

                    if "count" in key:
                        _counts[new_key].Add(_subtract_hist, -1 * self.sideband.scale())
                    else:
                        _sideband_count = _counts[
                            key.replace("_signal_", "_sideband_")
                        ].GetEntries()

                        if _subtract_hist.GetNbinsY() > 1:
                            bin_nums = it.product(
                                (
                                    list(range(1, _subtract_hist.GetNbinsX() + 1)),
                                    list(range(1, _subtract_hist.GetNbinsY() + 1)),
                                )
                            )
                        else:
                            bin_nums = zip(
                                list(range(1, _subtract_hist.GetNbinsX() + 1))
                            )

                        for b in bin_nums:
                            n_bin = _subtract_hist.GetBin(*b)
                            if (
                                _subtract_hist.GetBinCenter(n_bin)
                                > self.sideband.signal[0]
                                and _subtract_hist.GetBinCenter(n_bin)
                                < self.sideband.signal[1]
                            ):
                                width = (
                                    _subtract_hist.GetBinWidth(n_bin)
                                    if "count" not in key
                                    else None
                                )
                                _subtract_hist.SetBinContent(
                                    n_bin, _sideband_count * self.sideband.scale(width)
                                )
                            else:
                                _subtract_hist.SetBinContent(n_bin, 0)

                        _counts[new_key].Add(_subtract_hist, -1)

        return _counts

    def _bin_to_ufloat(self, hist, n):
        return ufloat(hist.GetBinContent(n), hist.GetBinError(n))

    def _rebin_hist(self, hist):
        if hist.InheritsFrom(TH2.Class()):
            hist.Rebin2D(
                hist.GetXaxis().GetNbins(),
                hist.GetYaxis().GetNbins(),
            )
        else:
            hist.Rebin(hist.GetXaxis().GetNbins())

        return hist

    def _simple_eff(
        self, name, numerator_hist, denominator_hist, axis=None, integrated=False
    ):

        if integrated:
            numerator = ufloat(0, 0)
            denominator = ufloat(0, 0)
            for midpoint_coords in it.product(*self.midpoints):
                coords = [midpoint_coords[axis]] if axis else midpoint_coords
                n_bin = numerator_hist.FindBin(*coords)
                numerator += self._bin_to_ufloat(numerator_hist, n_bin)
                denominator += self._bin_to_ufloat(denominator_hist, n_bin)

            _err_square = (
                (
                    (denominator.n - numerator.n) ** 2 * numerator.s**2
                    + numerator.n**2 * np.abs(denominator.s**2 - numerator.s**2)
                )
                / denominator.n**4
                if denominator.n > 0
                else 0
            )  # Taken from Equation 14 of LHCb-INT-2013-038

            eff = numerator_hist.Clone(name)
            eff.Reset()
            eff = self._rebin_hist(eff)
            n_bin = eff.FindBin(*coords)

            eff.SetBinContent(
                n_bin, numerator.n / denominator.n if denominator.n > 0 else 0
            )
            eff.SetBinError(n_bin, np.sqrt(_err_square))

            if numerator.n == 0 or denominator.n == 0:
                self.logger.warning(
                    f"Efficiencies of 0 or nan (set to 0) computed for '{name}'"
                )

        else:
            eff = numerator_hist.Clone(name)
            eff.Divide(denominator_hist)
            has_zero = False
            for midpoint_coords in it.product(*self.midpoints):
                coords = [midpoint_coords[axis]] if axis else midpoint_coords
                n_bin = eff.FindBin(*coords)
                numerator = self._bin_to_ufloat(numerator_hist, n_bin)
                denominator = self._bin_to_ufloat(denominator_hist, n_bin)

                if numerator.n == 0 or denominator.s == 0:
                    has_zero = True

                _err_square = (
                    (
                        (denominator.n - numerator.n) ** 2 * numerator.s**2
                        + numerator.n**2 * np.abs(denominator.s**2 - numerator.s**2)
                    )
                    / denominator.n**4
                    if denominator.n > 0
                    else 0
                )  # Taken from Equation 14 of LHCb-INT-2013-038

                eff.SetBinError(n_bin, np.sqrt(_err_square))

            if has_zero:
                self.logger.warning(
                    f"Efficiencies of 0 or nan (set to 0) computed for '{name}'"
                )

        return eff

    def _full_eff(
        self,
        name,
        trig_hist,
        tistos_hist,
        tis_hist,
        tos_hist,
        tis_only_hist,
        tos_only_hist,
        axis=None,
        integrated=False,
    ):

        if integrated:
            numerator = ufloat(0, 0)
            _selected = 0
            _selected_err_square = 0
        else:
            eff = trig_hist.Clone(name)
            eff.Divide(tis_hist)
            eff.Multiply(tistos_hist)
            eff.Divide(tos_hist)
            has_zero = False

        for midpoint_coords in it.product(*self.midpoints):
            coords = [midpoint_coords[axis]] if axis else midpoint_coords
            n_bin = trig_hist.FindBin(*coords)

            trig = self._bin_to_ufloat(trig_hist, n_bin)
            tistos = self._bin_to_ufloat(tistos_hist, n_bin)  # d_i in Equation 11

            tis = self._bin_to_ufloat(tis_hist, n_bin)  # b_i + d_i in Equation 11
            tis_only = self._bin_to_ufloat(tis_only_hist, n_bin)  # b_i in Equation 11

            tos = self._bin_to_ufloat(tos_hist, n_bin)  # c_i + d_i in Equation 11
            tos_only = self._bin_to_ufloat(tos_only_hist, n_bin)  # c_i in Equation 11

            sel = (
                ufloat(
                    tis.n * tos.n / tistos.n,
                    np.sqrt(
                        (tos.n / tistos.n) ** 2 * tis_only.s**2
                        + (tis.n / tistos.n) ** 2 * tos_only.s**2
                        + (1 - tis_only.n * tos_only.n / tistos.n**2) * tistos.s**2
                    ),
                )
                if tistos.n > 0
                else ufloat(0, 0)
            )

            if integrated:
                numerator += trig
                _selected += sel.n
                _selected_err_square += sel.s**2

            else:
                if sel.n == 0 or trig.n == 0:
                    has_zero = True
                _err_square = (
                    (
                        (sel.n - trig.n) ** 2 * trig.s**2
                        + trig.n**2 * np.abs(sel.s**2 - trig.s**2)
                    )
                    / sel.n**4
                    if sel.n > 0
                    else 0
                )  # Taken from Equation 14 of LHCb-PUB-2014-039

                eff.SetBinError(n_bin, np.sqrt(_err_square))

        if integrated:
            _selected = ufloat(_selected, np.sqrt(_selected_err_square))
            _err_square = (
                (
                    (_selected.n - numerator.n) ** 2 * numerator.s**2
                    + numerator.n**2 * np.abs(_selected.s**2 - numerator.s**2)
                )
                / _selected.n**4
                if _selected.n > 0
                else 0
            )  # Taken from Equation 14 of LHCb-PUB-2014-039

            eff = trig_hist.Clone(name)
            eff.Reset()
            self._rebin_hist(eff)
            nbin = eff.FindBin(*coords)
            if numerator.n == 0 or _selected.n == 0:
                self.logger.warning(
                    f"Efficiencies of 0 or nan (set to 0) computed for '{name}'"
                )
            eff.SetBinContent(nbin, numerator.n / _selected.n if _selected.n > 0 else 0)
            eff.SetBinError(nbin, np.sqrt(_err_square))
        elif has_zero:
            self.logger.warning(
                f"Efficiencies of 0 or nan (set to 0) computed for '{name}'"
            )

        return eff
