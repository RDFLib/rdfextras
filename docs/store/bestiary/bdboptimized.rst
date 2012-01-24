.. _rdfextras.store.BDBOptimized: RDFExtras, stores, BDBOptimized.

|today|

================================================================
BDBOptimized :: a BDB Store using YARS optimized index structure
================================================================

An alternative BDB store implementing the index-structure proposed in Harth and 
Decker's (2005) paper `Optimized Index Structures for Querying RDF from the Web <http://sw.deri.org/2005/02/dexa/yars.pdf>`_ and as used in `YARS <http://sw.deri.org/2004/06/yars/>`_
     
Index structures
++++++++++++++++

key -> int, int -> key for variable to id and id -> variable

Triple indices: spoc, pocs, ocsp, cspo, cpso, ospc

This store is both transaction and context-aware.

The BDBOptimized store is experimental and not recommended for production.

Requires bsddb version >= 4.3.29.

Module API
++++++++++


:mod:`rdfextras.store.BDBOptimized`
----------------------------------------
.. automodule:: rdfextras.store.BDBOptimized
.. autoclass:: NamespaceIndex
   :members:
.. autoclass:: IDMap
   :members:
.. autoclass:: QuadIndex
   :members:
.. autoclass:: BDBOptimized
   :members:



