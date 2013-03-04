
=============================================
Working with RDFLib and RDFExtras, the basics
=============================================

Working with Graphs
===================

The RDFLib :class:`~rdflib.graph.Graph` is one of the main workhorses for
working with RDF.

The most direct way to create a Graph is simply::

    >>> from rdflib import Graph
    >>> g = Graph()
    >>> g
    <Graph identifier=aGwNIAoQ0 (<class 'rdflib.graph.Graph'>)>

A BNode is automatically created as the graph's default identifier. A specific identifier can be supplied at creation time::

    >>> g = Graph(identifier="mygraph")
    >>> g
    <Graph identifier=mygraph (<class 'rdflib.graph.Graph'>)>

By default a Graph is persisted in an integer-key-optimized, context-aware,
in-memory :class:`~rdflib.store.Store`::

    >>> g.store
    <rdflib.plugins.memory.IOMemory object at 0x8c881ac>

A different store can be specified at creation time by using the identifying string
registered for the store, e.g. for a Sleepycat store::

    >>> g = Graph('Sleepycat', identifier="mygraph")
    >>> g.store
    <rdflib.plugins.sleepycat.Sleepycat object at 0x8c8836c>

Note that an identifier for the Graph object is required. The Sleepycat Store
affords the storage of multiple graphs so having an identifier is necessary for
any subsequent retrieval by identifier.

RDFLib Stores can be created separately and can subsequently be bound to
Graph.store::

    >>> from rdflib_sqlalchemy.SQLAlchemy import SQLAlchemy
    >>> store = SQLAlchemy(configuration="postgresql://localhost/test")
    >>> g = Graph(store, identifier="mygraph")
    >>> g.store
    <Partitioned SQL N3 Store: 0 contexts, 0 classification assertions, \
    0 quoted statements, 0 property/value assertions, and 0 other assertions>

See the RDFLib documentation for further details of the RDFLib `Graph API
<http://rdflib.readthedocs.org/en/latest/modules/graphs/graph.html>`_.

For a list of other available RDFLib plugin Stores see the `RDFLib Github
project page <http://github.com/RDFLib>`_.

Working with ConjunctiveGraphs
==============================

The ConjunctiveGraph is the 'top-level' Graph. It is the aggregation of all the
contexts (sub-graphs) within it and it is also the appropriate, absolute
boundary for closed world assumptions / models.

For the sake of persistence, Conjunctive Graphs must be distinguished by
identifiers. If an identifier is not supplied at creation time, then one will
be automatically assigned::

    >>> from rdflib import ConjunctiveGraph, URIRef
    >>> g = ConjunctiveGraph(store)
    >>> g
    <Graph identifier=JAxWBSXY0 (<class 'rdflib.graph.ConjunctiveGraph'>)>

Contexts are sub-graphs, they are identified by an identifier which may be
an RDFLib Literal or a URIRef::

    >>> c1 = URIRef("http://example.org/mygraph1")
    >>> c2 = URIRef("http://example.org/mygraph2")

Statements can be added to / retrieved from specific contexts::

    >>> bob = URIRef(u'urn:bob')
    >>> likes = URIRef(u'urn:likes')
    >>> pizza = URIRef(u'urn:pizza')
    >>> g.get_context(c1).add((bob, likes, pizza))
    >>> g.get_context(c2).add((bob, likes, pizza))

