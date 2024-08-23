.. _sec_plot_casasim:

Plotting routines for CASA simulations
======================================

This module provides several routines to plot results from CASA simulations. 

This module is supposed to be used together with :mod:`~prodimopy.read_casasim`

Usage example
-------------

Reads in the Casa simulation with name L001ALMA_NN and plots the line cube and 
the integrated line emission. The output is in pdf (in the file `L001.pdf`)

.. code-block:: python

   import prodimopy.read_casasim as preadc
   import prodimopy.plot_casasim as pplotc
   from matplotlib.backends.backend_pdf import PdfPages

   data = preadc.CasaSim("L001ALMA_NN")

   with PdfPages("L001.pdf") as pdf:
     pc = pplotc.PlotCasasim(pdf)
     pc.plot_cube(data.cube,nrows=5,ncol=5)
     pc.plot_integrated(data.integrated)

Source documentation
--------------------
.. automodule:: prodimopy.plot_casasim


.. some usefull replacements for units

