.. _sec_plot:

Plotting routines for a single model
====================================

Collections of plotting routines for ProDiMo model output. All the routines use matplotlib.
Typically the output is a pdf file.

Usage example
-------------

.. code-block:: python

   # the prodimopy modules for reading and plotting
   import prodimopy.read as pread
   import prodimopy.plot as pplot
   # this is for the PDF output
   from matplotlib.backends.backend_pdf import PdfPages

   # Load the default prodimopy style
   pplot.load_style()


   # read the model from the current directory
   model=pread.read_prodimo()

   # Create an out.pdf where all the various plots are stored
   with PdfPages("out.pdf") as pdf:
      # create a prodimo Plot object for the various plotting routines
      pp=pplot.Plot(pdf)
      # vertical hydrogen number density
      pp.plot_NH(model,ylim=[1.e20,None])
      # a generic contour plot routine with many options
      pp.plot_cont(model, model.nHtot, r"$\mathsf{n_{<H>} [cm^{-3}]}$",
                   zlim=[1.e4,None],extend="both")

      # Here follows an example for a more complex contour plot, showing
      # some of the plenty options of this routine

      # Define some additional contours, with also showing labels
      # as the automatic positioning of labels does not work very well,
      # you likely have to tweak the label locations (see next line)
      tcont=pplot.Contour(model.td, [20,100,1000], linestyles=["-","--",":"],
                         showlabels=True,label_fontsize=10,label_fmt="%.0f")
      #tcont.label_locations=[(100,100),(55,5),(40,5)]

      # another contour, a simple one
      avcont=pplot.Contour(model.AV,[1.0],colors="black")

      # define the ticks shown in the colorbar
      cbticks=[10,30,100,300,1000]
      pp.plot_cont(model, model.td, r"$\mathrm{T_{dust}\,[K]}$",zr=True,xlog=True,
                   ylim=[0,0.5], zlim=[5,1500],extend="both",
                   oconts=[tcont,avcont],   # here the addtional contour added
                   contour=False,           # switch of the standard contours
                   clevels=cbticks,         # explictly set ticks for the cbar
                   clabels=map(str,cbticks),# and make some nice labels
                   cb_format="%.0f")


Source documentation
--------------------

.. autosummary:: 
      
   prodimopy.plot.Plot
   prodimopy.plot.Contour
   prodimopy.plot.load_style

.. automodule:: prodimopy.plot



