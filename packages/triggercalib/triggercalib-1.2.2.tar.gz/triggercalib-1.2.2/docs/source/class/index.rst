HltEff core class
=======================================================

The ``HltEff`` class forms the core of the TISTOS for HLT tools.
This Python class provides a basic interface for you to input your samples, trigger lines of interest, variables, binning schemes and more details required to calculate trigger efficiencies.
The class breaks the calculation process up into two methods:

#. ``counts()`` (see :doc:`counts`): The counts in each category (TIS, TOS, TISTOS and Trig) are computed in each variable/bin provided.
   Background present in these samples is removed in one of three ways:

   #. Sideband subtraction: The density of background is computed in the sidebands (i.e., user-defined regions either side of a signal peak in a given distribution) and used to estimate (and subtract) the amount of background beneath the signal.
      It is **strongly** recommended that you use sideband subtraction as it is currently the fastest and most stable approach.
   #. Fit-and-count: A user-defined PDF is fit to the sample in each bin for each category. 
      The PDF is assumed to be a sum of component PDFs, with the first coefficient interpreted as the signal yield (count in the bin).
   #. *sWeight*\s (experimental): A user-defined PDF is fit to the sample for each category and used to calculate *sWeight*\s (see Ref. [1]_).
      The signal (also assumed as first component) *sWeight* are then applied as weights when histogramming the sample in each category, i.e., the counts are taken as the sum of *sWeight*\s in each bin rather than the number of events.
      This method, whilst significantly faster than fit-and-count, requires an additional level of statistical rigour to be as accurate as either other method.
      For checks to understand whether you can use the *sWeight* approach please see :doc:`checks`.

#. ``efficiencies()`` (as discussed in :doc:`../background/tistos`\): The counts from the previous stage are propagated into TIS, TOS and Trig efficiencies.

.. [1] \M. Pivk and \F. \R. Le Diberder, *sPlot: a statistical tool to unfold data distributions* (`Nucl.Instrum.Meth.A555:356-369,2005 <https://doi.org/10.1016/j.nima.2005.08.106>`_), 2005

.. toctree::
   :maxdepth: 2
   :hidden:

   configuration
   counts
   writing
   checks