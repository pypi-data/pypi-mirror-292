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

import numpy as np
import pytest
from ROOT import RDataFrame, RooWorkspace


@pytest.fixture
def example_file():

    tree = "Hlt2Test/DecayTree"
    path = "example_file.root"

    threshold = 0.05  # <- Proportion of sample which should be signal
    lower_limit = 5000
    upper_limit = 5600
    mean = 5280
    sigma1 = 16
    sigma2 = 24
    exponent = 800
    threshold /= (
        np.exp(-lower_limit / exponent) - np.exp(-upper_limit / exponent)
    ) * exponent

    rdf = RDataFrame(1_000_000)
    rdf = rdf.Define("isSignal", f"gRandom->Uniform(0, 1) < {threshold}")
    rdf = rdf.Define(
        "var1",
        f"isSignal ? (gRandom->Uniform(0, 1) < 0.5 ? gRandom->Gaus({mean}, {sigma1}) : gRandom->Gaus({mean}, {sigma2})) : gRandom->Exp({exponent}) + {lower_limit}",
    )
    rdf = rdf.Filter(f"var1 > {lower_limit} && var1 < {upper_limit}")

    rdf = rdf.Define(
        "var2", f"isSignal ? gRandom->Gaus(1.4, 0.4) : gRandom->Gaus(2, 0.6)"
    )

    rdf = rdf.Define("Hlt1DummyOneDecision", "1")
    rdf = rdf.Define(
        "P_Hlt1DummyOneDecision_TOS",
        f"gRandom->Uniform(0, 1) < (isSignal && Hlt1DummyOneDecision ? 0.85 : 0.1)",
    )
    rdf = rdf.Define(
        "P_Hlt1DummyOneDecision_TIS",
        f"gRandom->Uniform(0, 1) < (isSignal ? (P_Hlt1DummyOneDecision_TOS ? 0.12 : 0.12) : 0.1)",
    )

    rdf.Snapshot(tree, path)

    return tree, path


distributions = {
    "exponential": "Exponential",
    "doublecrystalball": "CrystalBall",
    "gauss": "Gaussian",
}


def build_component(ws, name, observable, component):
    distribution = distributions[component["model"]]
    expanded_vars = ", ".join(
        f"{name}_{variable}[{', '.join(str(value) for value in values)}]"
        for variable, values in component["variables"].items()
    )
    expanded_vars = f"{observable}, {expanded_vars}"

    ws.factory(f"{distribution}::{name}_pdf({expanded_vars})")

    return ws


def model():  # <- not decorated as pytest fixture due to PyROOT RooFit persistency issues
    description = {
        "signal": {
            "model": "gauss",
            "variables": {"mean": [5280, 5260, 5300], "width": [24, 8, 32]},
            "yield": [100_000, 0, 1_000_000],
        },
        "combinatorial": {
            "model": "exponential",
            "variables": {"exponent": [0, -0.01, 0.01]},
            "yield": [10_000, 0, 1_000_000],
        },
    }

    ws = RooWorkspace("test_ws")
    obs = ws.factory("var1[5000, 5600]")
    build_strings = []
    for name, component in description.items():
        build_component(ws, name, "var1", component)
        build_strings += [
            f"{name}_yield[{','.join(str(y) for y in component['yield'])}]*{name}_pdf",
        ]
    pdf = ws.factory(f"SUM::test_pdf({','.join(build_strings)})")
    return ws, obs, pdf
