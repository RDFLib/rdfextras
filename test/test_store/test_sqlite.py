import logging

_logger = logging.getLogger(__name__)

import test_context
import test_graph
from nose.exc import SkipTest
import tempfile

class SQLiteGraphTestCase(test_graph.GraphTestCase):
    storetest = True
    def setUp(self):
        self.store_name = "SQLite"
        self.path = tempfile.mktemp()
        test_graph.GraphTestCase.setUp(self)
    
    def testStatementNode(self):
        raise SkipTest("Known issue.")

class SQLiteContextTestCase(test_context.ContextTestCase):
    storetest = True
    def setUp(self):
        self.store_name = "SQLite"
        self.path = tempfile.mktemp()
        test_context.ContextTestCase.setUp(self)
    
    def testConjunction(self):
        raise SkipTest("Known issue.")

    def testContexts(self):
        raise SkipTest("Known issue.")

    def testLenInMultipleContexts(self):
        raise SkipTest("Known issue.")
    
SQLiteGraphTestCase.storetest = True
SQLiteContextTestCase.storetest = True