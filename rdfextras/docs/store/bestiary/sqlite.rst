.. _rdfextras.store.SQLite: RDFExtras, stores, SQLite.

|today|

==========================================================
SQLite :: a formula-aware Store based on AbstractSQLStore
==========================================================


SQLite store formula-aware implementation.  It stores its triples in the 
following partitions:

* Asserted non rdf:type statements
* Asserted rdf:type statements (in a table which models Class membership). The motivation for this partition is primarily query speed and scalability as most graphs will always have more rdf:type statements than others
* All Quoted statements

In addition it persists namespace mappings in a separate table

Module API
++++++++++

.. currentmodule:: rdfextras.store.SQLite

:mod:`rdfextras.store.SQLite`
----------------------------------------
.. automodule:: rdfextras.store.SQLite
.. autoclass:: SQLite
   :members:
.. autofunction:: regexp


