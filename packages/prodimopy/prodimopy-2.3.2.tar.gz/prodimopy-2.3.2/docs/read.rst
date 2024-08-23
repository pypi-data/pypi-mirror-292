Read routines for a model
*************************

This module provides several routines to read the output of a |prodimo| model. 
All the data belonging to a |prodimo| model is put into an hierachical data structure (:class:`~prodimopy.read.Data_ProDiMo`).

The module provides a routine to read "all" the data of a |prodimo| model and spezialized routines  
to read only distinct model data (e.g. only the SED of a model).

Usage example
-------------

The following example reads the output files of a |prodimo| model from the current working directory.
The :func:`~prodimopy.read.read_prodimo` function tries to read (nearly)all |prodimo| output data which can found.
There are also more spezialed read routines (see :mod:`prodimopy.read`). 

.. code-block:: python

   import prodimopy.read as pread
   
   model=pread.read_prodimo()
   
   print(model)


Source documentation
--------------------

.. automodule:: prodimopy.read

