.. _rdfextras.store.BDBOptimized: RDFExtras, stores, BDBOptimized.

|today|

=======================================
BDBOptimized using YARS index structure
=======================================

An alternative BDB store implementing the index-structure proposed in:
http://sw.deri.org/2005/02/dexa/yars.pdf
     
Index structures
++++++++++++++++
key -> int, int -> key for variable to id and id -> variable

Triple indices: spoc, pocs, ocsp, cspo, cpso, ospc

This store is both transaction and context-aware.

The BDBOptimized store is experimental and not recommended for production.

Requires bsddb version >= 4.3.29.

Module contents
----------------

:mod:`~rdfextras.store.BDBOptimized`
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



