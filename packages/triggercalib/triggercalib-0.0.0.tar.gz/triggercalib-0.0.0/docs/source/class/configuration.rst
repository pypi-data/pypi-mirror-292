Configuring a HltEff instance
=======================================================

At the moment, the easiest way to include the HltEff class in analysis scripts is to clone the repo (we recommend `adding as a git submodule <https://www.git-scm.com/docs/git-submodule>`_\), append the repo path (i.e., to ``...tistos-for_hlt/``\) with ``sys.path.append`` and then import as ``from HltEff import HltEff``. In the near future we'd like to deploy this through PyPI so that it would be ``pip install``\able!

When initialising an instance of the class, the following arguments **must** be given

.. code-block:

    h = HltEff(
        name, # Name of object
        path, # Path(s) to sample(s)
        tag: # Trigger line(s) to be used as the tag (TIS)
        probe: # Trigger line(s) to be used as the probe (TOS)
        particle: # Label of particle to be used as signal (used to find TIS/TOS information)
        binning: # Either a path to a file/dictionary for an existing binning, or a dictionary defining a new binning scheme
        variables: # Variables involved in binning scheme 
    )

Additionally, the following arguments *can* be given, e.g., to specify a mode for count calculation, PDF for fit-and-count, etc.:

.. code_block:

    cut, # Cut or list of cuts (must be `RDataFrame compatible <https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0>`_)
    observable, # RooAbsReal used for fit-and-count/sWeights
    pdf, # RooAbsPdf used for fit-and-count/sWeights
    sideband, # A sideband used for sideband subtraction
    sweights, # An existing set of sWeights in the sample(s) provided
    expert_mode, # Disables checks on fit convergence
    lazy, # Flag for initialisation without executing counts() and efficiencies() immediately (default behaviour)
    plots, # Flag for whether to produce plots for fit-and-count/sWeights
    prefix, # Prefix to place before object names
    output_path, # Path in which to produce outputs
    threads, # Number of threads to be used by RooFit for fit-and-count/sWeights

