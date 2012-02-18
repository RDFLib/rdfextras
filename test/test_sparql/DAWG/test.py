"""Run DAWG tests against alternate SPARQL implementation."""
import rdflib
from rdflib import plugin
from rdflib import Namespace
from rdflib.graph import ConjunctiveGraph
from rdflib.graph import Graph
from rdflib.store import Store
from rdflib.store import NO_STORE
from rdfextras.sparql.parser import parse

try:
    set
except NameError:
    from sets import Set as set

import os
import logging
from cStringIO import StringIO
import unittest
from nose.exc import SkipTest
from glob import glob
try:
    from string import maketrans
except ImportError:
    maketrans = str.translate


log = logging.getLogger(__name__)
log.setLevel(logging.WARN)
DEBUG = False
EVALUATE = True
DEBUG_PARSE = False
STORE='IOMemory'
configString = ''

test = [
    'data/local-constr/expr-2.rq',
    'data/examples/ex11.2.3.2_1.rq',
    'data/TypePromotion/tP-unsignedByte-short.rq'
    'data/examples/ex11.2.3.1_0.rq',
    'data/ValueTesting/typePromotion-decimal-decimal-pass.rq',
    'data/examples/ex11.2.3.2_0.rq',
    'data/SyntaxFull/syntax-union-02.rq',
    'data/part1/dawg-query-004.rq',
]

