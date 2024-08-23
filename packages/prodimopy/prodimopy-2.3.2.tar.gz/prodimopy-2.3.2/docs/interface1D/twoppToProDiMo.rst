two-pop-py to ProDiMo interface
*******************************

Interface from two-pop-py to ProDiMo. Provides to routines to run two-pop-py, prepare to output of two-pop-py for the use in ProDiMo and generates the 1D interace inputfile for ProDiMo.

To use this iterface an installation of two-pop-py is required. You can get two-pop-py here
`github two-pop-py <https://github.com/birnstiel/two-pop-py>`_.


Usage example
-------------

.. code-block:: python

  import twopoppy
  from twopoppy.const import M_sun, R_sun, year, AU
  import prodimopy.interface1D.twoppToProDiMo as twopp2P
  
  # input parameters for two-pop-py
  # they are all stored in the args object
  # For details see the two-pop-py documentation https://github.com/birnstiel/two-pop-py
  args = twopoppy.args()
  
  # output directory for the results written by two-pop-py
  args.dir = "tppdata"
  
  args.tmax = 2e6*year # maximum time for the two-pop-py simulation
  args.nt   = 5           # five time snapshots
  
  # dust grain parameters
  args.na   = 80    # number of size bins for the grain size grid (150 is recommended)
  args.a0   = 5e-07 # minimum grain size (monomer), [cm]
  args.rhos = 2.076 # the mass density of a grain [g/cm^3] should be consistent with the 
                    # chosen dust composition in ProDiMo
  
  # Stellar parameters. This is the ProDiMo standard T Tauri model
  # to be consistent the stellar parameters also need to be set in ProDiMo (in Parameter.in)
  # this is not yet done automatically 
  args.rstar = 2.0862*R_sun
  args.mstar = 0.7*M_sun
  args.tstar = 4000
  
  # Disk parameters 
  # These parameters also similar to the T Tauri standard model. However, two-pop-py uses a 
  # a different method to construct the disk and also consideres the evolution
  args.nr    = 80      # number of radial grid points for the disk
  args.mdisk = 0.01*M_sun
  args.d2g   = 0.01    # the initial dust to gas mass ratio
  args.r0    = 0.07*AU # inner disk radius
  args.rc    = 100*AU  # characteristic disk radius (tapering off radius)
  args.r1    = 1200*AU # outer radius, chose large one for two-pop-py, but will be set to where 
                       # NH_ver reaches approx 1.e20 like in ProDiMo (happens in twopp_to_ProDiMo)
  args.alpha = 1e-3    # viscosity alpha
  args.gamma = 0.75    # exponent for the viscosity
  
  
  # run two-pop-py
  res = twopoppy.model_wrapper(args,save=True,plot=False)
  
  # Do some post-processing and generate the input file for ProDiMo. 
  # Should be a proper ProDiMo model directory (e.g. with all other input files). 
  twopp2P.twopp_to_ProDiMo(res,"./sdprofile.in",timeidx=-1)
  
  # To use the sdprofile.in the "! fixed_surface_density " paramter needs to be set in Parameter.in 
  # here the last snapshot of the two-pop-py simulation is used for ProDiMo



Source documentation
--------------------

.. automodule:: prodimopy.interface1D.twoppToProDiMo