The ConjunctiveGraph is the aggregation of all the contexts within it::

    >>> list(g.contexts())
    [<Graph identifier=http://example.org/mygraph2 (<class 'rdflib.graph.Graph'>)>,
     <Graph identifier=http://example.org/mygraph1 (<class 'rdflib.graph.Graph'>)>]

The contexts / sub-graphs are instances of RDFLib Graph::

    >>> gc1 = g.get_context(c1)
    >>> gc1
    <Graph identifier=http://example.org/mygraph1 (<class 'rdflib.graph.Graph'>)>
    >>> len(gc1)
    1
    >>> gc2 = g.get_context(c2)
    >>> len(gc2)
    1
    >>> len(g)
    2

Changes to the contexts are also changes to the embracing aggregate
ConjunctiveGraph::

    >>> tom = URIRef(u'urn:tom')
    >>> gc1.add((tom, likes, pizza))
    >>> len(g)
    3

Working with namespaces
=======================

A small selection of frequently-used namespaces are directly importable::

    >>> from rdflib import OWL, RDFS
    >>> OWL
    Namespace(u'http://www.w3.org/2002/07/owl#')
    >>> RDFS
    rdf.namespace.ClosedNamespace('http://www.w3.org/2000/01/rdf-schema#')

Otherwise, namespaces are defined using the :class:`~rdflib.namespace.Namespace` class
which takes as its argument the base URI of the namespace::

    >>> from rdflib import Namespace
    >>> FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    >>> FOAF
    Namespace(u'http://xmlns.com/foaf/0.1/')

Namespace instances can be accessed attribute-style or dictionary key-style::

    >>> RDFS.label
    rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#label')
    >>> RDFS['label']
    rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#label')

Typical use::

    >>> g = Graph()
    >>> s = BNode('someone')
    >>> g.add((s, RDF.type, FOAF.Person))

Instances of Namespace class can be bound to Graphs::

    >>> g.bind("foaf", FOAF)

As a programming convenience, a namespace binding is automatically created when :class:`~rdflib.term.URIRef` predicates are added to the graph::

    >>> g = Graph()
    >>> g.add((URIRef("http://example0.com/foo"),
    ...        URIRef("http://example1.com/bar"),
    ...        URIRef("http://example2.com/baz")))
    >>> print(g.serialize(format="n3"))
    @prefix ns1: <http://example1.com/> .

    <http://example0.com/foo> ns1:bar <http://example2.com/baz> .


Working with statements
=======================

Working with statements as Python strings
-----------------------------------------

An example of hand-drawn statements in Notation3::

    n3data = """\
    @prefix : <http://www.snee.com/ns/demo#> .

    :Jane :hasParent :Gene .
    :Gene :hasParent :Pat ;
          :gender    :female .
    :Joan :hasParent :Pat ;
          :gender    :female .
    :Pat  :gender    :male .
    :Mike :hasParent :Joan ."""

These can be added to a Graph via the :meth:`~rdflib.graph.Graph.parse` method::

    >>> gc1.parse(data=n3data, format="n3")
    <Graph identifier=http://example.org/mygraph1 (<class 'rdflib.graph.Graph'>)>
    >>> len(gc1)
    7

Working with external bulk data
-------------------------------

Alternatively, an external source of bulk data can be used (unless specified
otherwise the format defaults to RDF/XML)::

    >>> data_url = "http://www.w3.org/2000/10/swap/test/gedcom/gedcom-facts.n3"
    >>> gc1.parse(data_url, format="n3")
    <Graph identifier=http://example.org/mygraph1 (<class 'rdflib.graph.Graph'>)>
    >>> len(gc1)
    74
    >>> print(gc1.serialize(format="n3"))
    @prefix default5: <http://www.w3.org/2000/10/swap/test/gedcom/gedcom-relations.n3#> .
    @prefix gc: <http://www.daml.org/2001/01/gedcom/gedcom#> .

    default5:Ann gc:childIn default5:gd;
        default5:gender default5:F .

    default5:Ann_Sophie gc:childIn default5:dv;
        default5:gender default5:F .

    default5:Bart gc:childIn default5:gd;
        default5:gender default5:M .

    ...

Working with web pages containing RDFa
--------------------------------------

RDFLib provides a built-in version of Ivan Herman's `RDFa Distiller <http://www.w3.org/2007/08/pyRdfa/>`_ so
"external bulk data" also means "web pages containing `RDFa <http://www.w3.org/TR/rdfa-syntax>`_ markup"::

    >>> url = "http://www.oettl.it/"
    >>> gc1.parse(location=url, format="rdfa", lax=True)
    <Graph identifier=http://example.org/mygraph1 (<class 'rdflib.graph.Graph'>)>
    >>> len(gc1)
    68
    >>> print(gc1.serialize(format="n3"))
    @prefix commerce: <http://search.yahoo.com/searchmonkey/commerce/> .
    @prefix eco: <http://www.ebusiness-unibw.org/ontologies/eclass/5.1.4/#> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    @prefix gr: <http://purl.org/goodrelations/v1#> .
    @prefix media: <http://search.yahoo.com/searchmonkey/media/> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
    @prefix xhv: <http://www.w3.org/1999/xhtml/vocab#> .

    <http://www.oettl.it/#BusinessEntity> a gr:BusinessEntity,
            commerce:Business,
            vcard:VCard;
        gr:hasPOS <http://www.oettl.it/#LOSOSP_1>;
        gr:offers <http://www.oettl.it/#Offering_1>;
        commerce:hoursOfOperation "Mon-Fri 8.00-12.00 and 13.00-18.00, Sat 8.00-12.00 [Yahoo commerce]"@NULL;
        media:image <http://www.oettl.it/img/karl_foto.jpg>;
        rdfs:isDefinedBy <http://www.oettl.it/>;
        rdfs:seeAlso <http://www.oettl.it/>;
        vcard:adr <http://www.oettl.it/#address>;
        vcard:url <http://www.oettl.it/>;
        foaf:depiction <http://www.oettl.it/img/karl_foto.jpg> .

    ...


The GoodRelations wiki lists some other `sources of RDFa-enabled web pages <http://www.ebusiness-unibw.org/wiki/GoodRelations>`_

The RDFLib Graph API presents full details of args and kwargs for `Graph.parse <http://rdflib.readthedocs.org/en/latest/modules/graphs/graph.html#rdflib.graph.Graph.parse>`_.

Also see the `working with Graphs <http://rdflib.readthedocs.org/en/latest/modules/graphs/index.html#module-rdflib.graph>` section of the RDFLib documentation.

Working with individual statements
----------------------------------

Individual statements can be added, removed, etc.

    >>> gc1.remove((tom, likes, pizza))

    >>> from rdflib import RDFS, Literal
    >>> gc1.bind("rdfs", RDFS.uri)
    >>> graham = URIRef(u'urn:graham')
    >>> gc1.add((graham, likes, pizza))
    >>> gc1.add((graham, RDFS.label, Literal("Graham")))
    >>> print(gc1.serialize(format="n3"))
    @prefix ns4: <urn:> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    <BLANKLINE>
    ns4:graham rdfs:label "Graham";
        ns4:likes ns4:pizza .


As before, see the RDFLib documentation for further details of the RDFLib `Graph API
<http://rdflib.readthedocs.org/en/latest/modules/graphs/graph.html>`_ for a range of useful operations on Graphs, e.g.

    >>> [o for o in gc1.objects(subject=graham, predicate=likes)]
    [rdflib.term.URIRef(u'urn:pizza')]

    >>> [o for o in gc1.predicate_objects(subject=graham)] # output prettified by hand here
    [(rdflib.term.URIRef(u'urn:likes'), rdflib.term.URIRef(u'urn:pizza')),
     (rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#label'),
      rdflib.term.Literal(u'Graham'))]

    >>> gc1.value(subject=graham, predicate=likes)
    rdflib.term.URIRef(u'urn:pizza')

Working with nodes
==================

:class:`~rdflib.Literal` and :class:`~rdflib.URIRef` are the two most
commonly-used nodes in an RDF graph.

Working with URIRefs is quite straightforward::

    >>> uri = URIRef("http://example.com")
    >>> uri
    rdflib.term.URIRef(u'http://example.com')
    >>> str(uri)
    'http://example.com'


The options for working with Literals are amply illustrated in the
`Literal node docs <http://rdflib.readthedocs.org/en/latest/modules/node.html#rdflib.term.Literal>`_. Also see the appropriate section in the `RDF specs <http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal>`_::

    >>> graham = Literal(u'Graham', lang="en")
    >>> graham
    rdflib.term.Literal(u'Graham', lang='en')
    >>> from rdflib.namespace import XSD
    >>> graham = Literal(u'Graham', datatype=XSD.string)
    >>> graham
    rdflib.term.Literal(u'Graham', datatype=rdflib.term.URIRef(u'http://www.w3.org/2001/XMLSchema#string'))

Literals are permitted to have only one of the attributes datatype or lang.::

    >>> graham = Literal(u'Graham', datatype=XSD.string, lang="en")
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File ".../rdflib/term.py", line 337, in __new__
        raise TypeError("A Literal can only have one of lang or datatype, "
    TypeError: A Literal can only have one of lang or datatype,
        per http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal


Working with SPARQL
===================

Assuming the rdflib-sparql package has been installed, SPARQL queries can be used out of the box with RDFLib 3.X.

"SPARQL can be used out of the box" translates as: RDFLib Graph gets a 'query' method that accepts a SPARQL query string::

    >>> results = gc1.query("""SELECT ?s ?p ?o WHERE {?s ?p ?o .}""")

The 'query' method API offers keywords to set namespace bindings - ``initNs`` (RDF, RDFS and OWL namespaces are pre-installed as a convenience to programmers but see example below for usage), variable bindings - ``initBindings`` (also see example below) and a boolean debug flag - ``DEBUG`` (ditto)::

    >>> FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    >>> ns = dict(foaf=FOAF)
    >>> drew = URIRef('http://bigasterisk.com/foaf.rdf#drewp')
    >>> for row in g.query(
    ...         """SELECT ?name WHERE { ?p foaf:name ?name }""",
    ...         initNs=ns,
    ...         initBindings={'p' : drew},
    ...         DEBUG=True):
    ...     print(row)

.. note:: When graph.store is an instance of :class:`~rdfextras.store.SPARQL.SPARQLStore` or :class:`~rdfextras.store.SPARQL.SPARQLUpdateStore`, the API is reduced to just the query string arg, i.e. the 'initNs', 'initBindings' and 'DEBUG' keywords are not recognized.

Using the following set of statements::

    >>> n3data = """\
    @prefix : <http://www.snee.com/ns/demo#> .

    :Jane :hasParent :Gene .
    :Gene :hasParent :Pat ;
          :gender    :female .
    :Joan :hasParent :Pat ;
          :gender    :female .
    :Pat  :gender    :male .
    :Mike :hasParent :Joan ."""

And the following SPARQL CONSTRUCT query::

    >>> cq = """\
    CONSTRUCT { ?p :hasGrandfather ?g . }

    WHERE {?p      :hasParent ?parent .
           ?parent :hasParent ?g .
           ?g      :gender    :male .
    }"""


Executing the query returns a SPARQLQueryResult, the serialization of which can
be passed directly to Graph.parse::

    >>> gc1.parse(data=n3data, format="n3")
    >>> nsdict = {'':"http://www.snee.com/ns/demo#"}
    >>> result_graph = gc1.query(cq, initNs=nsdict)
    >>> newg = Graph().parse(data=result_graph.serialize(format='xml'))
    >>> print(newg.serialize(format="n3"))
    @prefix ns3: <http://www.snee.com/ns/demo#> .

    ns3:Jane ns3:hasGrandfather ns3:Pat .

    ns3:Mike ns3:hasGrandfather ns3:Pat .


The RDFExtras test suite contains many `examples <https://github.com/RDFLib/rdfextras/blob/master/test/test_sparql/test_sparql_date_filter.py>`_ of SPARQL queries and a `companion document <sparql/detailed_description.html>`_ provides further
details of working with basic SPARQL in RDFLib.

Working with SPARQL query results
=================================

Query results can be iterated over in a straightforward fashion. Row bindings are
positional::

    >>> gc1.parse("http://bel-epa.com/gjh/foaf.rdf", format="xml")
    <Graph identifier=http://example.org/mygraph1 (<class 'rdflib.graph.Graph'>)>
    >>> query = """\
    ... SELECT ?aname ?bname
    ... WHERE {
    ...     ?a foaf:knows ?b .
    ...     ?a foaf:name ?aname .
    ...     ?b foaf:name ?bname .
    ... }"""
    >>> nses = dict(foaf=Namespace("http://xmlns.com/foaf/0.1/"))
    >>> for row in gc1.query(query, initNs=nses):
    ...     print(repr(row))
    ...
    (rdflib.term.Literal(u'Graham Higgins'), rdflib.term.Literal(u'Ngaio Macfarlane'))

A more detailed view of the returned SPARQLResult::

    >>> gc1.parse("http://bel-epa.com/gjh/foaf.rdf", format="xml")
    <Graph identifier=http://example.org/mygraph1 (<class 'rdflib.graph.Graph'>)>
    >>> query = """\
    ... SELECT ?aname ?bname
    ... WHERE {
    ...     ?a :knows ?b .
    ...     ?a :name ?aname .
    ...     ?b :name ?bname .
    ... }"""
    >>>
    >>> foaf = Namespace("http://xmlns.com/foaf/0.1/")
    >>> rows = gc1.query(query, initNs={'':foaf})
    >>> for i in ['askAnswer', 'bindings', 'graph',
    ...           'selectionF', 'type', 'vars']:
    ...     v = getattr(rows, i)
    ...     print(i, type(v), v, repr(v))
    ...
    ('askAnswer', <type 'NoneType'>, None, 'None')
    ('bindings', <type 'list'>, [
        {?bname: rdflib.term.Literal(u'Ngaio Macfarlane'),
         ?aname: rdflib.term.Literal(u'Graham Higgins')]")
    ('graph', <type 'NoneType'>, None, 'None')
    ('selectionF', <type 'list'>, [?aname, ?bname], '[?aname, ?bname]')
    ('type', <type 'str'>, 'SELECT', "'SELECT'")
    ('vars', <type 'list'>, [?aname, ?bname], '[?aname, ?bname]')

    >>> x = rows.vars[0]
    >>> print(type(x), repr(x), str(x), x)
    (<class 'rdflib.term.Variable'>, '?aname', 'aname', ?aname)
    >>> for row in rows.bindings[4:5]:
    ...     print("Row", type(row), row)
    ...     for col in row:
    ...         print("Col", type(col), repr(col), str(col), col, row[col])
    ...
    ('Row', <type 'dict'>, {?bname: rdflib.term.Literal(u'Ngaio Macfarlane'),
                            ?aname: rdflib.term.Literal(u'Graham Higgins')})
    ('Col', <class 'rdflib.term.Variable'>, '?bname', 'bname', ?bname,
     rdflib.term.Literal(u'Ngaio Macfarlane'))
    ('Col', <class 'rdflib.term.Variable'>, '?aname', 'aname', ?aname,
     rdflib.term.Literal(u'Graham Higgins'))

Note the unusual \__repr__() result for the SPARQL variables, i.e. ``?aname``.
The actual value is ``aname``, the question mark is added for the \__repr__()
result. Iterating over the bindings behaves as expected::

    >>> for row in rows.bindings:
    ...     for col in row:
    ...         print(col, row[col])
    ...

and so does iteration driven by the vars::

    >>> for row in rows.bindings:
    ...     for col in rows.vars:
    ...         print(col, row[col])
    ...

But when using the keys directly, discard the '?' prefix:
    >>> for row in rows.bindings:
    ...     knowee = row['bname']

SPARQL query result objects can be serialized as XML or JSON::

    >>> print("json", rows.serialize(format="json"))
    ('json',
     '{"head": {"vars": ["aname", "bname"]},
       "results": {
            "bindings": [{
                "bname": {"type": "literal", "value": "Ngaio Macfarlane"},
                "aname": {"type": "literal", "value": "Graham Higgins"}}}]}}')