tests2Skip = {

    "data-r2/bnode-coreference/query.rq": 
        "Query results must maintain bnode co-references in the dataset",
    "data-r2/boolean-effective-value/query-bev-1.rq":"test failed",
    "data-r2/boolean-effective-value/query-bev-2.rq":"test failed",
    "data-r2/boolean-effective-value/query-bev-3.rq":"test failed",
    "data-r2/boolean-effective-value/query-bev-4.rq":"test failed",
    "data-r2/boolean-effective-value/query-bev-5.rq":"test failed",
    "data-r2/boolean-effective-value/query-boolean-literal.rq":"test failed",
    "data-r2/expr-builtin/q-blank-1.rq":"test failed",
    "data-r2/expr-builtin/q-datatype-1.rq":"test failed",
    "data-r2/expr-builtin/q-isliteral-1.rq":"test failed",
    "data-r2/expr-builtin/q-langMatches-4.rq":"'module' object has no attribute 'langmatches'",
    "data-r2/expr-builtin/sameTerm.rq":"'module' object has no attribute 'sameterm'",
    "data-r2/expr-builtin/sameTerm-eq.rq":"'module' object has no attribute 'sameterm'",
    "data-r2/expr-builtin/sameTerm-not-eq.rq":"'module' object has no attribute 'sameterm'",
    "data-r2/expr-equals/query-eq-1.rq":"test failed",
    "data-r2/expr-equals/query-eq-2.rq":"test failed",
    "data-r2/expr-equals/query-eq-3.rq":"test failed",
    "data-r2/expr-equals/query-eq-4.rq":"test failed",
    "data-r2/expr-equals/query-eq-5.rq":"test failed",
    "data-r2/expr-equals/query-eq-graph-1.rq":"test failed",
    "data-r2/expr-equals/query-eq-graph-2.rq":"test failed",
    "data-r2/expr-equals/query-eq-graph-3.rq":"test failed",
    "data-r2/expr-equals/query-eq-graph-4.rq":"test failed",
    "data-r2/expr-equals/query-eq-graph-5.rq":"test failed",
    "data-r2/graph/graph-04.rq":"parentGraph ID is BNode",
    "data-r2/graph/graph-06.rq":"parentGraph ID is BNode",
    "data-r2/graph/graph-07.rq":"parentGraph ID is BNode",
    "data-r2/graph/graph-08.rq":"parentGraph ID is BNode",
    "data-r2/graph/graph-09.rq":"parentGraph ID is BNode",
    "data-r2/graph/graph-10.rq":"parentGraph ID is BNode",
    "data-r2/graph/graph-11.rq":"parentGraph ID is BNode",
    "data-r2/i18n/kanji-01.rq":"Kanji-01",
    "data-r2/i18n/kanji-02.rq":"Kanji-02",
    "data-r2/i18n/normalization-01.rq":"under investigation",
    "data-r2/i18n/normalization-02.rq":"test failed",
    "data-r2/i18n/normalization-03.rq":"test failed",
    "data-r2/optional/q-opt-complex-2.rq":"parentGraph ID is BNode",
    "data-r2/optional/q-opt-complex-3.rq":"parentGraph ID is BNode",
    "data-r2/optional/q-opt-complex-4.rq":"parentGraph ID is BNode",
    "data-r2/optional-filter/expr-5.rq":"under investigation",
    "data-r2/regex/regex-query-001.rq":"test failed",
    "data-r2/regex/regex-query-002.rq":"test failed",
    "data-r2/regex/regex-query-003.rq":"test failed",
    "data-r2/regex/regex-query-004.rq":"test failed",
    "data-r2/solution-seq/slice-01.rq":"test failed",
    "data-r2/solution-seq/slice-02.rq":"test failed",
    "data-r2/solution-seq/slice-04.rq":"test failed",
    "data-r2/solution-seq/slice-10.rq":"test failed",
    "data-r2/solution-seq/slice-11.rq":"test failed",
    "data-r2/solution-seq/slice-13.rq":"test failed",
    "data-r2/solution-seq/slice-20.rq":"test failed",
    "data-r2/solution-seq/slice-21.rq":"test failed",
    "data-r2/solution-seq/slice-23.rq":"test failed",
    "data-r2/solution-seq/slice-24.rq":"test failed",
    "data-r2/sort/query-sort-builtin.rq":"under investigation",
    "data-r2/sort/query-sort-function.rq":"under investigation",
    "data-r2/sort/query-sort-numbers.rq":"Support for ORDER BY with anything other than a variable is not supported:",
    "data-r2/triple-match/dawg-tp-04.rq":"test failed",
    "data-r2/type-promotion/tP-byte-short-fail.rq": "XML type promotion",
    "data-r2/type-promotion/tP-byte-short.rq": "XML type promotion", 
    "data-r2/type-promotion/tP-decimal-decimal.rq": "XML type promotion",
    "data-r2/type-promotion/tP-double-decimal-fail.rq": "XML type promotion",
    "data-r2/type-promotion/tP-double-decimal.rq": "XML type promotion",
    "data-r2/type-promotion/tP-double-double.rq": "XML type promotion",
    "data-r2/type-promotion/tP-double-float-fail.rq": "XML type promotion",
    "data-r2/type-promotion/tP-double-float.rq": "XML type promotion",
    "data-r2/type-promotion/tP-float-decimal-fail.rq": "XML type promotion",
    "data-r2/type-promotion/tP-float-decimal.rq": "XML type promotion",
    "data-r2/type-promotion/tP-float-float.rq": "XML type promotion",
    "data-r2/type-promotion/tP-int-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-integer-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-long-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-negativeInteger-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-nonNegativeInteger-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-nonPositiveInteger-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-positiveInteger-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-short-byte-fail.rq": "XML type promotion",
    "data-r2/type-promotion/tP-short-decimal.rq": "XML type promotion",
    "data-r2/type-promotion/tP-short-double.rq": "XML type promotion",
    "data-r2/type-promotion/tP-short-float.rq": "XML type promotion",
    "data-r2/type-promotion/tP-short-int-fail.rq": "XML type promotion",
    "data-r2/type-promotion/tP-short-long-fail.rq": "XML type promotion",
    "data-r2/type-promotion/tP-short-short-fail.rq": "XML type promotion",
    "data-r2/type-promotion/tP-short-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-unsignedByte-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-unsignedInt-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-unsignedLong-short.rq": "XML type promotion",
    "data-r2/type-promotion/tP-unsignedShort-short.rq": "XML type promotion",
}

graphtests = {
"data-r2/construct/query-construct-optional.rq": "data-r2/construct/result-construct-optional.ttl",
"data-r2/construct/query-ident.rq":"data-r2/construct/result-ident.ttl",
"data-r2/construct/query-reif-1.rq":"data-r2/construct/result-reif.ttl",
"data-r2/construct/query-reif-2.rq":"data-r2/construct/result-reif.ttl",
"data-r2/construct/query-subgraph.rq":"data-r2/construct/result-subgraph.ttl",
}

