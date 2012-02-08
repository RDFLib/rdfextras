from rdflib.graph import ConjunctiveGraph
from StringIO import StringIO
import unittest

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')


rdflib.plugin.register('json', rdflib.query.ResultParser, 'rdfextras.sparql.results.jsonresults','JSONResultParser')
rdflib.plugin.register('json', rdflib.query.ResultSerializer, 'rdfextras.sparql.results.jsonresults','JSONResultSerializer')
from rdflib.py3compat import b

# json is only available as of python2.6, but simplejson is available 
# via PyPI for older pythons
try:
    import json
except ImportError: 
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("unable to find json or simplejson modules")

test_data = """
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://example.org/alice> a foaf:Person;
    foaf:name "Alice";
    foaf:knows <http://example.org/bob> .

<http://example.org/bob> a foaf:Person;
    foaf:name "Bob" .
"""


PROLOGUE = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
"""


test_material = {}

test_material['optional'] = (PROLOGUE+"""
    SELECT ?name ?x ?friend
    WHERE { ?x foaf:name ?name .
            OPTIONAL { ?x foaf:knows ?friend . }
    }
    """,
    {u'head': {u'vars': [u'name', u'x', u'friend']}, u'results': { u'bindings': [{u'x': {u'type': u'uri', u'value': u'http://example.org/alice'}, u'name': { u'type': u'literal', u'value': u'Alice'}, u'friend': {u'type': u'uri', u'value': u'http://example.org/bob'}}, {u'x': {u'type': u'uri', u'value': u'http://example.org/bob'}, u'name': { u'type': u'literal', u'value': u'Bob'}}], }} 
    )

test_material['select_vars'] = (PROLOGUE+"""
    SELECT ?name ?friend
    WHERE { ?x foaf:name ?name .
            OPTIONAL { ?x foaf:knows ?friend . }
    }""",
    {u'head': {u'vars': [u'name', u'friend']}, u'results': { u'bindings': [{u'name': { u'type': u'literal', u'value': u'Bob'}}, {u'name': { u'type': u'literal', u'value': u'Alice'}, u'friend': {u'type': u'uri', u'value': u'http://example.org/bob'}}], }} 
    )

test_material['wildcard'] = (PROLOGUE+"""
    SELECT * WHERE { ?x foaf:name ?name . }
    """,
    {u'head': {u'vars': [u'x', u'name']}, u'results': { u'bindings': [{u'x': {u'type': u'uri', u'value': u'http://example.org/bob'}, u'name': { u'type': u'literal', u'value': u'Bob'}}, {u'x': {u'type': u'uri', u'value': u'http://example.org/alice'}, u'name': { u'type': u'literal', u'value': u'Alice'}}], }} 
    )

test_material['wildcard_vars'] = (PROLOGUE+"""
    SELECT * WHERE { ?x foaf:name ?name . }
    """,
    {u'head': {u'vars': [u'x', u'name']}, u'results': { u'bindings': [{u'x': {u'type': u'uri', u'value': u'http://example.org/alice'}, u'name': { u'type': u'literal', u'value': u'Alice'}}, {u'x': {u'type': u'uri', u'value': u'http://example.org/bob'}, u'name': { u'type': u'literal', u'value': u'Bob'}}], }} 
    )

test_material['union'] = (PROLOGUE+"""
    SELECT DISTINCT ?name WHERE {
                { <http://example.org/alice> foaf:name ?name . } UNION { <http://example.org/bob> foaf:name ?name . }
    }
    """,
    {u'head': {u'vars': [u'name']}, u'results': { u'bindings': [{u'name': { u'type': u'literal', u'value': u'Bob'}}, {u'name': { u'type': u'literal', u'value': u'Alice'}}], }} 
    )

test_material['union3'] = (PROLOGUE+"""
    SELECT DISTINCT ?name WHERE {
                { <http://example.org/alice> foaf:name ?name . }
                UNION { <http://example.org/bob> foaf:name ?name . }
                UNION { <http://example.org/nobody> foaf:name ?name . }
    }
            """, 
    {u'head': {u'vars': [u'name']}, u'results': { u'bindings': [{u'name': { u'type': u'literal', u'value': u'Bob'}}, {u'name': { u'type': u'literal', u'value': u'Alice'}}], }}
    )


def make_method(testname):
    def test(self):
        query, correct = test_material[testname]
        self._query_result_contains(query, correct)
    test.__name__ = 'test%s' % testname.title()
    return test


class TestSparqlJsonResults(unittest.TestCase):

    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data), format="n3")

    def _query_result_contains(self, query, correct):
        results = self.graph.query(query)
        result_json = json.loads(results.serialize(format='json').decode('utf-8'))

        msg = "Expected:\n %s \n- to contain:\n%s" % (result_json, correct)
        self.assertEqual(result_json["head"], correct["head"], msg)

        # Sort by repr - rather a hack, but currently the best way I can think
        # of to ensure the results are in the same order.
        result_bindings = sorted(result_json["results"]["bindings"], key=repr)
        correct_bindings = sorted(correct["results"]["bindings"], key=repr)
        msg = "Expected:\n %s \n- to contain:\n%s" % (result_bindings, correct_bindings)
        self.failUnless(result_bindings==correct_bindings, msg)

    testOptional = make_method('optional')

    testWildcard = make_method('wildcard')

    testUnion = make_method('union')

    testUnion3 = make_method('union3')

    testSelectVars = make_method('select_vars')
    
    testWildcardVars = make_method('wildcard_vars')
    
if __name__ == "__main__":
    unittest.main()

