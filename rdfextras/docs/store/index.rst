.. _rdfextras_store: RDFExtras, store implementations.

|today|

=============
RDFLib Stores
=============

The basic task: creating a non-native RDF store
-----------------------------------------------

The basic task is to achieve an efficient and proper translation of an RDF 
graph into one or other of the wide range of currently-available data store 
models: relational, key-data, document, etc. Triplestore counts head off into 
the millions *very* quickly, so considered choices amongst the 
speed/space/structure tradeoffs in both storage and retrieval will be 
crucial to the success of any non-trivial attempt. Because data storage 
and retrieval is a highly technical field, those considerations can be 
complex, (a typical paper in the field:
`An Efficient SQL-based RDF Querying Scheme <http://www.nesc.ac.uk/talks/683/oracle_rdf_query_vldb_2005.pdf>`_) and
wide-ranging, as indicated in the W3C deliverable `Mapping Semantic Web Data with RDBMSes <http://www.w3.org/2001/sw/Europe/reports/scalable_rdbms_mapping_report/>`_ report 
(well worth a quick dekko and a leisurely revisit later).

``answers.semanticweb.com``, the semantic web "correlate" of stackoverflow
has some highly informative answers to questions about RDF storage and
contemporary non-native RDF stores: 

    `Storing RDF data into HBase? <http://answers.semanticweb.com/questions/716/storing-rdf-data-into-hbase>`_ 

    `RDF storages vs. other NoSQL storages <http://answers.semanticweb.com/questions/723/rdf-storages-vs-other-nosql-storages>`_ 

The answers are an excellent tour d'horizon of the principles in play and
provide accessible and highly-relevant background support to the RDFLib-specific 
topics that are covered in this document.

Other preliminary reading that would most likely make this document more useful:

* `RDF meets NoSQL <http://decentralyze.com/2010/03/09/rdf-meets-nosql/>`_ Sandro Hawkes, (the comments are useful).


Types of RDF Store
------------------

The domain being modelled is that of RDF graphs and (minimally) statements of 
the form ``{subject, predicate, object}`` (aka *triples*), desirably augmented
with the facility to handle statements about statements (*quoted statements*) and 
references to groups of statements (*contexts*), hence the following broad 
divisions of RDF store, all of which have an impact on the modelling:

    ``Context-aware``: An RDF store capable of storing statements within contexts 
    is considered ``context-aware``. Essentially, such a store is able to partition 
    the RDF model it represents into *individual*, *named*, and *addressable* 
    sub-graphs.

    ``Formula-aware``: An RDF store capable of distinguishing between statements 
    that are *asserted* and statements that are *quoted* is considered ``formula-aware``.

    ``Conjunctive Graph``: This refers to the 'top-level' Graph. It is the 
    aggregation of all the contexts within it and is also the appropriate, 
    absolute boundary for closed world assumptions / models.

    For the sake of persistence, Conjunctive Graphs must be distinguished by 
    identifiers (which may not necessarily be RDF identifiers or may be an RDF 
    identifier normalized - SHA1/MD5 perhaps - for database naming purposes).

The `Notation3 reference <http://www.w3.org/DesignIssues/Notation3.html>`_ 
has relevant information regarding formulae, quoted statements and such.

    "An RDF document parses to a set of statements, or graph. However
    RDF itself has no datatype allowing a graph as a literal value. N3 extends RDF
    allows a graph itself to be referred to within the language, where it is known
    as a ``formula``."

For a more detailed discussion, see Chimezie's blog post `"Patterns and Optimizations for RDF
Queries over Named Graph Aggregates" <http://copia.posterous.com/patterns-and-optimizations-for-rdf-queries-ov>`_


The RDFlib Store API
--------------------
.. toctree::
   :maxdepth: 2

   rdflib_store_api

A bestiary of RDFLib Stores
---------------------------
.. toctree::
   :maxdepth: 1

   bestiary/auditablestorage
   bestiary/backwardchainingstore
   bestiary/bdboptimized
   bestiary/berkeleydb
   bestiary/concurrentstore
   bestiary/kyotocabinet
   bestiary/mysql
   bestiary/nodepickler
   bestiary/postgresql
   bestiary/regexmatching
   bestiary/sparql
   bestiary/sqlite
   bestiary/zodb

