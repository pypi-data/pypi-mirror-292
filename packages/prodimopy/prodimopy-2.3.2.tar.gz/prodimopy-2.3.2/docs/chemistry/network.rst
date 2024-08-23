Representation of a chemical network
************************************

This module provides routines to read, compare, manipulate chemical networks.
The new chemical networks can than also be written to files in various formats.

Usage example
-------------

This examples reads a network from a ProDiMo Reaction.in renames a species in it
and writes the network back to a new file in the same format.

.. code-block:: python

   import prodimopy.chemistry.network as pcnet

   # Create a new network and load the rates from the Reactions.in (local directory)
   reacin=pcnet.ReactionNetworkPin()
   reacin.load_reactions("Reactions.in")

   # now do the renaming
   reacin.renameSpecies("C2H6","CH3CH3")

   # write it again in a new file, be careful if you directly want to overwrite your old file.
   reacin.write_reactions("Reactions.in.renamed")


Source documentation
--------------------

.. automodule:: prodimopy.chemistry.network
