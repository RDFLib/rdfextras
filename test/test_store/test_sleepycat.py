import logging

try:
    import bsddb
except ImportError:
    try:
        import bsddb3
    except:
        from nose.exc import SkipTest
        raise SkipTest("bsddb[3] not installed")

_logger = logging.getLogger(__name__)

import test_context
import test_graph
from test_n3_2 import testN3Store

class SleepycatGraphTestCase(test_graph.GraphTestCase):
    store_name = "Sleepycat"
    storetest = True
    bsddb = True
    
    def tearDown(self):
        self.graph.close()
        import os
        if hasattr(self, 'path') and self.path is not None:
            if os.path.exists(self.path):
                for f in os.listdir(self.path): os.unlink(self.path+'/'+f)
                os.rmdir(self.path)
    
    def testGraphValue(self):
        pass
    
    def testStatement(self):
        pass
    

class SleepycatStoreTestCase(test_context.ContextTestCase):
    store = "Sleepycat"
    storetest = True
    bsddb = True
    
    def tearDown(self):
        self.graph.close()
        import os
        if hasattr(self, 'path') and self.path is not None:
            if os.path.exists(self.path):
                for f in os.listdir(self.path): os.unlink(self.path+'/'+f)
                os.rmdir(self.path)
    
    def testGraphValue(self):
        pass
    
    def testStatement(self):
        pass

testdir = "/var/tmp/test"
testN3Store("Sleepycat", testdir)
import os
for f in os.listdir(testdir):
    os.unlink(testdir+'/'+f)
os.rmdir(testdir)
