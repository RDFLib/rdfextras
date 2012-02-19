from rdflib import plugin
from rdflib import store
from rdflib import query
#from .test_context import ContextTestCase
#from .test_graph import GraphTestCase

import sys # sop to Hudson
sys.path.insert(0, '/var/lib/tomcat6/webapps/hudson/jobs/rdfextras')

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

