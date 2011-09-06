.. _rdfextras.store.abstractsqlstore: RDFExtras, stores, AbstractSQLStore.

|today|

=====================================================
AbstractSQLStore, SQL-92 formula-aware implementation
=====================================================

:mod:`~rdfextras.store.AbstractSQLStore`
-----------------------------------------

SQL-92 formula-aware implementation of an rdflib Store. It stores its triples
in the following partitions:

 * Asserted non rdf:type statements
 * Asserted literal statements
 * Asserted rdf:type statements (in a table which models Class membership)
    The motivation for this partition is primarily query speed and 
    scalability as most graphs will always have more rdf:type statements 
    than others
 * All Quoted statements

In addition it persists namespace mappings in a separate table

    **"Addressing the RDF Scalability Bottleneck"**, post by Uche `28 Oct 2005 <http://copia.posterous.com/addressing-the-rdf-scalability-bottleneck>`_

    I've been building RDF persistence stores for some time (it's gone from
    something of a hobby to the primary responsibility in my current work
    capacity) and have come to the conclusion that RDF stores will almost always
    be succeptible to the physical limitations of database scalability.

    I recall when I was at the Semantic Technology Conference this spring and
    asked one of the presenters there what he thought about this problem that all
    RDF databases face and the reason why most don't function effectively beyond
    5-10 million triples. I liked his answer:

    It's an engineering problem

    Consider the amount of information an adult has stored (by whatever mechanism
    the human brain uses to persist information) in his or her noggin. We often
    take it for granted - as we do all other aspects of biology we know very
    little about - but it's worth considering when thinking about why scalability
    is a ubiquitous hurdle for RDF databases.

    Some basic Graph theory is relevant to this point:

    The size of a graph is the number of edges and the order of a graph is the
    number of nodes within the graph. RDF is a Resource Description Framework
    (where what we know about resources is key - not so much the resouces
    themselves) so it's not surprising that RDF graphs will almost always have a
    much larger size than order. It's also not suprising that most performance
    analysis made across RDF implementations (such as LargeTripleStores for
    instance) focus mostly on triple size.

    I've been working on a SQL-based persistence schema for RDF content (for
    rdflib) that is a bit different from the standard approaches taken by most
    RDBMS implementations of RDF stores I'm familiar with (including those I've
    written). Each of the tables are prefixed with a SHA1-hashed digest of the
    identifier associated with the 'localized universe' (AKA,the boundary for a
    closed world assumptions). The schema is below:

    .. sourcecode:: sql

        CREATE TABLE %s_asserted_statements (
            subject       text not NULL,
            predicate     text not NULL,
            object        text,
            context       text not NULL,
            termComb      tinyint unsigned not NULL,    
            objLanguage   varchar(3),
            objDatatype   text,
            INDEX termComb_index (termComb),    
            INDEX spoc_index (subject(100),predicate(100),object(50),context(50)),
            INDEX poc_index (predicate(100),object(50),context(50)),
            INDEX csp_index (context(50),subject(100),predicate(100)),
            INDEX cp_index (context(50),predicate(100))) TYPE=InnoDB

        CREATE TABLE %s_type_statements (
            member        text not NULL,
            klass         text not NULL,
            context       text not NULL,
            termComb      tinyint unsigned not NULL,
            INDEX termComb_index (termComb),
            INDEX memberC_index (member(100),klass(100),context(50)),
            INDEX klassC_index (klass(100),context(50)),
            INDEX c_index (context(10))) TYPE=InnoDB"""

        CREATE TABLE %s_quoted_statements (
            subject       text not NULL,
            predicate     text not NULL,
            object        text,
            context       text not NULL,
            termComb      tinyint unsigned not NULL,
            objLanguage   varchar(3),
            objDatatype   text,
            INDEX termComb_index (termComb),
            INDEX spoc_index (subject(100),predicate(100),object(50),context(50)),
            INDEX poc_index (predicate(100),object(50),context(50)),
            INDEX csp_index (context(50),subject(100),predicate(100)),
            INDEX cp_index (context(50),predicate(100))) TYPE=InnoDB

    The first thing to note is that statements are partitioned into logical groupings:

    **Asserted non ``rdf:type`` statements**: where all asserted RDF statements where the
    predicate isn't ``rdf:type`` are stored

    **Asserted ``rdf:type`` statements**: where all asserted ``rdf:type`` statements are
    stored

    **Quoted statements**: where all quoted / hypothetical statements are stored

    Statement quoting is a Notation 3 concept and an extension of the RDF model
    for this purpose. The most significant partition is the rdf:type grouping. The
    idea is to have class membership modeled at the store level instead of at a
    level above it. RDF graphs are as different as the applications that use them
    but the primary motivating factor for making this seperation was the
    assumption that in most RDF graphs a majority of the statements (or a
    significant portion) would consist of rdf:type statements (statements of class
    membership).

    Class membership can be considered an unstated RDF modelling best practice
    since it allows an author to say alot about a resource simply by associating
    it with a class that has it's semantics completely spelled out in a separate,
    supporting ontology.

    The ``rdf:type`` table models class membership explicitely with two columns: klass
    and member. This results in a savings of 43 characters per ``rdf:type`` statement.
    The implementation takes note of the predicate submitted in triple-matching
    pattern and determines which tables to search.

    Consider the following triple pattern:

        ``http://metacognition.info ?predicate ?object``

    The persistence layer would know it needs to check against the table that
    persists non rdf:type statements as well as the class membership table.
    However, patterns that match against a specific predicate (other than
    ``rdf:type``) or class membership queries only need to check within one partition
    (or table):

        ``http://metacognition.info rdf:type ?klass``

    In general, I've noticed that being able to partition your SQL search space
    (searching within a named graph / context or searching within a single table)
    goes along way in query response.

    The other thing worth noting is the ``termComb`` column, which is an integer value
    representing the 40 unique ways the following RDF terms could appear in a
    triple:

    * URI Ref
    * Blank Node
    * Formula
    * Literal
    * Variable

    I'm certain there are many other possible optimizations that can be made in a
    SQL schema for RDF triple persistence (there isn't much precedent in this
    regard - and Oracle has only recently joined the foray) but partitioning
    ``rdf:type`` statements separately is one such thought I've recently had.

Modules
--------

.. automodule:: rdfextras.store.AbstractSQLStore
.. autoclass:: SQLGenerator
   :members:
.. autoclass:: AbstractSQLStore
   :members:
.. autofunction:: queryAnalysis
.. autofunction:: unionSELECT
.. autofunction:: extractTriple
.. autofunction:: createTerm
