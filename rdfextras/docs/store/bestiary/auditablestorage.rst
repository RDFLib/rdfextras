.. _rdfextras.store.AuditableStorage: RDFExtras, stores, AuditableStorage.

|today|

=================================================================
AuditableStorage :: thread-safe logging of destructive operations
=================================================================

Contributed by Chimezie Ogbuji.

The transactional wrapper provides Atomicity, Isolation, but not 
Durability (a list of reversal RDF operations is stored on the live 
instance - so they won't survive a system failure). The store 
implementation is responsible for Consistency.

This wrapper intercepts calls through the store interface and implements 
thread-safe logging of destructive operations (adds / removes) in reverse.

This is persisted on the store instance and the reverse operations are 
executed in order to return the store to the state it was when the 
transaction began

Since the reverse operations are persisted on the store, the store itself acts
as a transaction. Calls to ``commit`` or ``rollback`` flush the list of reverse 
operations. This provides thread-safe atomicity and isolation (assuming 
concurrent operations occur with different store instances), but no durability
(transactions are persisted in memory and won't be available to reverse 
operations after the system fails): in essence, this store provides the ``A`` 
and ``I`` out of ``ACID``.


Typical usage
=============

Typical usage is as a wrapper for RDFLib Stores - in the example below, 
AuditableStorage is used in conjunction with the REGEXMatching Store to
enhance the capabilities of the basic RDFLib IOMemory Store.

.. sourcecode:: python

    from rdflib import ConjunctiveGraph, Graph
    from rdfextras.store.REGEXMatching import REGEXTerm, REGEXMatching
    from rdfextras.store.AuditableStorage import AuditableStorage
    from rdflib.store import Store
    from rdflib import plugin, URIRef, Literal, BNode, RDF

    store = plugin.get('IOMemory',Store)()
    regexStorage = REGEXMatching(store)
    txRegex =  AuditableStorage(regexStorage)
    g=Graph(txRegex, identifier = URIRef('http://del.icio.us/rss/chimezie'))
    g.load("http://del.icio.us/rss/chimezie")
    print(len(g), [t for t in g.triples((REGEXTerm('.*zie$'),None,None))])
    g.rollback()
    print(len(g), [t for t in g])

Module API
++++++++++

.. currentmodule:: rdfextras.store.AuditableStorage

:mod:`rdfextras.store.AuditableStorage`
----------------------------------------

.. automodule:: rdfextras.store.AuditableStorage
.. autoclass:: AuditableStorage
   :members:

