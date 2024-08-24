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

from ROOT import gROOT
from .utils import example_file

gROOT.SetBatch(True)


def test_sideband(example_file):
    from triggercalib import HltEff

    tree, path = example_file
    sideband = {
        "var1": {
            "range": [5100, 5460],
            "sideband": [5190, 5370],
            "signal": [5200, 5360],
        }
    }

    h = HltEff(
        "test_hlteff",
        tag="Hlt1DummyOne",
        probe="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        lazy=True,
        sideband=sideband,
    )
    h.set_binning(
        {"var2": {"label": "Variable 2", "bins": [3, 0, 3]}},
        compute_bins=True,
        cut="var1 > 5200 && var1 < 5360 && P_Hlt1DummyOneDecision_TIS && P_Hlt1DummyOneDecision_TOS",
    )
    h.counts()
    h.efficiencies()
    h.write("output_test_sideband.root")

    hist = h["efficiencies"]["tos_total_efficiency_var2"]
    n = hist.FindBin(1)
    val = hist.GetBinContent(n)
    err = hist.GetBinError(n)

    assert 0.85 > val - 3 * err and 0.85 < val + 3 * err
