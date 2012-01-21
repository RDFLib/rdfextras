.. _rdfextras.store.MySQL: RDFExtras, stores, MySQL.

|today|

=======================================================
MySQL :: an implementation of the FOPL Relational Model
=======================================================

MySQL implementation of FOPL Relational Model as an rdflib Store.

The MySQL store's relational schema incorporates hashes of terms for efficient
interning as well as other normalizations. Very little of it is written
specifically for MySQL and thus theoretically it can be very easily ported to
other back-ends (with the possible exception of issues with its use of foreign
keys)

Module API
++++++++++

.. currentmodule:: rdfextras.store.MySQL

:mod:`rdfextras.store.MySQL`
----------------------------------------
.. automodule:: rdfextras.store.MySQL
.. autoclass:: TimeStamp
   :members:
.. autoclass:: _variable_cluster
   :members:
.. autoclass:: SQL
   :members:
.. autoclass:: MySQL
   :members:
.. autoclass:: PostgreSQL
   :members:
.. autofunction:: createTerm
.. autofunction:: extractTriple

