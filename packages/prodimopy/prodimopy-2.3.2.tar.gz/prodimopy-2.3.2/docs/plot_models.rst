.. _sec_plot_models:

Plotting routines for a set of models
=====================================

Collections of plotting routines to produce comparison plots for a set of ProDiMo models.

Usage example
-------------

.. code-block:: python

	# the prodimopy modules for reading and plotting
	import prodimopy.read as pread
	import prodimopy.plot_models as ppms
	# this is for the PDF output
	from matplotlib.backends.backend_pdf import PdfPages

	# Load the prodimopy style
	import matplotlib.pyplot as plt
	plt.style.use("prodimopy")

	# the ProDiMo model directories, each directory is one model
	# adapt to your needs
	# for some plotting routines it is assumed that the last model
	# in that list is a reference model
	mdirs=["model1","model2","model3"]

	# make a list of models and read all of them
	models=list()
	for mdir in mdirs:
	  models.append(pread.read_prodimo(mdir))

	# one can also manipulate the name of a model, this name
	# will be shown in the legend of the plots
	models[-1].name="reference"

	# Create out_models.pdf where all the various plots are stored
	with PdfPages("out_models.pdf") as pdf:
	  # create the PlotModels object, here it is also possible to e.g.
	  # configure the colors used for line plots. For Details see the
	  # documentation
	  pms=ppms.PlotModels(pdf)

	  pms.plot_NH(models,xlog=True)

	  # if there was at least one SED calculated for the models, plot them including
	  # observational data for comparison (if available)
	  if not all(x.sed is None for x in models):
	    pms.plot_sed(models,ylim=[1.e-17,None],plot_starSpec=False,sedObs=models[0].sedObs)


	  # compare some column densities and average abundances
	  for spec in ["CO","H2O"]:
	    pms.plot_tcdspec(models, spec,xlog=True)
	    pms.plot_avgabun(models,spec,xlog=True)


	  # get all line estimates for CO in the wl range from 200 to 1500 mic
	  lines=models[0].selectLineEstimates("CO",wlrange=[200,1500])


	  # build an array of line idents which are considered for the plot
	  # here also only CO lines with an upper level smaller 20 are considered (i.e. the main transition)
	  # here jup is the internal level numbering of ProDiMo
	  idents=[[x.ident,x.wl] for x in lines if x.jup <20]
	  pms.plot_lines(models,idents,showBoxes=False)


Source documentation
--------------------
.. automodule:: prodimopy.plot_models


.. some usefull replacements for units
