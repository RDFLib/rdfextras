import rdflib
from rdflib import plugin

plugin.register('sparql2sql', rdflib.query.Processor,
                    'rdfextras.sparql2sql.bison.Processor', 'Processor')
plugin.register('sparql', rdflib.query.Result,
                    'rdfextras.sparql2sql.QueryResult', 'SPARQLQueryResult')

