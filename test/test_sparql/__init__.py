import rdflib
from rdflib import plugin

plugin.register('sparql', rdflib.query.Processor,
                    'rdfextras.sparql.processor', 'Processor')
plugin.register('sparql', rdflib.query.Result,
                    'rdfextras.sparql.query', 'SPARQLQueryResult')
