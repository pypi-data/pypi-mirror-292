.. prodimopy documentation master file, created by
   sphinx-quickstart on Mon Aug 14 16:48:46 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

*********
prodimopy
*********

The python package provides routines for reading and plotting the output of one or more ProDiMo model(s).


Installation
============

The package can be installed from a gitlab repository or if you want a stable version from pypi via pip.
For details see https://gitlab.astro.rug.nl/prodimo/prodimopy. There you find also
the instructions how to update the code. You will also find a binder like that allows you to try some features of the package without installing anything.


Source Documentation
====================

.. toctree::
   :maxdepth: 2
   :caption: Modules:

   read
   read_mc
   read_slab
   read_casasim
   plot
   plot_models
   plot_mc
   plot_slab
   plot_casasim
   movie
   run_slab
   grid
   compare
   interface1D/interface1D
   chemistry/chemistry
   postprocessing

The style of the plots
======================
The plotting routines of prodimopy use matplotlib_ in the background. That means all matplotlib features are also available in prodimopy.

To define the style of the plots the mpatlotlib style sheets can be used. During the installation of prodimopy a prodimpy.mplstyle style sheet is installed and can be used in your own scripts (for an example see :ref:`sec_plot`).

You can also use your own styles and colors. But it might be that in some plotting routines of prodimopy the colors are hardcoded and therefore cannot be easily changed.


Command-line utilities
======================

prodimopy also installs a few command line utils which can be used without lauching a python interpreter or
writing any python code.

**pplot**

Produces plots for a single prodimo model.
Useful to check the prodimopy installation or to take a quick look on a |prodimo| model. For details see :ref:`sec_plot`.

**pplot_models**

Produces plots for a given set of prodimo models.
Useful to quickly compare visualy different |prodimo| models. For details see :ref:`sec_plot_models`.

**pcompare**

Compares the results of two |prodimo| models. For details see :ref:`sec_compare`.

**pparam**

Simple script to manipulte the Parameter.in file from the command line. Just call pparam from the command line and check the help.



Using Jupyter
=============

Most prodimopy routines can also be used within a Jupyter notebook.
In this :download:`example notebook <./jupyter_example.ipynb>` it is shown how to use
the reading a plotting routines for a single model.

This feature is not well tested yet. It worked with python 3.6 as part of the anaconda distribution using
the local Jupyter server.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

TODO's
======
This is a list of all the things that marked as todo in the code. Maybe you find
something you would like to fix!

.. todolist::


.. _matplotlib: https://matplotlib.org/
