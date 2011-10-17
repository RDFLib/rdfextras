.. _rdfextras_sparql_sql: RDFExtras SPARQL implementations

|today|

================================================
SPARQL-to-SQL
================================================

Introduction
============

From `Chime's posterous <http://chimezie.posterous.com/?page=2>`_ of *10 November 2009* ...

    Our paper `<http://doi.acm.org/10.1145/1620432.1620437>`_ on a complete
    translation from SPARQL into efficient SQL has been published (it looks like it has been
    on the ACM portal for some time). This is the basis for our RDF `warehouse
    <http://www.w3.org/2001/sw/sweo/public/UseCases/ClevelandClinic/>`_ at the
    Cleveland Clinic that was recently 
    `committed <http://code.google.com/p/rdflib/source/detail?r=1545>`_ back to rdflib.


        A feature-complete translation from SPARQL, the proposed standard for
        RDF querying, into efficient SQL. We propose "SQL model"-based
        algorithms that implement each SPARQL algebra operator via SQL query
        augmentation, and generate a flat SQL statement for efficient
        processing by relational database query engines. SPARQL-to-SQL
        translation presented is feature-complete, since it applies to all
        SPARQL language features. Finally, we demonstrate the performance and
        scalability of our method by an extensive evaluation using recent
        SPARQL benchmark queries, and a benchmark dataset, as well as a
        real-world photo dataset.


From `W3C SWEO Use Cases <http://www.w3.org/2001/sw/sweo/public/UseCases/ClevelandClinic/>`_

    At the time of this writing, the patient record dataset has upwards of 54.2
    million RDF assertions. The dataset is managed using the RDFLib open source
    RDF library and its MySQL adapter, which delegates physical storage to a
    centralized MySQL database. The MySQL database resides on an SGI Altix 350
    super computer. In addition, stored SPARQL queries can be dispatched within a
    large distributed computing cluster.


Related work
------------
**A Mapping of SPARQL Onto Conventional SQL** by *Eric Prud'hommeaux* and *Alexandre 
Bertails* `W3C Paper <http://www.w3.org/2008/07/MappingRules/StemMapping>`_

    This paper documents a semantics for expressing relational data as
    an RDF graph [RDF] and an algebra for mapping SPARQL SELECT queries over
    that RDF to SQL queries over the original relational data. The RDF graph,
    called the stem graph, is constructed from the relational structure and a
    URI identifier called a stem URI. The algebra specifies a function taking
    a stem URI, a relational schema and a SPARQL query over the corresponding
    stem graph, and emitting a relational query, which, when executed over the
    relational data, produces the same solutions at the SPARQL query executed
    over the stem graph. Relational databases exposed on the Semantic Web can
    be queried with SPARQL with the same performance as with SQL.

**Semantics preserving SPARQL-to-SQL translation** by *Artem Chebotko*, *Shiyong* 
and *Lu* *Farshad Fotouhi* (`ACM entry <http://portal.acm.org/citation.cfm?id=1598336>`_)

    Most existing RDF stores, which serve as metadata repositories on
    the Semantic Web, use an RDBMS as a backend to manage RDF data. This
    motivates us to study the problem of translating SPARQL queries into
    equivalent SQL queries, which further can be optimized and evaluated by
    the relational query engine and their results can be returned as SPARQL
    query solutions. The main contributions of our research are: (i) We
    formalize a relational algebra based semantics of SPARQL, which bridges
    the gap between SPARQL and SQL query languages, and prove that our
    semantics is equivalent to the mapping-based semantics of SPARQL; (ii)
    Based on this semantics, we propose the first provably semantics
    preserving SPARQL-to-SQL translation for SPARQL triple patterns, basic
    graph patterns, optional graph patterns, alternative graph patterns, and
    value constraints; (iii) Our translation algorithm is generic and can be
    directly applied to existing RDBMS-based RDF stores; and (iv) We outline a
    number of simplifications for the SPARQL-to-SQL translation to generate
    simpler and more efficient SQL queries and extend our defined semantics
    and translation to support the bag semantics of a SPARQL query solution.
    The experimental study showed that our proposed generic translation can
    serve as a good alternative to existing schema dependent translations in
    terms of efficient query evaluation and/or ensured query result
    correctness.


Contents:
---------

.. toctree::
   :maxdepth: 2

.. currentmodule:: rdfextras.sparql2sql.sql

.. automodule:: rdfextras.sparql2sql.sql

:mod:`~rdfextras.sparql2sql.sql.DatabaseStats`
----------------------------------------------------------
.. automodule:: rdfextras.sparql2sql.sql.DatabaseStats
.. autoclass:: CSVWriter
   :members:
.. autofunction:: OpenGraph
.. autofunction:: GetCachedStats
.. autofunction:: LoadCachedStats
.. autofunction:: GetDatabaseStats
.. autofunction:: CountDistint
.. autofunction:: CountDistinctForColumn
.. autofunction:: CountTriples
.. autofunction:: PredicateJoinCount
.. autofunction:: Stats2CSV
.. autofunction:: Key2Dict
.. autofunction:: HistClass
.. autofunction:: TableSum
.. autofunction:: AddError
.. autofunction:: WriteErrorResults
.. autofunction:: CalculateEstimationAccuracy
.. autofunction:: WriteAllResults

:mod:`~rdfextras.sparql2sql.sql.QueryCostEstimator`
----------------------------------------------------------
.. automodule:: rdfextras.sparql2sql.sql.QueryCostEstimator
.. autoclass:: QueryTree
   :members:
.. autoclass:: QuerySelection
   :members:
.. autoclass:: QueryCostEstimator
   :members:
.. autofunction:: ColDistMax

:mod:`~rdfextras.sparql2sql.sql.QueryStats`
----------------------------------------------------------
.. automodule:: rdfextras.sparql2sql.sql.QueryStats
.. autofunction:: ResetDepth
.. autofunction:: AddDepth
.. autofunction:: SubDepth
.. autofunction:: ChangeDepth
.. autofunction:: DepthPrint
.. autofunction:: QueryStats
.. autofunction:: PrintSyntaxTree
.. autofunction:: GetQueryInfo
.. autofunction:: GetQueryWhereInfo
.. autofunction:: GetTripleInfo
.. autofunction:: GetVarInfo
.. autofunction:: GetQueryFilterInfo
.. autofunction:: GetQueryStats

:mod:`~rdfextras.sparql2sql.sql.RdfSqlBuilder`
----------------------------------------------------------
.. automodule:: rdfextras.sparql2sql.sql.RdfSqlBuilder
.. autoclass:: ViewTable
   :members:
.. autoclass:: TriplesTable
   :members:
.. autoclass:: AllObjectsTable
   :members:
.. autoclass:: RdfVariable
   :members:
.. autoclass:: RdfVariableSource
   :members:
.. autoclass:: BNodeRef
   :members:
.. autoclass:: RdfSqlBuilder
   :members:
.. autofunction:: IsAVariable
.. autofunction:: EmptyVar

:mod:`~rdfextras.sparql2sql.sql.RelationalAlgebra`
----------------------------------------------------------
.. automodule:: rdfextras.sparql2sql.sql.RelationalAlgebra
.. autofunction:: TopEvaluate
.. autoclass:: RelQuery
   :members:
.. autoclass:: RelSelectQuery
   :members:
.. autoclass:: RelAskQuery
   :members:
.. autoclass:: RelGraph
   :members:
.. autoclass:: RelUnion
   :members:
.. autoclass:: RelAnd
   :members:
.. autoclass:: RelOptional
   :members:
.. autoclass:: RelGroup
   :members:
.. autoclass:: RelBGP
   :members:
.. autoclass:: RelEmpty
   :members:
.. autoclass:: RelTriple
   :members:
.. autoclass:: RelFilter
   :members:
.. autoclass:: RelVariableExp
   :members:
.. autoclass:: RelConstantExp
   :members:
.. autoclass:: RelLiteralExp
   :members:
.. autoclass:: RelUriExp
   :members:
.. autoclass:: RelBinaryExp
   :members:
.. autoclass:: RelUnaryExp
   :members:
.. autoclass:: RelFunctionExp
   :members:
.. autoclass:: RelTypeCastExp
   :members:
.. autofunction:: ExecuteSqlQuery
.. autofunction:: GetDataTypes
.. autofunction:: ProcessRow
.. autofunction:: ParseQuery
.. autofunction:: ParseAsk
.. autofunction:: ParseSelect
.. autofunction:: ParseGraphPattern
.. autofunction:: ParseGraphPatternSimple
.. autofunction:: ParseGraph
.. autofunction:: ParseUnion
.. autofunction:: xcombine
.. autofunction:: FindValidJoinField
.. autofunction:: ParseOptional
.. autofunction:: ParseGroup
.. autofunction:: ParseBGP
.. autofunction:: ParseTriples
.. autofunction:: ParseFilter
.. autofunction:: ParseFilterExp
.. autofunction:: ParseBinaryOperator
.. autofunction:: ParseUnaryOperator
.. autofunction:: ParseFunction

:mod:`~rdfextras.sparql2sql.sql.RelationalOperators`
----------------------------------------------------------
.. automodule:: rdfextras.sparql2sql.sql.RelationalOperators
.. autoclass:: RelationalOperator
   :members:
.. autoclass:: RelationalExpOperator
   :members:
.. autoclass:: RelationalTerminalExpOperator
   :members:
.. autoclass:: NoResultsException
   :members:

:mod:`~rdfextras.sparql2sql.sql.SqlBuilder`
----------------------------------------------------------
.. automodule:: rdfextras.sparql2sql.sql.SqlBuilder
.. autoclass:: FromJoinNode
.. autoclass:: SqlBuilder

.. .. autoclass:: Processor
..    :members:
.. 
.. .. autoclass:: SPARQLError
..    :members:





