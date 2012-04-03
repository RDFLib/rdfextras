import unittest
from rdflib.graph import ConjunctiveGraph

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