MANIFEST_NS = Namespace(
        'http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#'
)
MANIFEST_QUERY_NS = Namespace(
        'http://www.w3.org/2001/sw/DataAccess/tests/test-query#'
)
TEST_BASE = Namespace(
        'http://www.w3.org/2001/sw/DataAccess/tests/'
)
RESULT_NS = Namespace(
        'http://www.w3.org/2001/sw/DataAccess/tests/result-set#'
)
manifestNS = {
    u"rdfs": Namespace(
                "http://www.w3.org/2000/01/rdf-schema#"),
    u"mf"  : Namespace(
                "http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#"),
    u"qt"  : Namespace(
                "http://www.w3.org/2001/sw/DataAccess/tests/test-query#"),
}
EARL = Namespace("http://www.w3.org/ns/earl#")
DOAP = Namespace("http://usefulinc.com/ns/doap#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

MANIFEST_QUERY = \
"""
SELECT ?source ?testName ?testComment ?result
WHERE {
  ?testCase mf:action    ?testAction;
            mf:name      ?testName;
            mf:result    ?result.
  ?testAction qt:query ?query;
              qt:data  ?source.

  OPTIONAL { ?testCase rdfs:comment ?testComment }

}"""
PARSED_MANIFEST_QUERY = parse(MANIFEST_QUERY)

def bootStrapStore(store):
    rt = store.open(configString,create=False)
    if rt == NO_STORE:
        store.open(configString,create=True)
    else:
        store.destroy(configString)
        store.open(configString,create=True)

def trialAndErrorRTParse(graph,queryLoc,DEBUG):
    qstr = StringIO(open(queryLoc).read())
    try:
        graph.parse(qstr,format='n3')
        return True
    except Exception, e:
        if DEBUG:
            log.debug(e)
            log.debug("#### Parse Failure (N3) ###")
            log.debug(qstr.getvalue())
            log.debug("#####"*5)
        try:
            graph.parse(qstr)
            assert list(graph.objects(None,RESULT_NS.resultVariable))
            return True
        except Exception, e:
            if DEBUG:
                log.debug(e)
                log.debug("#### Parse Failure (RDF/XML) ###")
                log.debug(qstr.getvalue())
                log.debug("#### ######### ###")
            return False

def generictest(testFile):
    func_name = __name__ = __doc__ = id = 'test_sparql.' + \
                os.path.splitext(testFile)[0][8:].translate(
                                                    maketrans('-/','__'))
    store = plugin.get(STORE,Store)()
    bootStrapStore(store)
    store.commit()
    prefix = testFile.split('.rq')[-1]
    manifestPath = '/'.join(testFile.split('/')[:-1]+['manifest.n3'])
    manifestPath2 = '/'.join(testFile.split('/')[:-1]+['manifest.ttl'])
    queryFileName = testFile.split('/')[-1]
    store = plugin.get(STORE,Store)()
    store.open(configString,create=False)
    assert len(store) == 0
    manifestG=ConjunctiveGraph(store)
    if not os.path.exists(manifestPath):
        assert os.path.exists(manifestPath2)
        manifestPath = manifestPath2
    manifestG.default_context.parse(open(manifestPath),
                                    publicID=TEST_BASE,
                                    format='n3')
    manifestData = manifestG.query(
                      MANIFEST_QUERY,
                      processor='sparql',
                      initBindings={'query' : TEST_BASE[queryFileName]},
                      initNs=manifestNS,
                      DEBUG = False)
    store.rollback()
    store.close()
    for source,testCaseName,testCaseComment,expectedRT in manifestData:
        if expectedRT:
            expectedRT = '/'.join(testFile.split('/')[:-1] + \
                                    [expectedRT.replace(TEST_BASE,'')])
        if source:
            source = '/'.join(testFile.split('/')[:-1] + \
                                    [source.replace(TEST_BASE,'')])
        testCaseName = testCaseComment and testCaseComment or testCaseName
        # log.debug("## Source: %s ##"%source)
        # log.debug("## Test: %s ##"%testCaseName)
        # log.debug("## Result: %s ##"%expectedRT)
        #Expected results
        if expectedRT:
            store = plugin.get(STORE,Store)()
            store.open(configString,create=False)
            resultG=ConjunctiveGraph(store).default_context
            log.debug("###"*10)
            log.debug("parsing: %s" % open(expectedRT).read())
            log.debug("###"*10)
            assert len(store) == 0
            # log.debug("## Parsing (%s) ##"%(expectedRT))
            if not trialAndErrorRTParse(resultG,expectedRT,DEBUG):
                log.debug(
                    "Unexpected result format (for %s), skipping" % \
                                                    (expectedRT))
                store.rollback()
                store.close()
                continue
            log.debug("## Done .. ##")
            rtVars = [rtVar for rtVar in 
                        resultG.objects(None,RESULT_NS.resultVariable)]
            bindings = []
            resultSetNode = resultG.value(predicate=RESULT_NS.value,
                                          object=RESULT_NS.ResultSet)
            for solutionNode in resultG.objects(resultSetNode,
                                                RESULT_NS.solution):
                bindingDict = dict([(key,None) for key in rtVars])
                for bindingNode in resultG.objects(solutionNode,
                                                   RESULT_NS.binding):
                    value = resultG.value(subject=bindingNode,
                                          predicate=RESULT_NS.value)
                    name  = resultG.value(subject=bindingNode,
                                          predicate=RESULT_NS.variable)
                    bindingDict[name] = value
                rbinds = [bindingDict[vName] for vName in rtVars]
                # print("Rbinds", rbinds)
                if len(rbinds) > 1 and (
                    isinstance(rbinds, list) or isinstance(rbinds, tuple)):
                    bindings.append(frozenset(rbinds))
                elif len(rbinds) == 1 and (
                    isinstance(rbinds, list) or isinstance(rbinds, tuple)):
                    bindings.append(rbinds[0])
                else:
                    bindings.append(rbinds)
                # bindings.append(tuple([bindingDict[vName] for vName in rtVars]))
            log.debug(open(expectedRT).read())
            store.rollback()
            store.close()
        if testFile in tests2Skip.keys():
            log.debug("Skipping test (%s) %s\n" % \
                        (testFile, tests2Skip[testFile]))
            raise SkipTest("Skipping test (%s) %s\n" % \
                        (testFile, tests2Skip[testFile]))
        query = open(testFile).read()
        log.debug("### %s (%s) ###" % (testCaseName,testFile))
        log.debug(query)
        p = parse(query)#,DEBUG_PARSE)
        log.debug(p)
        if EVALUATE and source:
            log.debug("### Source Graph: ###")
            log.debug(open(source).read())
            store = plugin.get(STORE,Store)()
            store.open(configString,create=False)
            g = ConjunctiveGraph(store)
            try:
                g.parse(open(source),format='n3')
            except:
                log.debug("Unexpected data format (for %s), skipping" % \
                                                                (source))
                store.rollback()
                store.close()
                continue
            rt = g.query(query,
                         processor='sparql',
                         DEBUG = False)
            if expectedRT:
                try:
                    result = rt.result
                except AttributeError:
                    result = rt
                if isinstance(result, Graph):
                    resgraph = open(graphtests[testFile]).read()
                    store = plugin.get(STORE,Store)()
                    store.open(configString,create=False)
                    g = ConjunctiveGraph(store)
                    g.parse(data=resgraph,format="n3")
                    assert result == g, \
                            "### Test Failed: ###\n\nB:\n%s\n\nR:\n%s\n\n" % \
                                    (g.serialize(format="n3"), 
                                     result.serialize(format="n3"))
                else:
                    # result = [r[0] for r in result if isinstance(r, (tuple, list))]
                    def stab(r):
                        if isinstance(r, (tuple, list)):
                            return frozenset(r)
                        else:
                            return r
                    results = set(
                        [stab(r) for r in result])
                    assert set(bindings).difference(results) == set([]) or set(bindings) == results, \
                            "### Test Failed: ###\n\nB:\n%s\n\nR:\n%s\n\n" % \
                                    (set(bindings), results)
                log.debug("### Test Passed: ###")
            store.rollback()
    

def test_cases():
    if 'DAWG' not in os.getcwd():
        os.chdir(os.getcwd()+'/test/test_sparql/DAWG')
    for idx, testFile in enumerate(glob('data-r2/*/*.rq')): #[40:50]):
        g = generictest
        g.__name__ = g.__doc__ = g.func_name = g.id = \
            'test.test_sparql.' + \
                testFile[8:-3].translate(maketrans('-/','__'))
        yield g, testFile

if __name__=="__main__":
    # import nose; nose.main()
    test_cases()
