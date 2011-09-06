.. _rdfextras.store.AuditableStorage: RDFExtras, stores, AuditableStorage.

|today|

===============================================================
AuditableStorage, thread-safe logging of destructive operations
===============================================================

This wrapper intercepts calls through the store interface and implements 
thread-safe logging of destructive operations (adds / removes) in reverse.

This is persisted on the store instance and the reverse operations are 
executed in order to return the store to the state it was when the 
transaction began

Since the reverse operations are persisted on the store, the store itself acts
as a transaction. Calls to commit or rollback flush the list of reverse 
operations. This provides thread-safe atomicity and isolation (assuming 
concurrent operations occur with different store instances), but no durability
(transactions are persisted in memory and won't be available to reverse 
operations after the system fails): A and I out of ACID.


Modules
-------

:mod:`~rdfextras.store.AuditableStorage`
----------------------------------------
.. automodule:: rdfextras.store.AuditableStorage
.. autoclass:: AuditableStorage
   :members:

