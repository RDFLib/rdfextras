.. _rdfextras_store: RDFExtras, store implementations.

|today|

================================
Back-end stores and persistences
================================

TODO: More detailed documentation (design rationale, pros and cons of the 
different implementations), benchmarks.

.. automodule:: rdfextras.store

Types of store available for use with rdflib
============================================


Context-aware
-------------
An RDF store capable of storing statements within contexts is considered
``context-aware``. Essentially, such a store is able to partition the RDF model
that it represents into *individual*, *named* and *addressable* sub-graphs.

`Relevant Notation3 reference <http://www.w3.org/DesignIssues/Notation3.html>`_ 
regarding formulae, quoted statements, and such. e.g.

	"An RDF document parses to a set of statements, or graph. However
	RDF itself has no datatype allowing a graph as a literal value. N3 extends RDF
	allows a graph itself to be referred to within the language, where it is known
	as a ``formula``."

Formula-aware
-------------

An RDF store that is capable of distinguishing between statements that are
``asserted`` and those that are ``quoted`` is considered to be *formula-aware*.

Conjunctive Graph
-----------------

This refers to the 'top-level' Graph. It is the aggregation of all the
contexts within it and is also the appropriate absolute boundary for closed
world assumptions and/or models.

For the sake of persistence, Conjunctive Graphs must be distinguished by
identifiers. They may not necessarily be RDF identifiers or they may be an RDF
identifier that has been normalized - SHA1/MD5 perhaps - for database-naming
purposes.

Conjunctive Query
-----------------
Any query that doesn't limit the store to search within a named context only.
Such a query expects a context-aware store to search the entire asserted
universe (the conjunctive graph). A formula-aware store is expected not to
include quoted statements when matching such a query.

To this effect, see Chimezie's blog post `"Patterns and Optimizations for RDF
Queries over Named Graph Aggregates" <http://copia.posterous.com/patterns-and-optimizations-for-rdf-queries-ov>`_

Contents:
=========

.. toctree::
   :maxdepth: 3
   
   backends
   range
   conjquery
   mysqlpg
   bnode_drama
   rdfmodelling



:author: `Graham Higgins <http://bel-epa.com/gjh/>`_

:contact: Graham Higgins, gjh@bel-epa.com

:version: 0.1


