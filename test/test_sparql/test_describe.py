import unittest

import rdflib

rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')


class TestDescribe(unittest.TestCase):

    def test_describe(self): 
        g=rdflib.Graph()
        g.add((rdflib.URIRef("urn:a"),
               rdflib.URIRef("urn:b"),
               rdflib.URIRef("urn:c")))

        res=g.query("DESCRIBE <urn:a>")
        
        self.assertEqual(len(res), 1)
        
    test_describe.known_issue = True

"""
ERROR: test_describe (test_describe.TestDescribe)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_sparql/test_describe.py", line 19, in test_describe
    res=g.query("DESCRIBE <urn:a>")
  File "rdflib/graph.py", line 804, in query
    return result(processor.query(query_object, initBindings, initNs, **kwargs))
  File "rdfextras/sparql/processor.py", line 45, in query
    extensionFunctions=extensionFunctions)
  File "rdfextras/sparql/algebra.py", line 322, in TopEvaluate
    expr = reduce(ReduceToAlgebra,query.query.whereClause.parsedGraphPattern.graphPatterns,
 AttributeError: 'NoneType' object has no attribute 'parsedGraphPattern'
"""        

if __name__ == '__main__':
    unittest.main()
