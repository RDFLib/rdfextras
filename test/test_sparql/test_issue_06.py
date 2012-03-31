import unittest
from rdflib.graph import ConjunctiveGraph
from rdfextras.sparql import SPARQLError

"""
File ".../rdflib/graph.py", line 892, in query
  return result(processorinst.query(query_object, initBindings, initNs, **kwargs))
File ".../rdfextras/sparql/processor.py", line 45, in query
  extensionFunctions=extensionFunctions)
File ".../rdfextras/sparql/algebra.py", line 461, in TopEvaluate
  offset
File ".../rdfextras/sparql/query.py", line 1072, in select
  results = self._orderedSelect(selectionF,orderBy,orderAscend)
File ".../rdfextras/sparql/query.py", line 966, in _orderedSelect
  fullBinding = self._getFullBinding()
File ".../rdfextras/sparql/query.py", line 923, in _getFullBinding
  results = self.parent1.select(None) + self.parent2.select(None)
File ".../rdfextras/sparql/query.py", line 1062, in select
  selectionF = _variablesToArray(selection,"selection")
File ".../rdfextras/sparql/query.py", line 96, in _variablesToArray
  raise SPARQLError("'%s' argument must be a string, a Variable, or a list of those - got %s" % (name, repr(variables)))
rdfextras.sparql.SPARQLError: SPARQL Error: 'selection' argument must be a string, a Variable, or a list of those - got None.
"""

testgraph = """<rdf:RDF  xmlns:ex="http://temp.example.org/terms/"
    xmlns:loc="http://simile.mit.edu/2005/05/ontologies/location#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">

   <ex:Event rdf:about="http://temp.example.org/terms/Event#case0">
      <ex:date rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2007-12-31</ex:date>
      <loc:place rdf:resource="http://temp.example.org/terms/Place#case1_place" />
   </ex:Event>
   <ex:Event rdf:about="http://temp.example.org/terms/Event#case1">
      <ex:date rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-06</ex:date>
      <loc:place rdf:resource="http://temp.example.org/terms/Place#case1_place" />
   </ex:Event>
   <ex:Event rdf:about="http://temp.example.org/terms/Event#case2">
      <ex:starts rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-04</ex:starts>
      <ex:finishes rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-05</ex:finishes>
      <loc:place rdf:resource="http://temp.example.org/terms/Place#case2_place" />
   </ex:Event>
   <ex:Event rdf:about="http://temp.example.org/terms/Event#case3">
      <ex:starts rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-07</ex:starts>
      <ex:finishes rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-08</ex:finishes>
      <loc:place rdf:resource="http://temp.example.org/terms/Place#case4_place" />
   </ex:Event>
   <ex:Event rdf:about="http://temp.example.org/terms/Event#case4">
      <ex:starts rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-02</ex:starts>
      <ex:finishes rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-03</ex:finishes>
      <loc:place rdf:resource="http://temp.example.org/terms/Place#case3_place" />
   </ex:Event>
   <ex:Event rdf:about="http://temp.example.org/terms/Event#case5">
      <ex:starts rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-09</ex:starts>
      <ex:finishes rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-10</ex:finishes>
      <loc:place rdf:resource="http://temp.example.org/terms/Place#case5_place" />
   </ex:Event>
   <ex:Event rdf:about="http://temp.example.org/terms/Event#case6">
      <ex:starts rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-01</ex:starts>
      <ex:finishes rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2008-01-11</ex:finishes>
      <loc:place rdf:resource="http://temp.example.org/terms/Place#case6_place" />
   </ex:Event>
</rdf:RDF>"""

class TestIssue06(unittest.TestCase):
    debug = False
    sparql = True
    # known_issue = True    

    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(data=testgraph, publicID="testgraph")

    def test_issue_6(self):
        query = """
        PREFIX ex: <http://temp.example.org/terms/>
        PREFIX loc: <http://simile.mit.edu/2005/05/ontologies/location#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT *
        WHERE { 
            {?event ex:date ?date . 
            FILTER (xsd:date(?date) >= xsd:date("2007-12-31") && xsd:date(?date) <= xsd:date("2008-01-11"))}
            
            UNION 
            
            {?event ex:starts ?start; ex:finishes ?end . 
             FILTER (xsd:date(?start) >= xsd:date("2008-01-02") && xsd:date(?end) <= xsd:date("2008-01-10"))}
        }
        ORDER BY ?event
        """
        self.graph.query(query, DEBUG=False)


