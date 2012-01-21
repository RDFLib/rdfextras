.. _rdfextras.store.BerkeleyDB: RDFExtras, stores, BerkeleyDB.

|today|

====================================
BerkeleyDB, transaction-capable
====================================


A transaction-capable BerkeleyDB implementation.

The major difference are:
 * a ``dbTxn`` attribute which is the transaction object used for all bsddb 
    databases
 * All operations (put,delete,get) take the ``dbTxn`` instance
 * The actual directory used for the bsddb persistence is the name of 
    the identifier as a subdirectory of the 'path'


Module contents
---------------

:mod:`~rdfextras.store.BerkeleyDB`
----------------------------------------
.. automodule:: rdfextras.store.BerkeleyDB
.. autoclass:: BerkeleyDB
   :members:
.. autofunction:: transaction

