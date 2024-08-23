.. _sec_movie:

Movie Maker
===========

Collections of classes that allow to produce movies from a series of ProDiMo models.
Currently only contour plot movies are available.

This is still quite experimental and not very flexible. I guess there are several other
possibilities for movies. For example evolution of columndensities as function of time in a time
dependent model. Contributions are very welcome !

Usage example
-------------

.. code-block:: python

	import numpy as np
	import prodimopy.read as pread
	import prodimopy.movie as pmovie


	"""
	Example for a time-dependent ProDimo model.
	"""

	# the ages of the model. As the log10 of the ages is used age of 1 is avoided.
	# the unit is in yr
	# If you want to make a movie it is recommended to run the time-dependent ProDiMo 
	# model with small first time step (e.g. 1 yr) otherwise it might be the the 
	# movie routine has problems with the interpolation
	ages=np.array([1.000000000001,1e3,1e4,1e5,5e5,1e6,2e6,3.e6,5.e6])

	# read all the time output from the time-dependent ProDiMo model.
	# Assumes the model is in the current working directory of that script.
	models=list()
	for i in range(len(ages)):
	  models.append(pread.read_prodimo(".",td_fileIdx="{:02d}".format(i+1),readlineEstimates=False))

	# Make movie showing the time evolution of the CO abundance in mp4 format.
	pm=pmovie.ContourMovie(ages,models,[2.e-9,2.e-4],species="CO",nframes=100,plot_cont_dict={"zr": True})
	pm.make_movie("CO.mp4")

	# now write the same movie in html format (video tag)
	# this movie is shown below
	pm.make_movie("CO.html")

	# no make one for the gas temperature. Also evolves with time as the heating/cooling was solved
	# consistently with the time-dependent chemistry in this model.
	pm=pmovie.ContourMovie(ages,models,[5,5000],field="tg",nframes=100,cblabel=r"log T$_g$ [K]")
	pm.make_movie("tgas.mp4")


.. raw:: html
	:file: CO.html


Source documentation
--------------------
.. automodule:: prodimopy.movie
