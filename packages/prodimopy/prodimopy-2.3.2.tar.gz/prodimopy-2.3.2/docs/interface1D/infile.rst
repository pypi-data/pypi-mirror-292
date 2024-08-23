Creating input files for the 1D interface 
*****************************************

This module provides routines to generate the the input files for the 1D (radial) interface of ProDiMo. 


.. code-block:: python

    # Create some 1d inputfile for ProDiMo using the interface1D option
    # just a simply one made by hand with a gap.
    
    import prodimopy.interface1D.infile as in1D
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy.integrate as integ
    import astropy.constants as const
    
    # create a radial grid from 0.1 to 600 au
    rin=0.1
    rout=600.
    r=np.logspace(np.log10(rin),np.log10(rout),endpoint=True,num=80)
    
    # make a gas density profile
    # powerlaw surface density profile with index -1.0
    q=-1.0
    sdg=r[:]*0.0
    sdg = r**q
    # normalize the profile to a disk mass of 1.e-2 Msun
    rcm=r*in1D.autocm # use the au conversion factor from ProDiMo
    norm=1.e-2*const.M_sun.cgs.value/(np.pi*np.trapz(sdg*rcm,rcm))
    sdg[:]=sdg[:]*norm
    
    # make the gas to dust ratio profile
    g2d=sdg[:]*0.0+100 # assume g2d 100 everywhere
    
    # produce some gaps, shallow gas gap, deeper dust gap
    gap=(r>10) & (r<20)
    sdg[gap]=sdg[gap]*0.1
    g2d[gap]=g2d[gap]*100  # increase the gas to dust ratio, but keep gas
    
    #assume some smaller gaps outside of the gap
    amax=sdg[:]*0+3 # 3 cm maximum size
    amax[r>=20]=0.3 # smaller grains
    
    # Write the inputfile for ProDiMo, with a fixed g2dratio of 100 at all radii
    # factor +0.5 for top and bottom half of disk, ProDiMo uses only one half
    # this way the disk also has 1.e-2 in ProDiMo (a bit less because of the gap)
    in1D.write("sdprofile.in", rcm, sdg*0.5,g2d,amax=amax )
    
    
    # just make a plot 
    fig,ax=plt.subplots()
    ax.plot(r,sdg,label="gas")
    ax.plot(r,sdg/g2d,label="dust")
    
    ax.semilogx()
    ax.semilogy()
    ax.set_xlabel("r [au]")
    ax.set_ylabel("surface density [$\mathrm{g\,cm^{-2}}$]")
    ax.legend()


Source documentation
--------------------

.. automodule:: prodimopy.interface1D.infile

