==============================================
Parsing RDF into rdflib graphs
==============================================

Reading an NT file
==================

RDF data has various syntaxes ([ xml], [ n3], [ ntriples], trix, etc) that you
might want to read. The simplest format is ``ntriples``. Create the file
``demo.nt`` in the current directory with these two lines:

.. sourcecode:: n3

    <http://bigasterisk.com/foaf.rdf#drewp> \
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> 
        <http://xmlns.com/foaf/0.1/Person> .
    <http://bigasterisk.com/foaf.rdf#drewp> \ 
        <http://example.com/says> "Hello world" .

In an interactive python interpreter, try this:

.. sourcecode:: pycon

    >>> from rdflib.graph import Graph

    >>> g = Graph()

    >>> g.parse("demo.nt", format="nt") # DOCTEST ELLIPSIS
    <Graph identifier=... (<class 'rdflib.Graph.Graph'>)>

    >>> len(g)
    2

    >>> for stmt in g:
    ...     print stmt
    ... 
    (rdflib.URIRef('http://bigasterisk.com/foaf.rdf#drewp'), 
     rdflib.URIRef('http://example.com/says'), 
     rdflib.Literal('Hello world', language=None, datatype=None))
    (rdflib.URIRef('http://bigasterisk.com/foaf.rdf#drewp'), 
     rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), 
     rdflib.URIRef('http://xmlns.com/foaf/0.1/Person'))


The final lines show how RDFLib represents the two statements in
the file. The statements themselves are just length-3 tuples; and the
subjects, predicates, and objects are all rdflib types.

Reading remote graphs
=====================

Reading graphs from the net is just as straightforward:

.. sourcecode:: pycon

    >>> g.parse("http://bigasterisk.com/foaf.rdf")

    >>> len(g)
    42

The format defaults to ``xml``, which is the common format for .rdf files
you'll find on the net.

See also `the :meth:`~rdflib.graph.Graph.parse` method <http://readthedocs/rdflib3/rdflib.Graph.Graph-class.html#parse>`_ and

`other parsers supported by rdflib 3 <http://readthedocs.com/rdflib3/rdflib.syntax.parsers-module.html>`_
