Read routines for a molecular cloud model
*****************************************

Routines to read the output of a (time-dependent) molecular cloud (mc,0D chemistry) |prodimo| model. 
All the data belonging to a mc |prodimo| model is put into a hierachical data structure (:class:`~prodimopy.read_mc.Data_mc`).
Those kind of |prodimo| models are 0D chemistry models which provide the abundances for a given set of parameters (e.g. density,temperature etc.)

The module provides routines to read only the final abundances (last age or steady-state model) or the
abundances for all ages (as a function of time). Also the according ages and species names are read.

Usage example
-------------
Reads the time-dependent results of a molecular cloud |prodimo| model from the current working directory..

.. code-block:: python

   import prodimopy.read_mc as pread_mc
   
   model=pread_mc.read_mc("MC_Results.out")
   
   print(model)

Source documentation
--------------------
.. automodule:: prodimopy.read_mc

