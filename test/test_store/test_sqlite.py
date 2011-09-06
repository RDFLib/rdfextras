import logging

_logger = logging.getLogger(__name__)

import test_context
import test_graph

class SQLiteGraphTestCase(test_graph.GraphTestCase):
    storetest = True
    def setUp(self):
        self.store_name = "SQLite"
        self.path = "/var/tmp/test.sqlite"
        test_graph.GraphTestCase.setUp(self)

class SQLiteContextTestCase(test_context.ContextTestCase):
    storetest = True
    def setUp(self):
        self.store_name = "SQLite"
        self.path = "/var/tmp/test.sqlite"
        test_context.ContextTestCase.setUp(self)

    
