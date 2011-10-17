from rdflib import plugin
from rdflib import store
from rdflib import query
#from .test_context import ContextTestCase
#from .test_graph import GraphTestCase

plugin.register(
        'sparql', query.Processor,
        'rdfextras.sparql.processor', 'Processor')

plugin.register(
        'sparql', query.Result,
        'rdfextras.sparql.query', 'SPARQLQueryResult')

plugin.register(
        'BerkeleyDB', store.Store,
        'rdfextras.store.BerkeleyDB', 'BerkeleyDB')

plugin.register(
        'BDBOptimized', store.Store,
        'rdfextras.store.BDBOptimized', 'BDBOptimized')

plugin.register(
        'MySQL', store.Store,
        'rdfextras.store.MySQL', 'MySQL')

plugin.register(
        'PostgreSQL', store.Store,
        'rdfextras.store.PostgreSQL', 'PostgreSQL')

plugin.register(
        'SPARQL', store.Store,
        'rdfextras.store.SPARQL', 'SPARQLStore')

plugin.register(
        'SQLite', store.Store,
        'rdfextras.store.SQLite', 'SQLite')

plugin.register(
        'ZODB', store.Store,
        'rdfextras.store.ZODB', 'ZODBGraph')

plugin.register(
        'KyotoCabinet', store.Store,
        'rdfextras.store.KyotoCabinet', 'KyotoCabinet')

# SQLObject schemes
# scheme://[user[:password]@]host[:port]/database[?parameters]
# Scheme is one of: sqlite, mysql, postgres, firebird,
# interbase, maxdb, sapdb, mssql, sybase.
# connections = dict(
#     sqlite = 'sqlite:///%s/sqlobject.sqlite' % os.getcwd(),
#     sqlitemem = 'sqlite:///:memory:',
#     postgres = 'postgres://localhost/sqlobject_rdflib',
#     firebird = 'firebird://user:password@localhost//path/to/rdflib',
#     mysql = 'mysql://user:password@localhost/sqlobject_rdflib',
#     psycopg = 'psycopg://user:password@localhost/sqlobject_rdflib')

