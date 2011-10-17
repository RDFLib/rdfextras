try:
    import kyotocabinet
except ImportError:
    from nose.exc import SkipTest
    raise SkipTest("KyotoCabinet not installed")

import test_context
import test_graph
from rdflib import plugin
from rdflib import store
from test_n3_2 import testN3Store

storename = "KyotoCabinet"
storetest = True
configString = "/var/tmp/test"

plugin.register(storename, store.Store,
                'rdfextras.store.KyotoCabinet', 
                'KyotoCabinet')

class KyotoCabinetGraphTestCase(test_graph.GraphTestCase):
    store_name = storename
    path = configString
    storetest = True

class KyotoCabinetContextTestCase(test_context.ContextTestCase):
    store_name = storename
    path = configString
    storetest = True

testN3Store(storename, configString)

