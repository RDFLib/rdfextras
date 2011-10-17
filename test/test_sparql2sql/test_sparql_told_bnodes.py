from rdflib import Variable, RDF, RDFS
from rdflib.store import Store
from rdflib import plugin
from rdflib.parser import StringInputSource
from rdflib.graph import Graph
import unittest

global store,debug

"""
This test is actually completely broken 
SPARQL defines bnode IDs in queries to be distinct from all other bnodes, 
i.e. using bnode IDs in filter expressions like done here is not meant to work

Note: the presence of a BNode in the SPARQL FILTER query in 
testToldBNodeWithBinding would seem to trigger a ParseException:

ParseException: Expected "}" (at char 44), (line:1, col:45)
-------------------- >> begin captured stdout << ---------------------
SELECT ?subj WHERE { { ?subj ?prop ?obj } . FILTER ( ?subj != _:ub81bL5C12 ) }

char 44:                                  ^
"""


class TestSPARQLToldBNodes(unittest.TestCase):

    known_issue=True
    sparql = True
    debug = False
    
    def setUp(self):
        # NS = u"http://example.org/"
        self.graph = Graph("IOMemory")
        self.graph.parse(StringInputSource("""
           @prefix    : <http://example.org/> .
           @prefix rdf: <%s> .
           @prefix rdfs: <%s> .
           [ :prop :val ].
           [ a rdfs:Class ]."""%(RDF, RDFS)), format="n3")
        # print(self.graph.serialize(format="nt"))
    
    def testToldBNode(self):
        for s,p,o in self.graph.triples((None,RDF.type,None)):
            pass
        query = """SELECT ?obj WHERE { %s ?prop ?obj }""" % s.n3()
        # print(query)
        rt = self.graph.query(
            query, processor="sparql2sql",
            DEBUG=self.debug).result
        self.failUnless(
            len(rt) == 1,"BGP should only match the 'told' BNode by name")
    
    def testToldBNodeWithBinding(self):
        for s,p,o in self.graph.triples((None,RDF.type,None)):
            pass
        query = """SELECT ?obj WHERE { ?subj ?prop ?obj }"""
        bindings = {Variable('subj'):s}
        # print(query)
        rt = self.graph.query(
            query, processor="sparql2sql", 
            initBindings=bindings, DEBUG=self.debug).result
        self.failUnless(
            len(rt) == 1,"BGP should only match the 'told' BNode by name")
    
    def testFilterBNode(self):
        for s,p,o in self.graph.triples((None,RDF.type,None)):
            pass        
        query = """\
        SELECT ?subj WHERE { { ?subj ?prop ?obj } . FILTER ( ?subj != %s ) }
        """ % s.n3()
        print(query.strip())
        rt = self.graph.query(
            query.strip(), processor="sparql2sql", 
            DEBUG=self.debug).result
        print("rt", rt)
        self.failUnless(
            len(rt) == 1,"FILTER should exclude 'told' BNodes by name")
    
    def tearDown(self):
        self.graph.store.rollback()
    

if __name__ == '__main__':
    # import doctest
    from optparse import OptionParser
    usage = '''usage: %prog [options]'''
    op = OptionParser(usage=usage)
    op.add_option('-s','--storeKind',default="IOMemory",
      help="The (class) name of the store to use for persistence")
      
    op.add_option('-c','--config',default='',
      help="Configuration string to use for connecting to persistence store")
      
    op.add_option('-i','--identifier',default='',
      help="Store identifier")
    
    op.add_option('-d','--debug',action="store_true",default=False,
      help="Debug flag")
      
    (options, args) = op.parse_args()
    
    debug = options.debug
    store = plugin.get(options.storeKind,Store)(options.identifier)
    store.open(options.config,create=False)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSPARQLToldBNodes)
    unittest.TextTestRunner(verbosity=2).run(suite)    
