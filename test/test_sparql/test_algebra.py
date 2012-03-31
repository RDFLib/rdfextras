import unittest
from rdflib import plugin, Graph, URIRef
from rdflib.graph import ReadOnlyGraphAggregate
from rdflib.store import Store
from rdfextras.sparql.components import Prolog
from rdfextras.sparql.algebra import ReduceToAlgebra, TopEvaluate, GraphExpression

TEST1="BASE <http://example.com/> SELECT * WHERE { ?s :p1 ?v1 ; :p2 ?v2 }"
#BGP( ?s :p1 ?v1 .?s :p2 ?v2 )
TEST1_REPR=\
"BGP((?s,http://example.com/p1,?v1),(?s,http://example.com/p2,?v2))"

TEST2 = "BASE <http://example.com/> SELECT * WHERE { { ?s :p1 ?v1 } UNION {?s :p2 ?v2 } }"
#Union( BGP(?s :p1 ?v1) , BGP(?s :p2 ?v2) )
TEST2_REPR=\
"Union(BGP((?s,http://example.com/p1,?v1)),BGP((?s,http://example.com/p2,?v2)))"

TEST3 = "BASE <http://example.com/> SELECT * WHERE { ?s :p1 ?v1 OPTIONAL {?s :p2 ?v2 } }"
#LeftJoin(BGP(?s :p1 ?v1), BGP(?s :p2 ?v2), true)
TEST3_REPR=\
"LeftJoin(BGP((?s,http://example.com/p1,?v1)),BGP((?s,http://example.com/p2,?v2)))"

TEST4 = "BASE <http://example.com/> SELECT * WHERE { ?s :p ?o. { ?s :p1 ?v1 } UNION {?s :p2 ?v2 } }"
#Join(BGP(?s :p ?v),Union(BGP(?s :p1 ?v1), BGP(?s :p2 ?v2)))
TEST4_REPR=\
"Join(BGP((?s,http://example.com/p,?o)),Union(BGP((?s,http://example.com/p1,?v1)),BGP((?s,http://example.com/p2,?v2))))"

TEST5 = "BASE <http://example.com/> SELECT * WHERE { ?a ?b ?c OPTIONAL { ?s :p1 ?v1 } }"
#Join(BGP(?s :p ?v),Union(BGP(?s :p1 ?v1), BGP(?s :p2 ?v2)))
TEST5_REPR=\
"LeftJoin(BGP((?a,?b,?c)),BGP((?s,http://example.com/p1,?v1)))"

TEST6="BASE <http://example.com/> SELECT * WHERE { ?a :b :c OPTIONAL {:x :y :z} { :x1 :y1 :z1 } UNION { :x2 :y2 :z2 } }"
TEST6_REPR=\
"Join(LeftJoin(BGP((?a,http://example.com/b,http://example.com/c)),BGP((http://example.com/x,http://example.com/y,http://example.com/z))),Union(BGP((http://example.com/x1,http://example.com/y1,http://example.com/z1)),BGP((http://example.com/x2,http://example.com/y2,http://example.com/z2))))"

TEST7="BASE <http://example.com/> SELECT * WHERE { ?s :p1 ?v1 OPTIONAL { ?s :p2 ?v2. FILTER( ?v1 < 3 ) } }"
TEST7_REPR=\
"LeftJoin(BGP((?s,http://example.com/p1,?v1)),Filter(.. a filter ..,BGP(?s,http://example.com/p2,?v2)))"

TEST8="BASE <http://example.com/> SELECT * WHERE { ?s :p1 ?v1. FILTER ( ?v1 < 3 ) OPTIONAL { ?s :p3 ?v3 } }"
TEST8_REPR=\
"LeftJoin(Filter(.. a filter ..,BGP(?s,http://example.com/p1,?v1)),BGP((?s,http://example.com/p3,?v3)))"

TEST10=\
"""
PREFIX  data:  <http://example.org/foaf/>
PREFIX  foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX  rdfs:  <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?mbox ?nick ?ppd
FROM NAMED <http://example.org/foaf/aliceFoaf>
FROM NAMED <http://example.org/foaf/bobFoaf>
WHERE
{
  GRAPH data:aliceFoaf
  {
    ?alice foaf:mbox <mailto:alice@work.example> ;
           foaf:knows ?whom .
    ?whom  foaf:mbox ?mbox ;
           rdfs:seeAlso ?ppd .
    ?ppd  a foaf:PersonalProfileDocument .
  } .
  GRAPH ?ppd
  {
      ?w foaf:mbox ?mbox ;
         foaf:nick ?nick
  }
}"""

reducableSPARQL=\
"""
PREFIX mf: <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#>
PREFIX qt: <http://www.w3.org/2001/sw/DataAccess/tests/test-query#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?test ?testName ?testComment ?query ?result ?testAction
WHERE {
    { ?test a mf:QueryEvaluationTest }
      UNION
    { ?test a <http://jena.hpl.hp.com/2005/05/test-manifest-extra#TestQuery> }
    ?test mf:name   ?testName.
    OPTIONAL { ?test rdfs:comment ?testComment }
    ?test mf:action    ?testAction;
          mf:result ?result.
    ?testAction qt:query ?query }"""
    
