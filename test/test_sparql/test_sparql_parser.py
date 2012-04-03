import unittest
from rdflib import Graph

def buildQueryArgs(q):
    return dict(select="", where="", optional="")

class SPARQLParserTest(unittest.TestCase):
    known_issue = True

    def setUp(self):
        self.graph = Graph()
        pass

    def tearDown(self):
        pass

tests = [
    ("basic",
    """\
    SELECT ?name
    WHERE { ?a <http://xmlns.com/foaf/0.1/name> ?name }"""),
    ("simple_prefix",
    """\
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?name
    WHERE { ?a foaf:name ?name }"""),
    ("base_statement",
    """\
    BASE <http://xmlns.com/foaf/0.1/>
    SELECT ?name
    WHERE { ?a <name> ?name }"""),
    ("prefix_and_colon_only_prefix",
    """\
    PREFIX : <http://xmlns.com/foaf/0.1/>
    PREFIX vcard: <http://www.w3.org/2001/vcard-rdf/3.0#>
    SELECT ?name ?title
    WHERE {
        ?a :name ?name .
        ?a vcard:TITLE ?title
    }"""),
    ("predicate_object_list_notation",
    """\
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?name ?mbox
    WHERE {
        ?x  foaf:name  ?name ;
            foaf:mbox  ?mbox .
    }"""),
    ("object_list_notation",
    """\
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?x
    WHERE {
        ?x foaf:nick  "Alice" ,
                      "Alice_" .
    }
    """),
    ("escaped_literals",
    """\
    PREFIX tag: <http://xmlns.com/foaf/0.1/>
    PREFIX vcard: <http://www.w3.org/2001/vcard-rdf/3.0#>
    SELECT ?name
    WHERE {
        ?a tag:name ?name ;
           vcard:TITLE "escape test vcard:TITLE " ;
           <tag://test/escaping> "This is a ''' Test \"\"\"" ;
           <tag://test/escaping> ?d
    }
    """),
    ("key_word_as_variable",
    """\
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?PREFIX ?WHERE
    WHERE {
        ?x  foaf:name  ?PREFIX ;
            foaf:mbox  ?WHERE .
    }"""),
    ("key_word_as_prefix",
    """\
    PREFIX WHERE: <http://xmlns.com/foaf/0.1/>
    SELECT ?name ?mbox
    WHERE {
        ?x  WHERE:name  ?name ;
            WHERE:mbox  ?mbox .
    }"""),
    ("some_test_cases_from_grammar_py_1",
    """\
    SELECT ?title 
    WHERE { 
        <http://example.org/book/book1> 
        <http://purl.org/dc/elements/1.1/title> 
        ?title . 
    }"""),
    ("some_test_cases_from_grammar_py_2",
    """\
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?name ?mbox
    WHERE { ?person foaf:name ?name .
    OPTIONAL { ?person foaf:mbox ?mbox}
    }"""),
    ("some_test_cases_from_grammar_py_3",
    """\
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?name ?name2
    WHERE { ?person foaf:name ?name .
    OPTIONAL { ?person foaf:knows ?p2 . ?p2 foaf:name   ?name2 . }
    }"""),
    ("some_test_cases_from_grammar_py_4",
    """\
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    #PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?name ?mbox
    WHERE
    {
        { ?person rdf:type foaf:Person } .
        OPTIONAL { ?person foaf:name  ?name } .
        OPTIONAL {?person foaf:mbox  ?mbox} .
    }""")
]


def _buildQueryArg(q):
    res = buildQueryArgs(q)
    if res.get('select', False):
        assert res["select"] is not None
    if res.get('where', False):
        assert res["where"] is not None
    if res.get('optional', False):
        assert res["optional"] is not None
    # result = sparqlGr.query(select, where, optional)
        # self.assert_(self.graph.query(q) is not None)