Approaches to modelling RDF
---------------------------

.. toctree::
   :maxdepth: 3

   rdfmodelling
   abstract_sql_store
   anatomy

Technical discussions and support
---------------------------------

.. toctree::
   :maxdepth: 2

   performance
   conjquery
   mysqlpg
   bnode_drama


Additional Reading:
-------------------

* `How RDF Databases Differ from Other NoSQL Solutions <http://blog.datagraph.org/2010/04/rdf-nosql-diff>`_
* `RDF on Cloud Number Nine <http://vzach.de/papers/2010_nefors.pdf>`_
* `Versa: Path-Based RDF Query Language <http://www.xml.com/pub/a/2005/07/20/versa.html>`_
* `Versa 2.0 <http://wiki.xml3k.org/Versa>`_
* `A Semantic Graph Query Language <http://www.bearcave.com/misl/misl_tech/dsge_query_language.pdf>`_
* `Experimenting with MongoDB as an RDF Store <http://www.dotnetrdf.org/blogitem.asp?blogID=35>`_
* `SHARD <http://www.dist-systems.bbn.com/people/krohloff/shard.shtml>`_


Resources
---------

* `SHARD-3STORE <http://sourceforge.net/projects/shard-3store/>`_
* `Berlin SPARQL Benchmark (BSBM) <http://www4.wiwiss.fu-berlin.de/bizer/BerlinSPARQLBenchmark/>`_
* `BSBM Tools - Java-implemented test dataset generator <http://sourceforge.net/projects/bsbmtools/>`_ 
* `DAWG SPARQL Testcases <http://www.w3.org/2001/sw/DataAccess/tests/r2>`_
* `Thea SWIProlog-OWL <https://github.com/vangelisv/thea/wiki>`_
* `RDFS and OWL2 RL <http://www.ivan-herman.net/Misc/2008/owlrl/>`_


Scamped Notes
^^^^^^^^^^^^^^

`Rob Vesse <http://answers.semanticweb.com/questions/2579/approaches-to-storing-semantic-data-in-a-document-database-like-mongodb>`_

    The one I settled on is essentially to have a single simple document 
    which represents the existence of the Graph:

    .. code-block:: javascript

        {
          name: "some-name" ,
          uri: "http://example.org/graph"
        }
        
    And then to have a document for each individual triple:

    .. code-block:: javascript

        {
          subject : "<http://example.org/subject>" ,
          predicate : "<http://example.org/predicate>" ,
          object : "<http://example.org/object>" ,
          graphuri : "http://example.org/graph"
        }
    
    I took advantage of MongoDBs indexing capabilities to generate indexes 
    on Subject, Predicate, Object and Graph URI and then used these to apply 
    SPARQL queries over MongoDB and it worked reasonably well. Though as I 
    note in my blog post it isn't going to replace dedicated triple stores 
    but does work well for small scale stores - actual performance would 
    vary depending on your data and how you use it in your application.

Vasiliy Faronov

    Suppose I am building a Linked Data client app based on Python and RDFLib,
    and I want to do some reasoning. Most likely I have a few vocabularies that
    are dear to my heart, and want to do RDFS reasoning with them, i.e.
    materialize superclass membership, superproperty values etc. I also want to
    handle owl:sameAs in instance data. Support for the rest of OWL is welcome
    but not essential.

    The graphs I will be working with are rather small, let’s say on the order
    of 10,000 triples (all stored in memory), but I need to reason in real-time
    (e.g. my client is an end-user app that works with Linked Data) and so
    delays should be small.

    But most importantly, the solution has to be as easy to use as possible. 
    Ideally:

    .. code-block:: python

        import reasoner
        reasoner.infer_all(my_rdflib_graph)

    What are my best options?



:author: `Graham Higgins <http://bel-epa.com/gjh/>`_

:contact: Graham Higgins, gjh@bel-epa.com

:version: 0.1


