import os
import logging
import time
import unittest
from glob import glob
import rdflib
from rdflib.graph import Graph


log = logging.getLogger(__name__)
DEBUG = False
EVALUATE = True
DEBUG_PARSE = False
STORE='IOMemory'
configString = ''


def create_graph(n3data):
    g = Graph()
    g.parse(location=n3data, format='n3')
    return g

global g
fn = os.path.dirname(os.path.abspath(__file__))+'/sp2b/10kdata.n3'
g = create_graph(fn)


class TestSimpleQueries(unittest.TestCase):
    def test_sbp2(self):
        import sys
        if sys.platform.startswith("linux2"):
            return # Interminable, almost literally
        else:
            print("Graph loaded.")
            here_dir = os.path.dirname(os.path.abspath(__file__))
            if not 'sp2b' in here_dir:
                os.chdir(here_dir+'/sp2b')
            for idx, testFile in enumerate(glob('queries/*.sparql')): #[40:50]):
                if idx in [5,6]:
                    continue
                q = open(testFile).read()
                t1 = time.time()
                result = g.query(q,processor='sparql')
                t2 = time.time()
                if not result.result:
                    def stab(result):
                        if result.askAnswer[0]:
                            return [True]
                        else:
                            []
                    if result.askAnswer:
                        result.result = stab(result)
                    else:
                        result.result = []
                print("Q%s\t%s\t%fs" % (testFile[9:-7], len(result.result), t2-t1))

if __name__ == '__main__':
    unittest.main()
