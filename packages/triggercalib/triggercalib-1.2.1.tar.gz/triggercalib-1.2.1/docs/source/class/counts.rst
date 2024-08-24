Obtaining signal counts
=======================================================

As discussed in :doc:`index`, three approaches are taken to removing background from samples to calculate signal counts in each phase space bin.
Each approach is applicable across the TIS/TOS/TISTOS/Trig categories and *can* be applied across an arbitrary binning scheme (*should* is another question).


Sideband subtraction
-------------------------------------------------------

This approach relies on having a clean peaking signal distribution atop an (approximately) linear background.
Sidebands in this observable are defined as ranges outside of the signal peak in which it is anticipated that there is only background.
In these ranges, the background density is calculated as the ratio of number of events to (combined) sideband width, e.g. in a distribution :math:`M`,

.. math:

    \rho = \frac{N_\mathrm{lower} + N_\mathrm{upper}}{\delta M_\mathrm{lower} + \delta M_\mathrm{upper}},

where :math:`N_\mathrm{lower~(upper)}` and :math:`\delta M_\mathrm{lower~(upper)}` are the count and width of the lower (upper) sidebands, respectively.

Assuming that this is also the density of the background beneath the signal peak, the signal count, :math:`N_\mathrm{sig}`, can be defined as 

.. math:

    N_\mathrm{sig} = N_{\Delta M} - \rho \Delta M,

where :math:`\Delta M` is a window around the signal mass and :math:`N_\mathrm{\Delta M}` is the total number of events inside this window.

Since this approach does not involve any form of fitting, it is much faster than fit-and-count/*sWeight*\s; however, it cannot make use of the full statistics of the sample (only the events in the defined ranges) and is not typically applicable in channels where peaking backgrounds present beneath the signal (in addition to combinatorial). 


Fit-and-count over phase space
-------------------------------------------------------

The fit-and-count approach takes a user-defined PDF and performs a fit to a given variable, e.g., :math:`M`, repeated over each phase space bin and each category.
The PDF is assumed to be an extended sum of component PDFs, with each coefficient corresponding to the yield of each component.
This allows full analysis-level precision in determining the signal yield in each bin as such fit provide much better separation of signal and background than sideband subtraction.
However, this approach may run into problems with complicated (many parameter) fits or small samples as the division of the sample into phase space bins may not leave sufficient statistics for the fits to converge.
Ensuring that all fits converge for many bins may require a lot of fine tuning and is thus not advised.
Additionally, running many fits is inherently much more time consuming than performing sideband subtraction in the same binning.
Fitting is currently handled by the ``ROOT``-native ``RooFit`` library, though we foresee ``ZFit`` compatibility in the near future!


*sWeight*\ed phase space binning
-------------------------------------------------------
The *sWeight* approach provides a potential compromise between the speed of the sideband subtraction approach and precision of the fit-and-count approach.
The full calculation of *sWeight*\s is beyond the scope of the tool but further details can be found in the *sPlot* method paper and ``RooStats`` ``SPlot`` documentation (the implementation used here), Refs. [1]_ and [2]_, respectively.
In short, *sWeight*\s are calculated from a discriminating variable, e.g., the :math:`M` used above, to which a PDF is fit.
From this PDF, per-event weights are computed which can then be applied to *statistically independent* control variables, e.g., the kinematic variables of the phase space binning.

If the control and discriminating variables are indepenent (often a **big** if), then the counts in each category can be calculated by summing the *sWeight*\s in each phase space bin (rather than the number of events).
This independence (a.k.a factorisation) can be tested in a few different ways, though two very nice methods are introduced in Ref. [3]_.
Indeed these checks **will** be implemented in the tool in the near future!



.. [1] \M. Pivk and \F. \R. Le Diberder, *sPlot: a statistical tool to unfold data distributions* (`Nucl.Instrum.Meth.A555:356-369,2005 <https://doi.org/10.1016/j.nima.2005.08.106>`_), 2005

.. [2] *RooStats::SPlot Class Reference* (`https://root.cern/doc/master/classRooStats_1_1SPlot.html <https://root.cern/doc/master/classRooStats_1_1SPlot.html>`_), Accessed 2024

.. [3] \H. Dembinski, *Factorization test* (`https://hdembinski.github.io/posts/factorization_test.html <https://hdembinski.github.io/posts/factorization_test.html>`_), 2024