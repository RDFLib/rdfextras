try:
    from rdflib.graph import Graph
except ImportError:
    from rdflib.Graph import Graph
BAD_SPARQL=\
"""
BASE <tag:chimezie@ogbuji.net,2007:exampleNS>.
SELECT ?s
WHERE { ?s ?p ?o }"""

def test_bad_sparql():
    Graph().query(BAD_SPARQL,processor='sparql2sql')
test_bad_sparql.unstable = True

if __name__ == '__main__':
    test_bad_sparql()
