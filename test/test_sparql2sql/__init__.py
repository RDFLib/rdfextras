import rdflib
from rdflib import plugin

plugin.register(
    'sparql2sql', rdflib.query.Processor,
    # 'rdfextras.sparql2sql.bison.Processor', 
    'rdfextras.sparql2sql.processor', 
    'Processor')

plugin.register(
    'sparql', rdflib.query.Processor,
    # 'rdfextras.sparql2sql.bison.Processor', 
    'rdfextras.sparql2sql.processor', 
    'Processor')

plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql2sql.QueryResult', 'SPARQLQueryResult')

rdflib.plugin.register(
    'xml', rdflib.query.ResultSerializer, 
    'rdfextras.sparql2sql.QueryResult','SPARQLQueryResult')

rdflib.plugin.register(
    'json', rdflib.query.ResultSerializer, 
    'rdfextras.sparql2sql.QueryResult','SPARQLQueryResult')
