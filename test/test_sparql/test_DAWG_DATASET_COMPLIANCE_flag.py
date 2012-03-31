import unittest
from nose.exc import SkipTest
from rdflib.graph import ConjunctiveGraph as Graph, URIRef

"""
`Issue #45 <https://code.google.com/p/rdflib/issues/detail?id=45>`_ refers.

`r1480 <https://code.google.com/p/rdflib/source/detail?r=1480>`_ exposes 
another error here, where ``ASK{}`` will return False when 
``DAWG_DATASET_COMPLIANCE`` is set to True, and the triple does exist. 

See also `RDF Composite Datasets 
<http://www.w3.org/2009/sparql/wiki/Feature:CompositeDatasets>`_


http://www.mail-archive.com/dev@rdflib.net/msg00237.html
-------------------------------------------------------------------------------
Chimezie Ogbuji
Thu, 09 Aug 2007 08:58:16 -0700

Some explanation of this switch (DAWG_DATASET_COMPLIANCE) might shed
some light.  If you follow SPARQL specification verbatim, the
'default' graph is always the first one that is matched.  The
'default' graph is a graph without an identifier - or at least, its
identifier cannot be matched.  This breaks with RDFLib where *all*
Graphs have an identifier which can be matched (note the Graph.quads
method).  In the absence of a default graph specified explicitly as
the dataset for the query (via FROM <..>), the default graph is an
empty graph, so any pattern without a GRAPH directive will always
match nothing! In order to comply with SPARQL, the assumption had to
be made (when the compliance flag is set to True) that the default
context for a ConjunctiveGraph is *the* default graph (as defined by
SPARQL).

Take a look at the graph tests for an example of what is the
'expected' verbatim behavior here - and how it might be problematic
for RDFLib without these caveats:

http://www.w3.org/2001/sw/DataAccess/tests/data-r2/graph/

This switch was a first attempt to allow a break from this verbatim
interpretation which is problematic for practical use where you have
an RDF dataset all with well-defined identifiers and you wish to have
SPARQL patterns without GRAPH operators search within all the named
graphs (which is the expected behavior of ConjunctiveGraph.quads()).
The default is True, currently.  Perhaps it should be false by default
instead?

This is not the only area where RDFLib's SPARQL capabilities break
from the verbatim spec interpretation.  SPARQL does not allow direct
matching of BNodes in persistence, RDFLib does.  So SPARQL patterns
with BNode identifiers evaluated within RDFLib will match those BNodes
in persistence with the same name.  It is a well known frustration to
not be able to carry BNode identifiers from one query session to
another (especially against RDF graphs which make heavy use of
BNodes).

-------------------------------------------------------------------------------
Chimezie Ogbuji
Sat, 11 Aug 2007 06:56:31 -0700
> soooooo... if I add a FROM <my-graph-uri> my problem should be solved?

FROM <my-graph-uri> will cause the RDF dereferenced from that URI to
comprise the default graph.  Since the default graph is matched by
default, any SPARQL patterns in the query will be matched against that
graph (as long as GRAPH is not used)


-------------------------------------------------------------------------------
Chimezie Ogbuji
Wed, 19 Sep 2007 05:41:58 -0700

Some clarification.

> soooooo... if I add a FROM <my-graph-uri> my problem should be solved?

This should only be used against a ConjunctiveGraph since it will cause it to
load the default graph ("context").  If you are dispatching SPARQL, you
should either do it against a ConjunctiveGraph or use a GRAPH name / variable
in the expression (perhaps with a topLevel binding of the graph's identifier::

    g.query(query, initBindings={Variable('graphName'): g.identifier}).

SPARQL queries are dispatched against RDF datasets, which are composed of 
'multiple' RDF graphs.

-------------------------------------------------------------------------------
Chimezie Ogbuji
Wed, 19 Sep 2007 14:32:01 -0700

> I think saying graph.query(somequery) explicitly says "I want to query this
> graph", and no ids should be necessary

True.  In retrospect, I guess it would simply be an API shortcut for
"construct a RDF dataset consisting of an empty set of URI labeled
graphs and a default graph composed of the source graph and evaluate
the query".

That accommodates both SPARQL and the RDFLib API

> (note... this is what seems to be going on) so though I accept that
> passing in the initBinding would work, why are you making me do that?

It was only a first attempt to reconcile the expected behavior for
matching RDF datasets with the RDFLib API.  This is not a trivial
consideration.  See: `No way to specify an RDF dataset of all the
known named graphs`__, for instance:

.. __:http://lists.w3.org/Archives/Public/public-rdf-dawg-comments/2007Apr/0001.html

> And why should CG and Graph act differently here
> (and why should I have to care?)

See above.  I can add the above behavior.

> > SPARQL queries are dispatched against RDF datasets, which are
> > composed of 'multiple' RDF graphs.
> hmmm... I picked that up from the  crazy conditional blocks in
> rdflib.sparql.Algebra.TopEvaluate (speaking of which,
> shouldn't we be following
> http://www.python.org/dev/peps/pep-0008/?)

Sure.  I've been a little more preoccupied with implementing full
SPARQL behavior than formatting printable code =).

> would the determination of dataset be something that should happen outside
> of the graph API?

In the absence of a dataset identified in the protocol request or  in
the query itself, the dataset used to match against a SPARQL query is
application-specific.  So, other than the graph API there isn't any
other immediately obvious place to identify the dataset.

> the fact that a query can call in other resources beyond the graph makes me
> sort of feel like a more explicit api would be something like this:

This is built into the SPARQL language.  Any use of ``FROM <..>``
*requires* that the 'default graph' is loaded with the RDF resolved
from the URI.

> from rdflib import sparql
>
> ... set up a list of graph and resource, etc
>
> sparql.query(myquery, data=list_of_graphs_or_resources,
> default_graphs='someid')

The data argument wouldn't make sense there since the dataset is
either determined already (if specified at the protocol), specified in
the SPARQL query itself, or it is application-specific (in which case
if it is evaluated against a CG, this is the RDF dataset, otherwise
it's a bit wonky and the compromise seems to be to assume an RDF
dataset with no named graphs and a single default graph consisting of
the object of the 'query' method).

The default_graph keyword would really only apply if the query is
called against a CG and you wanted to explicitly identify the BNode to
use as the identifier of the default graph (instead of using the
'first' one).  i.e::

    class ConjunctiveGraph(..)
      def query(self, query, default_graph=self.default_context,....):
        pass

> Otherwhise, it feels like we are conflating graphs and datasets or at least
> hiding the actual relationship (and leading to nasty surprises).

There is no conflation happening with graphs and datasets.  The
confusion is between the RDFLib API, the 'formal' definition of an RDF
dataset and the way for RDFLib to setup an 'application-specific'
RDF dataset (in the abcense of any indication of one).

> If my graph is ided as "http://myns/dataname";, I expect FROM to use that if
> my graph is ided "http://myns/dataname"; as it, not attempt to download some
> web resource (what currently happens).

The ``FROM`` operation is supposed to behave that way by definition:

"The FROM and FROM NAMED keywords allow a query to specify an RDF
dataset by reference; they indicate that the dataset should include
graphs that are obtained from representations of the resources
identified by the given IRIs"

By "representations of the resources .." they mean a HTTP dereference
- at least with ``FROM <...>``.  ``FROM NAMED`` is different.

> Sparql seems to default sensibly the graph the query dispatched from, 
> but not recognize the id of that default graph.

Here is the chain:

1. No FROM / FROM NAMED in SPARQL query
2. Does the protocol specify a URI which resolves to an RDF representation to
   use as the default graph?  No...
3. Use the application-specific default graph.  Either:
3a. The default_context of the CG the query was dispatched against
3b. The Graph in CG with the given BNode as its identifier
3c. The *first* Graph in CG with a BNode identifier (or en empty graph
    if there is none)
3d. Use the graph the query was dispatched against


-------------------------------------------------------------------------------
whit
Wed, 19 Sep 2007 14:32:03 -0700

ok... after lots of experiment I finally got some that worked for my usecase.

PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX annotea: <http://www.w3.org/2000/10/annotation-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?entry_uri
WHERE {

      {
        ?annotation annotea:related ?entry_uri .
        ?annotation annotea:body ?term_uri .
        ?term_uri rdfs:label ?term.filter(?term = 'test2')
      }
       UNION
      {
        ?annotation annotea:related ?entry_uri .
        ?annotation annotea:body ?term_uri .
        ?term_uri rdfs:label ?term.filter(?term = 'test3')
      }
}

Note, three unions does not work(same pattern but with another term in
the graph, 'term3'), which limit's the usefulness of this approach
(but this seems to be reparable bug):

    return graph.query(q).serialize(format='python')
  File "/Users/whit/dev/tagger/src/rdflib.plug/rdflib/Graph.py", line
690, in query
    processed_query = processor.query(strOrQuery, initBindings,
initNs, DEBUG, dataSetBase)
  File 
"/Users/whit/dev/tagger/src/rdflib.plug/rdflib/sparql/bison/Processor.py",
line 39, in query
    return 
TopEvaluate(strOrQuery,self.graph,initBindings,DEBUG=DEBUG,dataSetBase=dataSetBase)
  File "/Users/whit/dev/tagger/src/rdflib.plug/rdflib/sparql/Algebra.py",
line 341, in TopEvaluate
    topUnionBindings = result.parent1.top.returnResult(selectionF)+\
AttributeError: 'NoneType' object has no attribute 'returnResult'

Though it works (or could for more than 2), it seems unwieldy since it
requires replicating the entire query for each variation.  But every
case where two statements like so:

WHERE  {
      ?annotation annotea:related ?entry_uri .
      ?annotation annotea:body ?term_uri .
      ?term_uri rdfs:label ?term.filter(?term = 'test2')
      ?term_uri rdfs:label ?term.filter(?term = 'test3')
}

returned nothing (where ultimately there is a single entry_id that has
both terms).  It seems fundamentally limiting for sparql if this is
the correct behavior (though http://www.w3.org/TR/rdf-sparql-query/
lists UNION as the way to do alternatives)

sort of frustrating. in the old graphpattern way of querying, this was
fairly easy to do and it's a fairly common querying usecase.  Should
we be able to do this with sparql? and if not, what are we suppose to
use (and how do we get graphpattern and graph)?  Is there a way to
generate programmatic queries that makes more sense (currently I am
generating strings and feed them to graph.query)?

I've attached the rdf/xml of my data so others could look and see if
I'm missing something.

-w

<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:annotea="http://www.w3.org/2000/10/annotation-ns#";
   xmlns:foaf="http://xmlns.com/foaf/0.1/";
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#";
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#";
   xmlns:tagger="http://xmlns.openplans.org/tagger#";
>
  <rdf:Description rdf:about="http://annotation.openplans.org/entry/urn:uuid:60a76c80-d399-11d9-b91C-0003939e0af6";>
    <annotea:created rdf:datatype="http://www.w3.org/2001/XMLSchema#date";>2007-09-19 19:37:00.353979</annotea:created>
    <rdf:ID rdf:resource="urn:uuid:60a76c80-d399-11d9-b91C-0003939e0af6"/>
    <rdf:type rdf:resource="http://www.w3.org/2005/Atom/entry"/>
  </rdf:Description>
  <rdf:Description rdf:about="http://example.org/test3";>
    <rdfs:label>test3</rdfs:label>
    <tagger:hasScheme rdf:resource="http://example.org"/>
    <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/topic"/>
  </rdf:Description>
  <rdf:Description rdf:about="http://annotation.openplans.org/annotation/GiHeEEPV2";>
    <annotea:body rdf:resource="http://annotation.openplans.org/tag/test1"/>
    <annotea:annotates rdf:resource="http://example.org/ann-page.html"/>
    <rdf:type rdf:resource="http://www.w3.org/2000/10/annotation-ns#Annotation"/>
    <annotea:related rdf:resource="http://annotation.openplans.org/entry/urn:uuid:60a76c80-d399-11d9-b91C-0003939e0af6"/>
    <annotea:created rdf:datatype="http://www.w3.org/2001/XMLSchema#date";>2007-09-19 19:37:00.353979</annotea:created>
    <annotea:author rdf:resource="http://example.org/test-user.html"/>
  </rdf:Description>
  <rdf:Description rdf:about="http://annotation.openplans.org/tag/test1";>
    <rdfs:label>test1</rdfs:label>
    <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/topic"/>
  </rdf:Description>
  <rdf:Description rdf:about="http://annotation.openplans.org/tag/test2";>
    <rdfs:label>test2</rdfs:label>
    <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/topic"/>
  </rdf:Description>
  <rdf:Description rdf:about="http://annotation.openplans.org/annotation/GiHeEEPV3";>
    <annotea:body rdf:resource="http://annotation.openplans.org/tag/test2"/>
    <annotea:annotates rdf:resource="http://example.org/ann-page.html"/>
    <rdf:type rdf:resource="http://www.w3.org/2000/10/annotation-ns#Annotation"/>
    <annotea:related rdf:resource="http://annotation.openplans.org/entry/urn:uuid:60a76c80-d399-11d9-b91C-0003939e0af6"/>
    <annotea:created rdf:datatype="http://www.w3.org/2001/XMLSchema#date";>2007-09-19 19:37:00.353979</annotea:created>
    <annotea:author rdf:resource="http://example.org/test-user.html"/>
  </rdf:Description>
  <rdf:Description rdf:about="http://example.org/ann-page.html";>
    <rdf:type rdf:resource="http://www.w3.org/2005/Atom/link"/>
  </rdf:Description>
  <rdf:Description rdf:about="http://example.org/test-user.html";>
    <foaf:name>Test User</foaf:name>
    <foaf:mbox>[EMAIL PROTECTED]</foaf:mbox>
    <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>
  </rdf:Description>
  <rdf:Description rdf:about="http://annotation.openplans.org/annotation/GiHeEEPV4";>
    <annotea:body rdf:resource="http://example.org/test3"/>
    <annotea:annotates rdf:resource="http://example.org/ann-page.html"/>
    <rdf:type rdf:resource="http://www.w3.org/2000/10/annotation-ns#Annotation"/>
    <annotea:related rdf:resource="http://annotation.openplans.org/entry/urn:uuid:60a76c80-d399-11d9-b91C-0003939e0af6"/>
    <annotea:created rdf:datatype="http://www.w3.org/2001/XMLSchema#date";>2007-09-19 19:37:00.353979</annotea:created>
    <annotea:author rdf:resource="http://example.org/test-user.html"/>
  </rdf:Description>
</rdf:RDF>
"""

n3data = """\
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://goonmill.org/2007/skill.n3#> .

:Foo a rdfs:Class .

:bar a :Foo ."""

ask_query = """\
ASK { 
    <http://goonmill.org/2007/skill.n3#bar> \
        a \
        <http://goonmill.org/2007/skill.n3#Foo> 
}"""

alicecontext = URIRef("http://example.org/foaf/aliceFoaf")

alicegraph = """\
# Named graph: http://example.org/foaf/aliceFoaf
@prefix  foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix  rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix  rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .

_:a  foaf:name     "Alice" .
_:a  foaf:mbox     <mailto:alice@work.example> .
_:a  foaf:knows    _:b .

_:b  foaf:name     "Bob" .
_:b  foaf:mbox     <mailto:bob@work.example> .
_:b  foaf:nick     "Bobby" .
_:b  rdfs:seeAlso  <http://example.org/foaf/bobFoaf> . 
<http://example.org/foaf/bobFoaf>
     rdf:type      foaf:PersonalProfileDocument .
"""

bobcontext = URIRef("http://example.org/foaf/bobFoaf")
bobgraph = """\
# Named graph: http://example.org/foaf/bobFoaf
@prefix  foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix  rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix  rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .

_:z  foaf:mbox     <mailto:bob@work.example> .
_:z  rdfs:seeAlso  <http://example.org/foaf/bobFoaf> .
_:z  foaf:nick     "Robert" .

<http://example.org/foaf/bobFoaf>
     rdf:type      foaf:PersonalProfileDocument . """

