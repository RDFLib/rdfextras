.. _rdfextras_sparql: rdfextras sparql-p SPARQL implementation

|today|

==========================================
"sparql-p" (default) SPARQL implementation
==========================================

Originally, on *Wednesday 24 August, 2005*: 

    **rdflib and SPARQL** by *Michel Pelletier*:
    
    As some of you know rdflib has been slowly growing SPARQL support. It started
    when Ivan Herman from the W3C implemented the SPARQL query logic for rdflib
    and contributed it back to us. The bulk of his work is in the rdflib.sparql
    module. While not a complete SPARQL implementation, because it lacked a
    parser, it represented the bulk of the work necessary to implement a SPARQL
    query language, ie, the actual query logic.

    On the parser front I have made some progress. You can find it in
    rdflib.sparql.grammar in the current SVN. It depends on the excellent
    `pyparsing <http://sourceforge.net/projects/pyparsing/>`_ library to parse
    SPARQL queries into a structured token object from which all of the
    relevant bits of data about a particular SPARQL query can be extracted.
    The grammar is still young and being tested and it doesn't work for all
    queries, but it's a start. I've written a script that applies the grammar
    to all of the standard SPARQL tests, so that over time I can keep working
    on it until all the tests pass. Once we have a working parser that parses
    all the known SPARQL test queries then we can implement the last piece,
    the thin glue layer between the parser and Ivan's query logic. I'm hoping
    that by rdflib 2.4 or 2.5 we can brag about having full SPARQL support as
    well as being able to successfully run and prove all of the standard
    tests. This would be a huge milestone for us as it would drive more
    developers to rdflib, if only because they want a framework against which
    to test and verify the spec: it encourages the existing SPARQL gurus out
    there to come our way because of the amazingly low barrier of entry rdflib
    provides by being pure Python.

Subsquently, on *10 Oct 2005*:

    **SPARQL in RDFLib (Version 2.1)** by *Ivan Herman*

    This is a short overview of the query facilities added to `RDFLib <http://rdflib.net>`_. 
    These are based on the July 2005 version of the `SPARQL draft <http://www.w3.org/TR/rdf-sparql-query/>`_
    worked on at the W3C. For a lack of a better word, I refer to this implementation as ``sparql-p``.

    Thanks to the work of Daniel Krech and mainly Michel Pelletier,
    ``sparql-p`` is now fully integrated with the newer versions of RDFLib
    (version `2.2.2 <http://rdflib.net/2005/09/10/rdflib-2.2.2/README/>`_ or
    later), whereas earlier versions were distributed as separate packages.
    This integration has led to some minor adjustments in class naming and
    structure compared to earlier versions. If you are looking for the
    documentation of the separate package, please refer to an `earlier version
    <http://dev.w3.org/cvsweb/~checkout~/2004/PythonLib-IH/Doc/sparqlDesc.html?rev=1.8>`_
    of this document. Be warned, though, that the earlier versions are now
    deprecated in favour of RDFLib 2.2.2 or later.
    
    The SPARQL draft describes its facilities in terms of a query language. A
    full SPARQL implementation should include a parser of that language
    mapping on the underlying implementation. ``sparql-p`` does *not* include
    such parser yet, only the underlying SPARQL engine and its API. The
    description below shows how the mapping works. This also means that the
    API is not the full implementation of SPARQL: some of the features should
    be left to the parser that could use this API. This is the case, for
    example, of named Graphs facilities that could be mapped using RDFLib
    ``Graph`` instances: *all* query is performed on such an instance in the
    first place! In any case, the implementation of ``sparql-p`` covers (I
    believe) the most frequently used cases of SPARQL. --- Intro

