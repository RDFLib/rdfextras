.. _rdfextras.parsers.rdfjson: an rdfxtras plugin parser

===================================
RDF/JSON parser plug-in for rdflib
===================================
|today|

RDF/JSON
--------

Lifted directly from the `Talis web site <http://docs.api.talis.com/platform-api/output-types/rdf-json>`_


This is a specification for a resource-centric serialisation of RDF in 
JSON. It aims to serialise RDF in a structure that is easy for developers 
to work with.

**Syntax Specification**

RDF/JSON represents a set of RDF triples as a series of nested data 
structures. Each unique subject in the set of triples is represented as 
a key in JSON object (also known as associative array, dictionary or hash 
table). The value of each key is a object whose keys are the URIs of the 
properties associated with each subject. The value of each property key 
is an array of objects representing the value of each property.

Blank node subjects are named using a string conforming to the nodeID 
production in Turtle. For example: ``_:A1``

In general, a triple (subject ``S``, predicate ``P``, object ``O``) is 
encoded in the following structure:

.. sourcecode:: text
    
    { "S" : { "P" : [ O ] } }

``O``, the object of the triple, is represented as a further JSON object 
with the following keys:

**type**

one of 'uri', 'literal' or 'bnode' (required and must be lowercase)

**value**

the lexical value of the object (required, full URIs should be used, 
not qnames)

**lang**

the language of a literal value (optional but if supplied it must 
not be empty)

**datatype**

the datatype URI of the literal value (optional)

The ``lang`` and ``datatype`` keys should only be used if the value of the 
``type`` key is "literal".

For example, the following triple:

.. sourcecode:: n3

    <http://example.org/about> 
        <http://purl.org/dc/elements/1.1/title> 
        "Anna's Homepage" .

can be encoded in RDF/JSON as:

.. sourcecode:: javascript

    {
      "http://example.org/about" : 
        {
           "http://purl.org/dc/elements/1.1/title": [ 
                { "type" : "literal" , "value" : "Anna's Homepage." } 
            ]
        }
    }

Example usage
-------------

.. code-block:: python

    >>> from rdflib import Graph, plugin
    >>> from rdflib.parser import Parser
    >>> from StringIO import StringIO
    >>> plugin.register("rdf-json", Parser, 
    ...     "rdfextras.parsers.rdfjson", "RdfJsonParser")
    >>> testrdfjson = '''
    ... {
    ...     "http://example.org/about" : {
    ...         "http://purl.org/dc/elements/1.1/creator" : [ { "value" : "Anna Wilder", "type" : "literal" } ],
    ...         "http://purl.org/dc/elements/1.1/title"   : [ { "value" : "Anna's Homepage", "type" : "literal", "lang" : "en" } ] ,
    ...         "http://xmlns.com/foaf/0.1/maker"         : [ { "value" : "_:person", "type" : "bnode" } ]
    ...     } ,
    ...  
    ...     "_:person" : {
    ...         "http://xmlns.com/foaf/0.1/homepage"      : [ { "value" : "http://example.org/about", "type" : "uri" } ] ,
    ...         "http://xmlns.com/foaf/0.1/made"          : [ { "value" : "http://example.org/about", "type" : "uri" } ] ,
    ...         "http://xmlns.com/foaf/0.1/name"          : [ { "value" : "Anna Wilder", "type" : "literal" } ] ,
    ...         "http://xmlns.com/foaf/0.1/firstName"     : [ { "value" : "Anna", "type" : "literal" } ] ,
    ...         "http://xmlns.com/foaf/0.1/surname"       : [ { "value" : "Wilder", "type" : "literal" } ] , 
    ...         "http://xmlns.com/foaf/0.1/depiction"     : [ { "value" : "http://example.org/pic.jpg", "type" : "uri" } ] ,
    ...         "http://xmlns.com/foaf/0.1/nick"          : [ 
    ...                                                       { "type" : "literal", "value" : "wildling"} , 
    ...                                                       { "type" : "literal", "value" : "wilda" } 
    ...                                                     ] ,
    ...         "http://xmlns.com/foaf/0.1/mbox_sha1sum"  : [ {  "value" : "69e31bbcf58d432950127593e292a55975bc66fd", "type" : "literal" } ] 
    ...     }
    ... }'''
    >>> g = Graph()
    >>> g.parse(StringIO(testrdfjson), format="rdf-json") # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> rdfxml = g.serialize(None, format="pretty-xml")
    >>> # assert '''<ns1:title>Anna's Homepage</ns1:title>''' in rdfxml
    >>> assert '''Anna's Homepage''' in rdfxml

Using the plug-in RDF/JSON parser with rdflib
---------------------------------------------

Usage with rdflib is straightforward: register the plugin, identify a source 
of RDF/JSON, pass the source to the parser, manipulate the resulting graph.

For the example, we will use a remote source, a test in the github repository for Bradley Pallen's JSON-LD processor. The JSON-LD code is as follows:

.. code-block:: python

    from rdflib import Graph, plugin
    from rdflib.parser import Parser
    plugin.register("rdf-json", Parser, 
       "rdfextras.parsers.rdfjson", "RdfJsonParser")

    g = Graph()
    testrdfjson = '''{
      "http://example.org/about" : 
        {
           "http://purl.org/dc/elements/1.1/title": [ 
                { "type" : "literal" , "value" : "Anna's Homepage." } 
            ]
        }
    }'''

    g.parse(data=testrdfjson, format="rdf-json") # doctest: +ELLIPSIS
    print(g.serialize(format="xml"))

    # <?xml version="1.0" encoding="utf-8"?>
    # <rdf:RDF
    #   xmlns:ns1="http://purl.org/dc/elements/1.1/"
    #   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    # >
    #   <rdf:Description rdf:about="http://example.org/about">
    #     <ns1:title>Anna's Homepage</ns1:title>
    #   </rdf:Description>
    # </rdf:RDF>


RDF/JSON as a JSON schema
--------------------------
More completely, RDF-JSON format is expressed as a JSON Scheme:

.. code-block:: javascript

    {
         "version":"0.3.0",
         "id":"RDF-JSON",
         "description":"RDF JSON definition",
         "type":"object",
         "properties":{
         },
         "additionalProperties":{
             "type":"object",
             "description":"subject (root object)",
             "optional":"true",
             "properties":{
             },
             "additionalProperties":{
                 "type":"array",
                 "description":"predicate (subject object)",
                 "optional":"true",
                 "items":{
                     "type":"object",
                     "description":"object (value array)",
                     "properties":{
                         "description":"content (value object)",
                         "type":{
                             "type":"string",
                             "enum":["uri","bnode","literal"]
                         },
                         "value":{
                             "type":"string"
                         },
                         "lang":{
                             "optional":true,
                             "description":"See ftp://ftp.isi.edu/in-notes/bcp/bcp47.txt",
                             "type":"string"
                         },
                         "datatype":{
                             "optional":true,
                             "format":"uri",
                             "type":"string"
                         }
                     }
                 }
             }
         }
    }


Modules
-------

.. currentmodule:: rdfextras.parsers.rdfjson

.. automodule:: rdfextras.parsers.rdfjson

.. autoclass:: RdfJsonParser
   :members: parse


