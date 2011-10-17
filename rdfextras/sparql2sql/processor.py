from rdfextras import sparql2sql
# from rdfextras.sparql2sql import parser
import parser
from Algebra import TopEvaluate
from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdfextras.sparql2sql.bison.Query import Prolog
from rdfextras.sparql2sql.bison.Query import Query

class Processor(sparql2sql.Processor):

    def __init__(self, graph):
        self.graph = graph

    def query(self, 
              strOrQuery, 
              initBindings={}, 
              initNs={}, 
              DEBUG=False,
              PARSE_DEBUG=False,
              dataSetBase=None,
              extensionFunctions={},
              USE_PYPARSING=False):

        initNs.update({u'rdfs':RDFS.uri, u'owl':OWL.uri, u'rdf':RDF.uri}) 

        assert isinstance(strOrQuery, (basestring, Query)), \
        "%s must be a string or an rdfextras.sparql2sql.Query.Query instance" % \
        strOrQuery
        if isinstance(strOrQuery, basestring):
            strOrQuery = sparql2sql.parser.parse(strOrQuery)
        if not strOrQuery.prolog:
            strOrQuery.prolog = Prolog(None, [])
            strOrQuery.prolog.prefixBindings.update(initNs)
        else:
            for prefix, nsInst in initNs.items():
                if prefix not in strOrQuery.prolog.prefixBindings:
                    strOrQuery.prolog.prefixBindings[prefix] = nsInst
                    
        global prolog            
        prolog = strOrQuery.prolog

        return TopEvaluate(strOrQuery,
                           self.graph,
                           initBindings,
                           DEBUG=DEBUG,
                           dataSetBase=dataSetBase,
                           extensionFunctions=extensionFunctions)

# Convenience
# from rdfextras.sparql2sql.processor import Processor
