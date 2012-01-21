.. _rdfextras.store.PostgreSQL: RDFExtras, stores, PostgreSQL.

|today|

===================================================
PostgreSQL formula-aware based on AbstractSQLStore
===================================================

PostgreSQL store formula-aware implementation. It stores its triples in the
following partitions (per AbstractSQLStore):

 * Asserted non rdf:type statements
 * Asserted rdf:type statements (in a table which models Class membership)
    The motivation for this partition is primarily query speed and 
    scalability as most graphs will always have more rdf:type statements 
    than others
 * All Quoted statements

In addition it persists namespace mappings in a separate table

Module contents
----------------

:mod:`~rdfextras.store.PostgreSQL`
----------------------------------------
.. automodule:: rdfextras.store.PostgreSQL
.. autoclass:: PostgreSQL
   :members:
.. autofunction:: ParseConfigurationString
.. autofunction:: GetConfigurationString
.. autofunction:: unionSELECT

