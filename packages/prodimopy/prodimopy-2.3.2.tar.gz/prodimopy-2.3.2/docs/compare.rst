.. _sec_compare:

Compare two |prodimo| models
****************************

This module provides several routines to compare two |prodimo| models.

Currently only certain output fields are compared. In each comparison a certain tolerance 
is considered. Those values depend on which quantity is compared (e.g. temperatures, abundances). 

Currently it is possible to compare full (standard) |prodimo| models and molecular cloud (0D chemistry) 
models.

This module is mainly used for automatic tests. However, it is also useful during development to compare
two models with one simple command.

Source documentation
--------------------
# .. inheritance-diagram:: prodimopy.compare.Compare prodimopy.compare.CompareMc

.. automodule:: prodimopy.compare

