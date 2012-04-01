
import rdfextras.sparql.parser

from rdfextras.sparql.algebra import TopEvaluate
from rdflib import RDFS, RDF, OWL
from rdflib.query import Processor
from rdfextras.sparql.components import Query, Prolog

class Processor(Processor):

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
              USE_PYPARSING=False,
              dSCompliance=False,
              loadContexts=False):

        initNs.update({u'rdfs':RDFS.uri, u'owl':str(OWL), u'rdf':RDF.uri})

        assert isinstance(strOrQuery, (basestring, Query)),"%s must be a string or an rdfextras.sparql.components.Query instance"%strOrQuery

        if isinstance(strOrQuery, basestring):
            strOrQuery = rdfextras.sparql.parser.parse(strOrQuery)

        if not strOrQuery.prolog:
            strOrQuery.prolog = Prolog(None, [])
            strOrQuery.prolog.prefixBindings.update(initNs)

        else:
            for prefix, nsInst in initNs.items():
                if prefix not in strOrQuery.prolog.prefixBindings:
                    strOrQuery.prolog.prefixBindings[prefix] = nsInst

        return TopEvaluate(strOrQuery,
                           self.graph,
                           initBindings,
                           DEBUG=DEBUG,
                           dataSetBase=dataSetBase,
                           extensionFunctions=extensionFunctions,
                           dSCompliance=dSCompliance,
                           loadContexts=loadContexts)
