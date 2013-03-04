=======================================
Using SPARQL to query an rdflib 3 graph
=======================================

Get the SPARQL RDFLib plugin
============================

Using SPARQL with RDFLib requires installing the rdflib-sparql project. 

Install with PIP: 

..code-block:: sh

    pip install rdflib-sparql

or from <http://github.com/RDFLib/rdflib-sparql>


Create an RDFLib Graph
======================
You might parse some files into a new graph or open an on-disk
RDFLib store.

.. code-block:: python

    from rdflib.graph import Graph
    g = Graph()
    g.parse("http://www.w3.org/People/Berners-Lee/card.rdf")

Run a Query
===========

.. code-block:: python

    querystr = """
    SELECT ?aname ?bname 
    WHERE { 
        ?a foaf:knows ?b . 
        ?a foaf:name ?aname . 
        ?b foaf:name ?bname . 
    }"""
    for row in g.query(
        querystr, 
        initNs=dict(foaf=Namespace("http://xmlns.com/foaf/0.1/"))):
        
        print("%s knows %s" % row)

The results are tuples of values in the same order as your SELECT arguments.

.. code-block:: text

    Timothy Berners-Lee knows Edd Dumbill
    Timothy Berners-Lee knows Jennifer Golbeck
    Timothy Berners-Lee knows Nicholas Gibbins
    Timothy Berners-Lee knows Nigel Shadbolt
    Dan Brickley knows binzac
    Timothy Berners-Lee knows Eric Miller
    Drew Perttula knows David McClosky
    Timothy Berners-Lee knows Dan Connolly
    ...

Namespaces
==========
The :meth:`rdfextras.sparql.graph.Graph.parse` ``initNs`` argument is a dictionary of namespaces to be
expanded in the query string. In a large program, it's common to use
the same dict for every single query. You might even hack your graph
instance so that the ``initNs`` arg is already filled in.

If someone knows how to use the empty prefix (e.g. "?a :knows ?b"),
please write about it here and in the Graph.query docs.


Bindings
========
As with conventional SQL queries, it's common to run the same query many
times with only a few terms changing. rdflib calls this ``initBindings``:

.. code-block:: python

    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    ns = dict(foaf=FOAF)
    drew = URIRef('http://bigasterisk.com/foaf.rdf#drewp')
    for row in g.query('SELECT ?name WHERE { ?p foaf:name ?name }', 
                       initNs=ns, 
                       initBindings={'p' : drew}):
        print(row)


``Output``:

.. code-block:: python

    (rdflib.Literal('Drew Perttula', language=None, datatype=None),)

See also the the :meth:`rdflib.graph.Graph.query` `API docs <http://rdflib.net/rdflib-2.4.0/html/public/rdflib.Graph.Graph-class.html#query>`_

