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

from ROOT import (
    RooMsgService,
    gROOT,
    RDataFrame,
    RooArgSet,
    RooDataSetHelper,
    RooFit,
    std,
)

from .utils import example_file, model

RooMsgService.instance().setGlobalKillBelow(RooFit.WARNING)
gROOT.SetBatch(True)


def test_fit_count_simple(example_file):
    from triggercalib import HltEff

    tree, path = example_file
    _, obs, pdf = model()

    h = HltEff(
        "test_hlteff",
        tag="Hlt1DummyOne",
        probe="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        lazy=True,
        observable=obs,
        pdf=pdf,
        output_path="results/fit_count_simple/",
        threads=8,
    )
    h.set_binning(
        {"var2": {"label": "Variable 2", "bins": [3, 0, 3]}},
        compute_bins=True,
        cut="var1 > 5200 && var1 < 5360 && P_Hlt1DummyOneDecision_TIS && P_Hlt1DummyOneDecision_TOS",
    )
    h.counts()
    h.efficiencies()
    h.write("output_test_fit_count_simple.root")

    hist = h["efficiencies"]["tos_total_efficiency_var2"]
    n = hist.FindBin(1)
    val = hist.GetBinContent(n)
    err = hist.GetBinError(n)

    assert 0.85 > val - 3 * err and 0.85 < val + 3 * err


def test_fit_count_with_prefit(example_file):
    from triggercalib import HltEff

    tree, path = example_file

    ws, obs, pdf = model()

    # Perform prefit #
    rdf = RDataFrame(*example_file)
    rdf = rdf.Filter("isSignal")
    data = rdf.Book(
        std.move(
            RooDataSetHelper(
                "data",
                "data",
                RooArgSet(
                    obs,
                ),
            )
        ),
        (obs.GetName(),),
    )

    pdf.pdfList()[0].fitTo(data.GetValue())

    ws.var("signal_mean").setConstant(True)
    ws.var("signal_width").setConstant(True)

    # Calculate counts and efficiencies #
    h = HltEff(
        "test_hlteff",
        tag="Hlt1DummyOne",
        probe="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        lazy=True,
        observable=obs,
        pdf=pdf,
        output_path="results/fit_count_with_prefit/",
        threads=8,
    )
    h.set_binning(
        {"var2": {"label": "Variable 2", "bins": [3, 0, 3]}},
        compute_bins=True,
        cut="var1 > 5200 && var1 < 5360 && P_Hlt1DummyOneDecision_TIS && P_Hlt1DummyOneDecision_TOS",
    )
    h.counts()
    h.efficiencies()
    h.write("output_test_fit_count_with_prefit.root")

    hist = h["efficiencies"]["tos_total_efficiency_var2"]
    n = hist.FindBin(1)
    val = hist.GetBinContent(n)
    err = hist.GetBinError(n)

    assert 0.85 > val - 3 * err and 0.85 < val + 3 * err
