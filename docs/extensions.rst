.. _rdfextras_extensions: RDFExtras Exensions

|today|

=====================================
Extending SPARQL Basic Graph Matching
=====================================

*Robbed from the W3C's* `SPARQL Query Language for RDF <http://www.w3.org/TR/rdf-sparql-query/#sparqlBGPExtend>`_

The overall SPARQL design can be used for queries which assume a more
elaborate form of entailment than simple entailment, by re-writing the
matching conditions for basic graph patterns. Since it is an open research
problem to state such conditions in a single general form which applies to all
forms of entailment and optimally eliminates needless or inappropriate
redundancy, this document only gives necessary conditions which any such
solution should satisfy. These will need to be extended to full definitions
for each particular case.

Basic graph patterns stand in the same relation to triple patterns that RDF
graphs do to RDF triples, and much of the same terminology can be applied to
them. In particular, two basic graph patterns are said to be equivalent if
there is a bijection ``M`` between the terms of the triple patterns that maps
blank nodes to blank nodes and maps variables, literals and IRIs to
themselves, such that a triple ``( s, p, o )`` is in the first pattern if and only
if the triple ``( M(s), M(p) M(o) )`` is in the second. This definition extends
that for RDF graph equivalence to basic graph patterns by preserving variable
names across equivalent patterns.

An entailment regime specifies

* a subset of RDF graphs called well-formed for the regime
* an entailment relation between subsets of well-formed graphs and well-formed graphs.

Examples of entailment regimes include simple entailment, RDF entailment, RDFS
entailment, D-entailment and OWL-DL entailment. Of these, only OWL-DL
entailment restricts the set of well-formed graphs. If ``E`` is an entailment
regime then we will refer to ``E-entailment``, ``E-consistency``, etc, following this
naming convention.

Some entailment regimes can categorize some RDF graphs as inconsistent. For
example, the RDF graph:

.. sourcecode:: n3

    _:x rdf:type xsd:string .
    _:x rdf:type xsd:decimal .

is ``D-inconsistent`` when ``D`` contains the XSD datatypes. The effect of a
query on an inconsistent graph is not covered by this specification, but must
be specified by the particular SPARQL extension.

A SPARQL extension to E-entailment must satisfy the following conditions.

1. The scoping graph, ``SG``, corresponding to any consistent active graph ``AG`` is uniquely specified and is ``E-equivalent`` to ``AG``.

2. For any basic graph pattern BGP and pattern solution mapping ``P, P(BGP)`` is well-formed for ``E``

3. For any scoping graph ``SG`` and answer set ``{P1 ... Pn}`` for a basic graph pattern BGP, and where ``{BGP1 .... BGPn}`` is a set of basic graph patterns all equivalent to BGP, none of which share any blank nodes with any other or with ``SG``. ``SG`` ``E-entails`` ``(SG union P1(BGP1) union ... union Pn(BGPn))``. These conditions do not fully determine the set of possible answers, since RDF allows unlimited amounts of redundancy. In addition, therefore, the following must hold.

4. Each SPARQL extension must provide conditions on answer sets which guarantee that every BGP and ``AG`` has a finite set of answers which is unique up to RDF graph equivalence.