reducableSPARQLExpr=\
"Join(LeftJoin(Join(Union(BGP((?test,http://www.w3.org/1999/02/22-rdf-syntax-ns#type,mf:QueryEvaluationTest)),BGP((?test,http://www.w3.org/1999/02/22-rdf-syntax-ns#type,http://jena.hpl.hp.com/2005/05/test-manifest-extra#TestQuery))),BGP((?test,mf:name,?testName))),BGP((?test,rdfs:comment,?testComment))),BGP((?test,mf:action,?testAction),(?test,mf:result,?result),(?testAction,qt:query,?query)))"    

ExprTests = \
[
    (TEST1,TEST1_REPR),
    (TEST2,TEST2_REPR),
    (TEST3,TEST3_REPR),
    (TEST4,TEST4_REPR),
    (TEST5,TEST5_REPR),
    (TEST6,TEST6_REPR),
    (TEST7,TEST7_REPR),
    (TEST8,TEST8_REPR),
    (reducableSPARQL,reducableSPARQLExpr),    
]

test_graph_a = """
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
     rdf:type      foaf:PersonalProfileDocument ."""
     
test_graph_b = """
@prefix  foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix  rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix  rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .

_:z  foaf:mbox     <mailto:bob@work.example> .
_:z  rdfs:seeAlso  <http://example.org/foaf/bobFoaf> .
_:z  foaf:nick     "Robert" .

<http://example.org/foaf/bobFoaf>
     rdf:type      foaf:PersonalProfileDocument ."""     
     
scopingQuery=\
"""
PREFIX  data:  <http://example.org/foaf/>
PREFIX  foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX  rdfs:  <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?ppd
FROM NAMED <http://example.org/foaf/aliceFoaf>
FROM NAMED <http://example.org/foaf/bobFoaf>
WHERE
{
  GRAPH ?ppd { ?b foaf:name "Bob" . } .
  GRAPH ?ppd { ?doc a foaf:PersonalProfileDocument . }
}"""     

class TestSPARQLAlgebra(unittest.TestCase):
    sparql = True
    known_issue = True
    
    def setUp(self):
        self.store = plugin.get('IOMemory', Store)()
        self.graph1 = Graph(self.store,identifier=URIRef('http://example.org/foaf/aliceFoaf'))
        self.graph1.parse(data=test_graph_a, format="n3")
        self.graph2 = Graph(self.store,identifier=URIRef('http://example.org/foaf/bobFoaf'))
        self.graph2.parse(data=test_graph_b, format="n3")
        self.unionGraph = ReadOnlyGraphAggregate(graphs=[self.graph1,self.graph2],store=self.store)
        
    def testScoping(self):
        from rdfextras.sparql.parser import parse
        from rdfextras.sparql.query import SPARQLQueryResult
        p = parse(scopingQuery)
        global prolog
        prolog = p.prolog
        if prolog is None:
            prolog = Prolog(u'',[])
            prolog.DEBUG = True
        rt = TopEvaluate(p,self.unionGraph,passedBindings = {},DEBUG=False)
        rt = SPARQLQueryResult(rt).serialize()#format='python')
        # print("Len rt", len(rt))
        self.failUnless(len(rt) == 1,"Expected 1 item solution set")
        for ppd in rt:
            self.failUnless(ppd == URIRef('http://example.org/foaf/aliceFoaf'),
                            "Unexpected ?mbox binding :\n %s" % ppd)

    def testExpressions(self):
        from rdfextras.sparql.parser import parse
        global prolog
        for inExpr,outExpr in ExprTests:
            p = parse(inExpr)
            prolog = p.prolog
            p = p.query.whereClause.parsedGraphPattern.graphPatterns
            if prolog is None:
                prolog = Prolog(u'',[])
            if not hasattr(prolog,'DEBUG'):                
                prolog.DEBUG = False
            self.assertEquals(repr(reduce(ReduceToAlgebra,p,None)),outExpr)

    def testSimpleGraphPattern(self):
        from rdfextras.sparql.parser import parse
        global prolog
        p = parse("BASE <http://example.com/> SELECT ?ptrec WHERE { GRAPH ?ptrec { ?data :foo 'bar'. } }")
        prolog = p.prolog
        p = p.query.whereClause.parsedGraphPattern.graphPatterns
        if prolog is None:
            prolog = Prolog(u'',[])
            prolog.DEBUG = True
        assert isinstance(reduce(ReduceToAlgebra,p,None),GraphExpression)

    def testGraphEvaluation(self):
        from rdflib import Literal
        from rdfextras.sparql.parser import parse
        p = parse(TEST10)
        # print TEST10
        rt = TopEvaluate(p,self.unionGraph,passedBindings = {})
        from rdfextras.sparql.query import SPARQLQueryResult
        rt = SPARQLQueryResult(rt).serialize()#format='python')
        # print("Len rt", len(rt))
        self.failUnless(len(rt) == 1,"Expected 1 item solution set")
        for mbox,nick,ppd in rt:
            self.failUnless(mbox == URIRef('mailto:bob@work.example'),
                            "Unexpected ?mbox binding :\n %s" % mbox)
            self.failUnless(nick  == Literal("Robert"),
                            "Unexpected ?nick binding :\n %s" % nick)
            self.failUnless(ppd == URIRef('http://example.org/foaf/bobFoaf'),
                            "Unexpected ?ppd binding :\n %s" % ppd)
