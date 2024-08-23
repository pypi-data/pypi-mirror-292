Routines for running slab models
********************************

This module provides several routines to run 0D and 1D (radial) |prodimo| slab model. 
More robust and efficient implementation can be found in ProDiMo Fortran package, which also includes multiple species.
The QTpy directory provided in the python zip (available here: https://hitran.org/suppl/TIPS/TIPS2021/) should be separately downloaded and the path should be provided for running the slab routines. The HITRAN line data files (the .par files) should also be downloaded (https://hitran.org/lbl/). If you have ProDiMo FORTRAN package installed, these files are also available in the 'data/HITRAN2020/' directory.

Also check the example `notebook <https://gitlab.astro.rug.nl/prodimo/prodimopy/-/blob/master/notebooks/SlabExample.ipynb>`_.

Usage example
-------------

The following example runs 0D and 1D slab model.
The :func:`~prodimopy.run_slab.run_0D_slab` function runs 0D |prodimo| slab.
The :func:`~prodimopy.run_slab.run_1D_radial_slab` function runs 1D radial |prodimo| slab.


.. code-block:: python
   
   # the prodimopy modules for running
   import prodimopy.run_slab as runs
   
   runs.run_0D_slab(1e17,250,2.0,'CO2',44,'/path/to/prodimo/data/HITRAN2020/CO2.par',1e5,'/path/to/directory/containing/QTpy','CO2_0D.fits.gz',isotopolog=[1],wave_mol=[4,30],wave_spec=[4.9,28])
   runs.run_1D_radial_slab([1e17,1e16,1e15],[250,200,150],[0.1,0.2,1.0],190,2.0,'CO2',44,'/path/to/prodimo/data/HITRAN2020/CO2.par',1e5,'/path/to/directory/containing/QTpy','CO2_0D.fits.gz',width='infer',Rin_limit=0.07,Rout_limit=600,isotopolog=[1],wave_mol=[4,30],wave_spec=[4.9,28]):

Source documentation
--------------------

.. automodule:: prodimopy.run_slab

