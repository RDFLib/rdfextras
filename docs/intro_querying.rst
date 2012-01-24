=======================================
Using SPARQL to query an rdflib 3 graph
=======================================

Get the Plugin
==============

SPARQL is no longer shipped with Core rdflib - instead it is now a part of
`rdfextras <http://code.google.com/p/rdfextras/>`_ a Google code project 
(http://code.google.com/p/rdfextras/):

Assuming you have rdfextras installed, you can use Sparql with rdflib 3.0 by
adding these lines somewhere at the top of your program:

.. sourcecode:: python

    import rdflib

    rdflib.plugin.register('sparql', rdflib.query.Processor,
                           'rdfextras.sparql.processor', 'Processor')
    rdflib.plugin.register('sparql', rdflib.query.Result,
                           'rdfextras.sparql.query', 'SPARQLQueryResult')

Create an rdflib Graph
======================
You might parse some files into a new graph (see above) or open an on-disk rdflib store.

.. sourcecode:: python

    from rdflib.graph import Graph
    g = Graph()
    g.parse("http://bigasterisk.com/foaf.rdf")
    g.parse("http://www.w3.org/People/Berners-Lee/card.rdf")

LiveJournal produces `FOAF data <http://captsolo.net/info/blog_a.php/2007/10/04/foaf_for_social_network_migration>`_
for their users, but they seem to use ``foaf:member_name`` for a person's full
name. For this demo, I made ``foaf:name`` act as a synonym for 
``foaf:member_name`` (a poor man's one-way 
`owl:equivalentProperty <http://www.w3.org/TR/owl-ref/#equivalentProperty-def>`_):

.. sourcecode:: python

    from rdflib import Namespace
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    g.parse("http://danbri.livejournal.com/data/foaf") 
    [g.add((s, FOAF['name'], n)) for s,_,n in g.triples((None, FOAF['member_name'], None))]

Run a Query
===========

.. sourcecode:: python

    for row in g.query('SELECT ?aname ?bname WHERE { ?a foaf:knows ?b . ?a foaf:name ?aname . ?b foaf:name ?bname . }', 
                       initNs=dict(foaf=Namespace("http://xmlns.com/foaf/0.1/"))):
        print("%s knows %s" % row)

The results are tuples of values in the same order as your SELECT arguments.

.. sourcecode:: text

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

.. sourcecode:: python

    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    ns = dict(foaf=FOAF)
    drew = URIRef('http://bigasterisk.com/foaf.rdf#drewp')
    for row in g.query('SELECT ?name WHERE { ?p foaf:name ?name }', 
                       initNs=ns, 
                       initBindings={'p' : drew}):
        print(row)


``Output``:

.. sourcecode:: python

    (rdflib.Literal('Drew Perttula', language=None, datatype=None),)

See also the the :meth:`rdflib.graph.Graph.query` `API docs <http://rdflib.net/rdflib-2.4.0/html/public/rdflib.Graph.Graph-class.html#query>`_