Later still, on *May 19 2006*:

    **SPARQL BisonGen Parser Checked in to RDFLib** `blog post <http://copia.posterous.com/sparql-bisongen-parser-checked-in-to-rdflib>`_ by *Chimezie* 
    
    I just checked in the most recent version of what had been an experimental,
    generated (see: http://copia.ogbuji.net/blog/2005-04-27/Of_BisonGe) parser for
    the full SPARQL syntax, I had been working on to hook up with ``sparql-p``. It
    parses a SPARQL query into a set of Python objects representing the components
    of the grammar:

    http://svn.rdflib.net/trunk/rdflib/sparql/bison/

    The parses itself is a Python/C extension, so the setup.py had to be modified
    in order to compile it into a Python module.

    I also checked in a test harness that’s meant to work with the DAWG test
    cases:

    http://svn.rdflib.net/trunk/test/BisonSPARQLParser

    I’m currently stuck on this test case, but working through it:

    http://www.w3.org/2001/sw/DataAccess/tests/#optional-outer-filter-with-bound

    The test harness only checks for parsing, it doesn’t evaluate the parsed query
    against the corresponding set of test data, but can be easily be extended to
    do so.

    I’m not sure about the state of those test cases, some have been ‘accepted’
    and some haven’t. I came across a couple that were illegal according to the
    most recent `SPARQL grammar <http://www.w3.org/2001/sw/DataAccess/rq23/rq24-algebra.html>`_ (the bad tests are noted in the test harness).
    Currently the parser is stand-alone, it doesn’t invoke sparql-p for a few
    reasons:

    I wanted to get it through parsing the queries in the test case first

    Our integrated version of sparql-p is outdated as there is a more recent
    version that Ivan has been working on with some improvements we should
    consider integrating

    Some of the more complex combinations of Graph Patterns don’t seem solvable
    without re-working / extending the expansion tree solver. I have some ideas
    about how this could be done (to handle things like nested UNIONS and
    OPTIONALs) but wanted to get a working parser in first


And later yet, on *Sun, 01 Apr 2007*

    **SPARQL Algebra, Reductions, Forms and Mappings for Implementations** a `post to public-sparql-dev <http://www.mail-archive.com/public-sparql-dev@w3.org/msg00040.html>`_ by *Chimezie*

    I've been gearing up to an attempt at implementing the Compositional
    SPARQL semantics expressed in both the 'Semantics of SPARQL' and
    'Semantics and Complexity of SPARQL' papers with the goal of reusing
    existing sparql-p which already implements much of the evaluation
    semantics.  Some intermediate goals are were neccessary for the first
    attempt at such a design [1]:

    * Incorporate rewrite rules outlined in the current DAWG SPARQL WD
    * Incorporate reduction to Disjunctive Normal Form outlined in `Semantics and Complexity of SPARQL <http://www.dcc.uchile.cl/~cgutierr/papers/sparql.pdf>`_
    * Formalize a mapping *from* the DAWG algebra notation to that outlined in `Semantics of SPARQL <http://ing.utalca.cl/~jperez/papers/sparql_semantics.pdf>`_
    * Formalize a mapping *from* the compositional semantics to `sparql-p <http://dev.w3.org/cvsweb/~checkout~/2004/PythonLib-IH/Doc/sparqlDesc.html?rev=1.11&content-type=text/html;%20charset=iso-8859-1>`_ methods

    In attempting to formalize the above mappings I noticed some
    interesting parallels that I thought you and Ivan might be interested
    in (given the amount independent, effort that was put into both the
    formal semantics and the implementations).  In particular

    The proposed disjunctive normal form of SPARQL patterns coincides
    directly with the 'query' API of sparql-p [2] which essentially
    implements evaluation of SPARQL patterns of the form:

    .. sourcecode:: text
    
        (P1 UNION P2 UNION .... UNION PN) OPT A) OPT B) ... OPT C)

    I.e., DNF extended with OPTIONAL patterns.

    In addition, I had suggested [3] to the DAWG that they consider
    formalizing a function symbol which relates a set of triples to the
    IRIs of the graphs in which they are contained.  As Richard Newman
    points out, this is implemented [4] by most RDF stores and in RDFLib
    in particular by the ConjunctiveGraph.contexts method:

    .. sourcecode:: text
    
        contexts((s,p,o)) -> {uri1,uri2,...}

    I had asked their thoughts on performance impact on evaluating GRAPH
    patterns declaratively instead of imperatively (the way they are
    defined in both the DAWG semantics and the Jorge P. et. al papers) and
    I'm curious on your thoughts on this as well.

    Finally, an attempt at a formal mapping from DAWG algebra evaluation
    operators to the operators outlined in the Jorge P.et. al papers is
    below:

    .. sourcecode:: text
    
        merge(μ1,μ2)             = μ1 ∪ μ2
        Join(Omega1,Omega2)      = Filter(R,Omega1 ⋉ Omega2)
        Filter(R,Omega)          = [[(P FILTER R)]](D,G)
        Diff(Omega1,Omega2,R)    = (Omega1 \ Omega2) ∪ {μ | μ in Omega1 ⋉
        Omega2 and *not* μ |= R}
        Union(Omega1,Omega2)     = Omega1 ∪ Omega2

Related documents
=================

.. toctree::
   :maxdepth: 3

   compformsem
   rdfqueryapi
   detailed_description 

Modules
=======

.. toctree::
   :maxdepth: 3
  
   sparql.rst
   algebra.rst
   components.rst
   evaluate.rst
   graph.rst
   operators.rst
   parser.rst
   processor.rst
   query.rst


