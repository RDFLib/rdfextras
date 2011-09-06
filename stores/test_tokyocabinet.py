import test_context
import test_graph
from rdflib import plugin
from rdflib import store

plugin.register('TokyoCabinet', store.Store,
                'rdfextras.store.TokyoCabinet', 
                'TokyoCabinet')

storetest = True
storename = "TokyoCabinet"

class TokyoCabinetGraphTestCase(test_graph.GraphTestCase):
    store_name = storename
    path = '/var/tmp/test'


class TokyoCabinetContextTestCase(test_context.ContextTestCase):
    store_name = storename
    path = '/var/tmp/test'


