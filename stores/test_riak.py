import test_context
import test_graph
from rdflib import plugin
from rdflib import store

plugin.register('Riak', store.Store,
                'rdfextras.store.riak', 
                'RiakStore')

class RiakGraphTestCase(test_graph.GraphTestCase):
    store_name = "Riak"
    storetest = True
    path = ''


class RiakContextTestCase(test_context.ContextTestCase):
    store_name = "Riak"
    storetest = True
    path = ''


