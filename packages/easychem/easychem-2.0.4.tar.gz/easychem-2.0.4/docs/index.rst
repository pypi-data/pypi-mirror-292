easyCHEM documentation
======================

Welcome to the **easyCHEM** documentation. easyCHEM is a Python package for calculating chemical abundances in exoplanet atmospheres, assuming atmospheric equilibrium chemistry. It is a clone of
the equilibrium chemistry part of `NASA's CEA <https://www1.grc.nasa.gov/research-and-engineering/ceaweb/>`_ code, written from scratch
and with numerical stability in mind. In particular, the code implements the
equations described in `Gordon & McBride (1994) <https://ntrs.nasa.gov/api/citations/19950013764/downloads/19950013764.pdf>`_.

**To get started with some examples on how to run easyCHEM, see our** `"easyCHEM tutorial" <content/notebooks/getting_started.html>`_. **Otherwise read on for some more general info.**

easyCHEM is available under the MIT License, and its base implementation is desribed in
`Mollière et al. (2017) <https://ui.adsabs.harvard.edu/abs/2017A&A...600A..10M>`_. It was benchmarked against the CEA code, leading to identical results. It was also compared to the equilibrium chemistry codes used for the ATMO and Exo-REM atmospheric models, again showing excellent agreement, see `Baudino et al. (2017) <https://ui.adsabs.harvard.edu/abs/2017ApJ...850..150B/abstract>`_.

.. _contact: molliere@mpia.de

This documentation webpage contains an `installation guide <content/installation.html>`_, a
`tutorial <content/notebooks/getting_started.html>`_, and an `API documentation <autoapi/index.html>`_.

Developers
___________

- Elise Lei and Paul Mollière

.. toctree::
   :maxdepth: 3
   :caption: Content:

   content/installation
   content/notebooks/getting_started

.. toctree::
   :maxdepth: 2
   :caption: Code documentation
