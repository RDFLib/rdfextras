import rdflib
from rdflib import OWL
from rdflib import plugin
from rdflib import RDF
from rdflib import RDFS
from rdfextras import sparql2sql
# from rdfextras.sparql2sql import parser
from rdfextras.sparql2sql.Algebra import TopEvaluate
from rdfextras.sparql2sql.bison.Query import Prolog

plugin.register('sparql2sql', rdflib.query.Result,
                 'rdfextras.sparql2sql.QueryResult', 'SPARQLQueryResult')

def sparql_query(
                 queryString,
                 queryObj,
                 graph,
                 dataSetBase,
                 extensionFunctions,
                 initBindings={},
                 initNs={},
                 DEBUG=False):
    """
    The default 'native' SPARQL implementation is based on sparql-p's expansion trees
    layered on top of the read-only RDF APIs of the underlying store.
    """
    rt =   TopEvaluate(queryObj,
                       graph,
                       initBindings,
                       DEBUG=DEBUG,
                       dataSetBase=dataSetBase,
                       extensionFunctions=extensionFunctions)
    # return plugin.get('sparql2sql', rdflib.query.Result)(rt)
    return rt

class Processor(sparql2sql.Processor):
    def __init__(self, graph):
        self.graph = graph
        self.graph.store.sparql_query = sparql_query
                                 
    def query(
              self, 
              queryString,
              initBindings={}, 
              initNs={}, 
              DEBUG=False,
              PARSE_DEBUG=False,
              dataSetBase=None,
              extensionFunctions={},
              USE_PYPARSING=True,
              parsedQuery=None):
        initNs.update({u'rdfs':RDFS.uri, u'owl':OWL.uri, u'rdf':RDF.uri})
        assert isinstance(queryString, basestring), \
            "%s must be a string, it is %s" % (queryString, type(queryString))
        if parsedQuery is None:
            assert USE_PYPARSING,'C-based BisonGen SPARQL parser has been removed'
            parsedQuery = sparql2sql.parser.parse(queryString)
        if not parsedQuery.prolog:
                parsedQuery.prolog = Prolog(None, [])
                parsedQuery.prolog.prefixBindings.update(initNs)
        else:
            for prefix, nsInst in initNs.items():
                if prefix not in parsedQuery.prolog.prefixBindings:
                    parsedQuery.prolog.prefixBindings[prefix] = nsInst

        global prolog            
        prolog = parsedQuery.prolog
        
        return self.graph.store.sparql_query(queryString,
                                             parsedQuery,
                                             self.graph,
                                             dataSetBase,
                                             extensionFunctions,
                                             initBindings,
                                             initNs,DEBUG)

#Convenience
# from rdfextras.sparql2sql.bison.Processor import sparql_query
# from rdfextras.sparql2sql.bison.Processor import Processor
