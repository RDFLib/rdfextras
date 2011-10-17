.. _rdfextras.store.ZODB: RDFExtras, stores, ZODB.

|today|

==================================================================
ZODB :: ZOPE Object Database persistence for RDFLib IOMemory Store
==================================================================

ZOPE Object Database implementation of :class:`rdflib.store.Store`.

The boilerplate ZODB/ZEO handling has been wrapped up in a utility class, 
:class:`rdfextras.store.ZODB.ZODBGraph`

Use straightforwardly as follows:

.. code-block:: python
	
	>>> import transaction
    >>> from rdflib import *
	>>> from rdfextras.store.ZODB import ZODBGraph
    >>> FOAF = Namespace("http://xmlns.com/foaf/0.1/")
	>>> g = ZODBGraph('file:///tmp/zodbtest.fs', create=True)
    >>> g.parse(format='n3', data='''
    ... @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    ... @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
    ... @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    ...
    ... @base <http://example.org/> .
    ...
    ... </person/some1#self> a foaf:Person;
    ...     rdfs:comment "Just a Python & RDF hacker."@en;
    ...     foaf:depiction </images/person/some1.jpg>;
    ...     foaf:homepage <http://example.net/>;
    ...     foaf:name "Some Body" .
    ...
    ... </images/person/some1.jpg> a foaf:Image;
    ...     rdfs:label "some 1"@en;
    ...     rdfs:comment "Just an image"@en;
    ...     foaf:thumbnail </images/person/some1-thumb.jpg> .
    ...
    ... </images/person/some1-thumb.jpg> a foaf:Image .
    ...
    ... ''')
	>>> transaction.begin()
	>>> g.store.commit()
	>>> transaction.commit()
	>>> g.serialize()
	...
	>>> g.close()
	>>> g = ZODBGraph(url, create=False)
	>>> g.serialize()
	...
	>>> g.close()


.. warning:: "Zope is especially memory hungry, because it uses ZODB object database." -- Mikko Ohtamaa

(`Posted`__ August 3, 2010)

.. __: http://blog.mfabrik.com/2010/08/03/running-32-bit-chroot-on-64-bit-ubuntu-server-to-reduce-python-memory-usage/

Module API
++++++++++

.. currentmodule:: rdfextras.store.ZODB

:mod:`rdfextras.store.ZODB`
----------------------------------------
.. automodule:: rdfextras.store.ZODB
.. autoclass:: ZODBGraph
   :members:

