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

from lhcbstyle import LHCbStyle
import os
from ROOT import RooAbsPdf, RooAbsReal, RooDataSet, TCanvas
from typing import Annotated, List


class Plot:

    def __init__(
        self,
        name: str,
        var: RooAbsReal,
        data: RooDataSet,
        pdf: RooAbsPdf,
        extension: str = ".pdf",
    ):

        self.name = name
        self.var = var
        self.data = data
        self.pdf = pdf
        self.extension = extension

        with LHCbStyle():

            self.canvas = TCanvas(self.name)
            self.canvas.cd()

            self.frame = self.var.frame()
            self.data.plotOn(self.frame)
            if hasattr(self.pdf, "coefList") and callable(
                getattr(self.pdf, "coefList")
            ):
                colors = ["r", "g"]

                for pdf_i, color in zip(self.pdf.pdfList(), colors):
                    self.pdf.plotOn(
                        self.frame,
                        Components=[
                            pdf_i,
                        ],
                        LineStyle="--",
                        LineColor=color,
                    )
            self.pdf.plotOn(self.frame)
            # lbs.lhcbName.Draw("same")

            self.frame.Draw()

    def save(self, plot_path: str):
        path = os.path.join(plot_path, self.name)
        if not os.path.exists(plot_path):
            os.makedirs(plot_path)

        self.canvas.Print(f"{path}{self.extension}")

        return


class Sideband:

    def __init__(
        self,
        variable: str,
        variable_range: Annotated[List[float], 2],
        sideband_range: Annotated[List[float], 2],
        signal_range: Annotated[List[float], 2] = None,
    ):

        self.variable = variable
        self.range = variable_range
        self.sideband = sideband_range

        if signal_range:
            self.signal = signal_range
        else:
            self.signal = [
                self.sideband[0] - self.range[0],
                self.range[1] - self.sideband[1],
            ]

    def scale(self, width=None):
        if not (width):
            width = self.signal[1] - self.signal[0]
        return width / (
            (self.sideband[0] - self.range[0]) + (self.range[1] - self.sideband[1])
        )

    def range_cut(self):
        var = self.variable
        return f"({var} > {self.range[0]}) && ({var} < {self.range[1]})"

    def sideband_cut(self):
        var = self.variable
        lower_cut = f"({var} > {self.range[0]}) && ({var} < {self.sideband[0]})"
        upper_cut = f"({var} < {self.range[1]}) && ({var} > {self.sideband[1]})"
        return f"({lower_cut}) || ({upper_cut})"

    def signal_cut(self):
        var = self.variable
        return f"({var} > {self.signal[0]}) && ({var} < {self.signal[1]})"
