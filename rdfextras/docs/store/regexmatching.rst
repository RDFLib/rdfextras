.. _rdfextras.store.REGEXMatching: RDFExtras, stores, REGEXMatching.

|today|

=================================================
REGEXMatching, literal comparison via regex
=================================================

This wrapper is for use with stores that do not support literal comparison via 
regex. It intercepts calls through the store interface which make use of the 
:class:`REGEXTerm` class to represent matches by REGEX instead of literal
comparison and essentially provides support for literal comparison by 
replacing the REGEXTerms by wildcards (None) and matching against the results
from the store.

    **"Store-agnostic REGEX Matching and Thread-safe Transactional Support in rdflib"**  
    --- a blog post by Chimezie `18 Dec 2005 <http://copia.posterous.com/store-agnostic-regex-matching-and-thread-safe-0>`_
     
    rdflib now has (checked into svn trunk) support for REGEX matching of RDF
    terms and thread-safe transactional support. The transactional wrapper
    provides Atomicity, Isolation, but not Durability (a list of reversal RDF
    operations is stored on the live instance - so they won't survive a system
    failure). The store implementation is responsible for Consistency.

    The REGEX wrapper provides a REGEXTerm which can be used in any of the RDF
    term 'slots' with:

    * ``remove``
    * ``triples``
    * ``contexts``

    It replaces any REGEX term with a wildcard (None) and performs the REGEX match
    after the query invokation is dispatched to the store implementation it is
    wrapping.

    Both are meant to work with a live instance of an RDF Store, but behave as a
    proxy for the store (providing REGEX and/or transactional support).

    For example:

    .. sourcecode:: python

        from rdflib.Graph import ConjunctiveGraph, Graph
        from rdflib.store.REGEXMatching import REGEXTerm, REGEXMatching
        from rdflib.store.AuditableStorage import AuditableStorage
        from rdflib.store import Store
        from rdflib import plugin, URIRef, Literal, BNode, RDF

        store = plugin.get('IOMemory',Store)()
        regexStorage = REGEXMatching(store)
        txRegex =  AuditableStorage(regexStorage)
        g=Graph(txRegex,identifier=URIRef('http://del.icio.us/rss/chimezie'))
        g.load("http://del.icio.us/rss/chimezie")
        print len(g),[t for t in g.triples((REGEXTerm('.*zie$'),None,None))]
        g.rollback()
        print len(g),[t for t in g]

    Results in:

    .. sourcecode:: python

        492 [(u'http://del.icio.us/chimezie', 
              u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 
              u'http://purl.org/rss/1.0/channel'), 
             (u'http://del.icio.us/chimezie', 
              u'http://purl.org/rss/1.0/link', 
              u'http://del.icio.us/chimezie'), 
             (u'http://del.icio.us/chimezie', 
              u'http://purl.org/rss/1.0/items', 
              u'QQxcRclE1'), 
             (u'http://del.icio.us/chimezie', 
              u'http://purl.org/rss/1.0/description', u''), 
             (u'http://del.icio.us/chimezie', 
              u'http://purl.org/rss/1.0/title', 
              u'del.icio.us/chimezie')] 0 []


Module contents
---------------

.. currentmodule:: rdfextras.store.REGEXMatching

:mod:`~rdfextras.store.REGEXMatching`
----------------------------------------
.. automodule:: rdfextras.store.REGEXMatching
.. autoclass:: REGEXTerm
   :members:
.. autoclass:: REGEXMatching
   :members:
.. autofunction:: regexCompareQuad