alicebobselectquery = """\
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?src ?bobNick
FROM NAMED <http://example.org/foaf/aliceFoaf>
FROM NAMED <http://example.org/foaf/bobFoaf>
WHERE
  {
    GRAPH ?src
    { ?x foaf:mbox <mailto:bob@work.example> .
      ?x foaf:nick ?bobNick
    }
  }"""

alicebobaskquery = """\
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

ASK 
FROM NAMED <http://example.org/foaf/aliceFoaf>
FROM NAMED <http://example.org/foaf/bobFoaf>
  {
    ?x foaf:mbox <mailto:bob@work.example> .
    ?x foaf:nick Robert .
    }
  }"""


test4data = """\
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix : <tag:example.org,2007;stuff/> .

:a foaf:knows :b .
:a foaf:knows :c .
:a foaf:knows :d .

:b foaf:knows :a .
:b foaf:knows :c .

:c foaf:knows :a ."""

test4query = """\
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

select distinct ?person
where {
     ?person foaf:knows ?a .
     ?person foaf:knows ?b .
    filter (?a != ?b) .
}"""


class TestDAWG_DATASET_COMPLIANCE(unittest.TestCase):
    sparql = True

    def test1_ASK_when_DAWG_DATASET_COMPLIANCE_is_False(self):
        graph = Graph()
        graph.parse(data=n3data, format='n3')
        res = graph.query(ask_query)
        self.assert_(res.askAnswer == True, res.askAnswer)

    def test1_ASK_when_DAWG_DATASET_COMPLIANCE_is_True(self):
        raise SkipTest("known DAWG_DATATSET_COMPLIANCE SPARQL issue")
        graph = Graph()
        graph.parse(data=n3data, format='n3')
        res = graph.query(ask_query,dSCompliance=True)
        self.assert_(res.askAnswer == True, res.askAnswer)

    # def test2_ASK_when_DAWG_DATASET_COMPLIANCE_is_False(self):
    #     graph = Graph()
    #     graph.get_context(alicecontext).parse(data=alicegraph, format='n3')
    #     graph.get_context(bobcontext).parse(data=bobgraph, format='n3')
    #     res = graph.query(alicebobselectquery)
    #     assert len(res) == 2

    # def test2_ASK_when_DAWG_DATASET_COMPLIANCE_is_True(self):
    #     graph = Graph()
    #     graph.get_context(alicecontext).parse(data=alicegraph, format='n3')
    #     graph.get_context(bobcontext).parse(data=bobgraph, format='n3')
    #     res = graph.query(alicebobselectquery,dSCompliance=True)
    #     # for row in res:
    #     #     print("bob in %s is %s" % row)
    #     assert len(res) == 2

    # def test3_ASK_when_DAWG_DATASET_COMPLIANCE_is_False(self):
    #     graph = Graph()
    #     graph.get_context(alicecontext).parse(data=alicegraph, format='n3')
    #     graph.get_context(bobcontext).parse(data=bobgraph, format='n3')
    #     res = graph.query(alicebobselectquery)
    #     self.assert_(res.askAnswer == True)

    # def test3_ASK_when_DAWG_DATASET_COMPLIANCE_is_True(self):
    #     graph = Graph()
    #     graph.get_context(alicecontext).parse(data=alicegraph, format='n3')
    #     graph.get_context(bobcontext).parse(data=bobgraph, format='n3')
    #     res = graph.query(alicebobaskquery,dSCompliance=True)
    #     self.assert_(res.askAnswer == True)

    def test4_DAWG_DATASET_COMPLIANCE_is_False(self):
        graph = Graph()
        graph.parse(data=test4data, format='n3')
        res = graph.query(test4query)
        # print("json", res.serialize(format='json'))
        assert len(res) == 2

    def test4_DAWG_DATASET_COMPLIANCE_is_True(self):
        raise SkipTest("known DAWG_DATATSET_COMPLIANCE SPARQL issue")
        graph = Graph()
        graph.parse(data=test4data, format='n3')
        res = graph.query(test4query, dSCompliance=True)
        # print("json", res.serialize(format='json'))
        assert len(res) == 2

