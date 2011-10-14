BAD_SPARQL=\
"""
BASE <tag:chimezie@ogbuji.net,2007:exampleNS>.
SELECT ?s
WHERE { ?s ?p ?o }"""

def test_bad_sparql():
    from rdflib import Graph
    Graph().query(BAD_SPARQL)
test_bad_sparql.known_issue = True

"""
ERROR: test_sparql_parser_instability.test_bad_sparql
----------------------------------------------------------------------
Traceback (most recent call last):
  File "nose-1.1.2-py2.7.egg/nose/case.py", line 197, in runTest 
    self.test(*self.arg)
  File "test/test_sparql/test_sparql_parser_instability.py", line 9, in test_bad_sparql
    Graph().query(BAD_SPARQL)
  File "rdflib/graph.py", line 804, in query
    return result(processor.query(query_object, initBindings, initNs, **kwargs))
  File "rdfextras/sparql/processor.py", line 28, in query
    strOrQuery = rdfextras.sparql.parser.parse(strOrQuery)
  File "rdfextras/sparql/parser.py", line 774, in parse
    return Query.parseString(stuff)[0]
  File "pyparsing-1.5.6-py2.7.egg/pyparsing.py", line 1032, in parseString
    raise exc
ParseException: Expected "SELECT" (at char 46), (line:2, col:46)
"""

if __name__ == '__main__':
    test_bad_sparql()
