Using and saving HltEff output
=======================================================

The ``ROOT`` histograms (``TH1``/ ``TH2``) containing the counts and efficiencies can be accessed directly 

.. code-block:
    hlt_eff = HltEff(...)
    counts = h["counts"]
    effs = h["efficiencies"]

These objects can also be written directly to a ``.root`` file with the ``.write(<path>)`` method of ``HltEff``.

If your analysis is more pythonic then these histograms can be easily converted with Uproot (Ref. [1]_), e.g., to Numpy (Ref. [2]_) or Boost (Ref. [3]_) histograms!

.. [1] \J. Pivarski et al., *Uproot: Version 5.3.1* (`10.5281/zenodo.10699405 <https://zenodo.org/records/10699405>`_), 2024

.. [2] \C. \R. Harris et al., *Array programming with NumPy* (`Nature 585, 357–362 <https://doi.org/10.1038/s41586-020-2649-2>`_), 2020

.. [3] \H. Schreiner et al., *scikit-hep/boost-histogram: Version 1.4.0*, (`10.5281/zenodo.8336454 <https://doi.org/10.5281/zenodo.8336454>`_), 2023