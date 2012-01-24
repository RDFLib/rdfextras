.. _rdfextras.parsers.rdfjson: an rdfxtras plugin parser

===================================
JSONLD parser plugin for rdflib
===================================
|today|

JSONLD
------

Read a JSON-LD formatted document into RDF. See:

    http://json-ld.org/


Using the plug-in JSONLD parser with rdflib
---------------------------------------------

Usage with rdflib is straightforward: register the plugin, identify a source 
of JSON-LD, pass the source to the parser, manipulate the resulting graph.

.. code-block:: python

    >>> from rdflib import Graph, plugin, URIRef, Literal
    >>> from rdflib.parser import Parser
    >>> plugin.register('json-ld', Parser,
    ...     'rdfextras.parsers.jsonld', 'JsonLDParser')
    >>> test_json = '''
    ... {
    ...     "@context": {
    ...         "dc": "http://purl.org/dc/terms/",
    ...         "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    ...         "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
    ...     },
    ...     "@id": "http://example.org/about",
    ...     "dc:title": {
    ...         "@language": "en",
    ...         "@literal": "Someone's Homepage"
    ...     }
    ... }
    ... '''
    >>> g = Graph().parse(data=test_json, format='json-ld')
    >>> list(g) == [(URIRef('http://example.org/about'),
    ...     URIRef('http://purl.org/dc/terms/title'),
    ...     Literal(%(u)s"Someone's Homepage", lang=%(u)s'en'))]
    True


Modules
-------

.. currentmodule:: rdfextras.parsers.jsonld

.. automodule:: rdfextras.parsers.jsonld

.. autoclass:: JsonLDParser
   :members: parse
