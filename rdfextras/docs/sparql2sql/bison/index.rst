.. _rdfextras_sparql_bison: RDFExtras SPARQL implementations

|today|
.. currentmodule:: rdfextras.sparql2sql.bison

=====================================================================
:mod:`~rdfextras.sparql2sql.bison` BisonGen full SPARQL syntax parser
=====================================================================

.. automodule:: rdfextras.sparql2sql.bison

.. important:: I just checked in the most recent version of what had been an experimental,
        BisonGen SPARQL parser for RDFLib. It parses a SPARQL query into a set of
        Python objects representing the components of the grammar:

Informative associated postings:

--------------------------------
.. toctree::
   :maxdepth: 2

   fullsparql
Module API
----------

.. currentmodule:: rdfextras.sparql2sql.bison

:mod:`~rdfextras.sparql2sql.bison`
++++++++++++++++++++++++++++++++++

.. automodule:: rdfextras.sparql2sql.bison

:mod:`~rdfextras.sparql2sql.bison.Bindings`
+++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.Bindings
.. autoclass:: PrefixDeclaration
   :members:
.. autoclass:: BaseDeclaration
   :members:

:mod:`~rdfextras.sparql2sql.bison.Expression`
+++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.Expression
.. autoclass:: ParsedConditionalAndExpressionList
   :members:
.. autoclass:: ParsedRelationalExpressionList
   :members:
.. autoclass:: ParsedPrefixedMultiplicativeExpressionList
   :members:
.. autoclass:: ParsedMultiplicativeExpressionList
   :members:
.. autoclass:: ParsedAdditiveExpressionList
   :members:
.. autoclass:: ParsedString
   :members:
.. autoclass:: ParsedDatatypedLiteral
   :members:

:mod:`~rdfextras.sparql2sql.bison.Filter`
+++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.Filter
.. autoclass:: ParsedFilter
   :members:
.. autoclass:: ParsedExpressionFilter
   :members:
.. autoclass:: ParsedFunctionFilter
   :members:

:mod:`~rdfextras.sparql2sql.bison.FunctionLibrary`
++++++++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.FunctionLibrary
.. autoclass:: FunctionCall
   :members:
.. autoclass:: ParsedArgumentList
   :members:
.. autoclass:: ParsedREGEXInvocation
   :members:
.. autoclass:: BuiltinFunctionCall
   :members:

:mod:`~rdfextras.sparql2sql.bison.GraphPattern`
+++++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.GraphPattern
.. autoclass:: ParsedGroupGraphPattern
   :members:
.. autoclass:: BlockOfTriples
   :members:
.. autoclass:: GraphPattern
   :members:
.. autoclass:: ParsedOptionalGraphPattern
   :members:
.. autoclass:: ParsedAlternativeGraphPattern
   :members:
.. autoclass:: ParsedGraphGraphPattern
   :members:

:mod:`~rdfextras.sparql2sql.bison.IRIRef`
+++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.IRIRef
.. autoclass:: IRIRef
   :members:
.. autoclass:: RemoteGraph
   :members:
.. autoclass:: NamedGraph
   :members:

:mod:`~rdfextras.sparql2sql.bison.Operators`
+++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.Operators
.. autoclass:: BinaryOperator
   :members:
.. autoclass:: EqualityOperator
   :members:
.. autoclass:: NotEqualOperator
   :members:
.. autoclass:: LessThanOperator
   :members:
.. autoclass:: LessThanOrEqualOperator
   :members:
.. autoclass:: GreaterThanOperator
   :members:
.. autoclass:: GreaterThanOrEqualOperator
   :members:
.. autoclass:: UnaryOperator
   :members:
.. autoclass:: LogicalNegation
   :members:
.. autoclass:: NumericPositive
   :members:
.. autoclass:: NumericNegative
   :members:

:mod:`~rdfextras.sparql2sql.bison.Processor`
+++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.Processor
.. autoclass:: Processor
   :members:
.. autofunction:: sparql_query

:mod:`~rdfextras.sparql2sql.bison.QName`
+++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.QName
.. autoclass:: QName
   :members:
.. autoclass:: QNamePrefix
   :members:

:mod:`~rdfextras.sparql2sql.bison.Query`
+++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.Query
.. autoclass:: Query
   :members:
.. autoclass:: WhereClause
   :members:
.. autoclass:: SelectQuery
   :members:
.. autoclass:: AskQuery
   :members:
.. autoclass:: ConstructQuery
   :members:
.. autoclass:: DescribeQuery
   :members:
.. autoclass:: Prolog
   :members:

:mod:`~rdfextras.sparql2sql.bison.Resource`
+++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.Resource
.. autoclass:: RDFTerm
   :members:
.. autoclass:: Resource
   :members:
.. autoclass:: TwiceReferencedBlankNode
   :members:
.. autoclass:: ParsedCollection
   :members:

:mod:`~rdfextras.sparql2sql.bison.SPARQLEvaluate`
+++++++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.SPARQLEvaluate
.. autoclass:: Resolver
   :members:
.. autoclass:: NotImplemented
   :members:
.. autofunction:: convertTerm
.. autofunction:: unRollCollection
.. autofunction:: unRollRDFTerm
.. autofunction:: unRollTripleItems
.. autofunction:: mapToOperator
.. autofunction:: createSPARQLPConstraint
.. autofunction:: isTriplePattern

:mod:`~rdfextras.sparql2sql.bison.SolutionModifier`
+++++++++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.SolutionModifier
.. autoclass:: SolutionModifier
   :members:
.. autoclass:: ParsedOrderConditionExpression
   :members:

:mod:`~rdfextras.sparql2sql.bison.Triples`
+++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.Triples
.. autoclass:: PropertyValue
   :members:
.. autoclass:: ParsedConstrainedTriples
   :members:

:mod:`~rdfextras.sparql2sql.bison.Util`
+++++++++++++++++++++++++++++++++++++++++++++
.. automodule:: rdfextras.sparql2sql.bison.Util
.. autoclass:: ListRedirect
   :members:
.. autofunction:: ListPrepend


.. .. autoclass:: Processor
..    :members:
.. 
.. .. autoclass:: SPARQLError
..    :members:
.. 
.. .. automethod:: rdfextras.sparql2sql.generateCollectionConstraint



