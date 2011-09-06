from test_context import ContextTestCase
from test_graph import GraphTestCase
from rdflib import plugin
from rdflib import store

plugin.register('Voldemort', store.Store,
                'rdfextras.store.Voldemort', 
                'VoldemortStore')

class VoldemortGraphTestCase(GraphTestCase):
    store_name = "Voldemort"
    storetest = True
    path = 'tcp://localhost:6666'


class VoldemortContextTestCase(ContextTestCase):
    store_name = "Voldemort"
    storetest = True
    path = 'tcp://localhost:6666'


