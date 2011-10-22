.. _rdfextras.serializers.rdfjson: an rdfxtras plugin serializer

=======================================
RDF/JSON serializer plug-in for rdflib
=======================================
|today|

Using the plug-in RDF/JSON-LD serializer with rdflib
-----------------------------------------------------

Usage with rdflib is straightforward: register the plugin, load in an rdflib 
Graph, serialize the graph.

.. warning:: Under construction

.. code-block:: python

    from rdflib import Graph, plugin
    from rdflib.parser import Parser

    plugin.register("rdfjson", Serializer,
       "rdfextras.serializers.rdfjson", "RdfJsonSerializer")
    
    data_source = \
        "https://raw.github.com/bradleypallen/json_ld_processor/" + \
            "master/test/json_ld_spec_section_6_1_example_2.json"

    g = Graph()
    g.parse(data_source, format="rdfjson")

    assert len(list(g.triples((None,None,None)))) == 2

    res = g.serialize(format="xml")
    
    assert 'rdf:about="&lt;http://example.org/people#jane&gt;"' in res
    assert 'rdf:about="&lt;http://example.org/people#john&gt;"' in res



DIY Section - Serialisation Algorithm
--------------------------------------
Lifted directly from the `Talis web site <http://docs.api.talis.com/platform-api/output-types/rdf-json>`_



Refer to http://json.org/ for definitions of terminology

Start a JSON object (called the root object)

Group all the triples by subject

For each subject:
^^^^^^^^^^^^^^^^^
Create a JSON object for the subject (called the subject object)

Group all triples having the current subject by predicate

For each predicate:
^^^^^^^^^^^^^^^^^^^
Create a JSON array (called the value array)

Select all triples having the current subject and current predicate

For each value:
^^^^^^^^^^^^^^^
Create a JSON object (called the value object)

Add a key/value pair to the value object with the key being the 
string "value" and the value being the lexical value of the triple value

Add a key/value pair to the value object with the key being the 
string "type" and the value being one of "literal", "uri" or 
"bnode" depending on the type of the triple's value

If the triple's value is a plain literal and has a language then 
add a key/value pair to the value object with the key being the 
string "lang" and the value being the language token

If the triple's value is a typed literal then add a key/value pair 
to the value object with the key being the string "datatype" and 
value being the URI of the datatype

Push the value object onto the end of the value array

Add a key/value pair to the subject object with the key being the 
predicate URI and the value being the value array

Add a key/value pair to the root object with the key being the URI or 
blank node identifier of the subject and the value being the subject 
object created in the previous step

Further Examples
-----------------
RDF/XML can be converted into the specified RDF/JSON format by using 
the `Talis conversion web service <http://convert.test.talis.com>`_.

Publishing RDF/JSON on the web
------------------------------
If doing content-negotiation, respond to, and send the content-type 
as ``application/json``. An empty graph (i.e. containing no triples) 
should be served as an empty object: ``{}``.


Modules
--------

.. currentmodule:: rdfextras.serializers.rdfjson

.. automodule:: rdfextras.serializers.rdfjson

.. autoclass:: RdfJsonSerializer
   :members: serialize


