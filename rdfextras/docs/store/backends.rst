.. _rdfextras.store_range: RDFExtras, store implementations.

|today|
.. currentmodule:: rdfextras.store

===========================================
Built-in RDFLib stores, Memory and IOMemory
===========================================

TODO: More detailed documentation (design rationale, pros and cons of the 
different implementations), benchmarks.

Contents:

.. toctree::
   :maxdepth: 2

Memory
========

Maintained in rdflib but described here for completeness.

:mod:`~rdfextras.store.Memory`
----------------------------------------
.. automodule:: rdfextras.store.Memory
.. autoclass:: Memory
   :members:



IOMemory
========

Maintained in rdflib but described here for completeness.
Both context-aware and formula-aware.

:mod:`~rdfextras.store.IOMemory`
----------------------------------------
.. automodule:: rdfextras.store.IOMemory
.. autoclass:: IOMemory
   :members:
.. automethod:: IOMemory.bind
.. automethod:: IOMemory.namespace
.. automethod:: IOMemory.namespaces
.. automethod:: IOMemory.prefix
.. automethod:: IOMemory.defaultContext
.. automethod:: IOMemory.uniqueSubjects
.. automethod:: IOMemory.uniquePredicates
.. automethod:: IOMemory.uniqueObjects


