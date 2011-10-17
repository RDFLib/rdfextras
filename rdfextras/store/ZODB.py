# Author: Michel Pelletier

Any = None

from rdflib.plugins.memory import IOMemory
# you must export your PYTHONPATH to point to a Z2.8 or Z3+ installation to 
# get this to work!, like: export PYTHONPATH="/home/michel/dev/Zope3Trunk/src"

try:
    # Zope 3
    from persistent import Persistent
except ImportError:
    # < Zope 2.8?
    from Persistence import Persistent

from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree

class ZODBGraph(Persistent, IOMemory):
    context_aware = True
    def createForward(self):
        return IOBTree()
    
    def createReverse(self):
        return OIBTree()
    
    def createIndex(self):
        return IOBTree()
    
    def createPrefixMap(self):
        return OOBTree()


    # def remove(self, triple, context=None):
    #     Store.remove(self, triple, context)
    #     if context is not None:
    #         if context == self:
    #             context = None
    #             
    #     f = self.forward
    #     r = self.reverse
    #     if context is None:
    #         for triple, cg in self.triples(triple):
    #             subject, predicate, object = triple
    #             si, pi, oi = self.identifierToInt((subject, predicate, object))
    #             contexts = list(self.contexts(triple))
    #             for context in contexts:
    #                 ci = r[context]
    #                 del self.cspo[ci][si][pi][oi]
    #                 del self.cpos[ci][pi][oi][si]
    #                 del self.cosp[ci][oi][si][pi]
    #                 
    #                 self._removeNestedIndex(self.spo, si, pi, oi, ci)
    #                 self._removeNestedIndex(self.pos, pi, oi, si, ci)
    #                 self._removeNestedIndex(self.osp, oi, si, pi, ci)
    #                 # grr!! hafta ref-count these before you can collect them dumbass!
    #                 #del f[si], f[pi], f[oi]
    #                 #del r[subject], r[predicate], r[object]
    #     else:
    #         subject, predicate, object = triple
    #         ci = r.get(context, None)
    #         if ci:
    #             for triple, cg in self.triples(triple, context):
    #                 si, pi, oi = self.identifierToInt(triple)
    #                 del self.cspo[ci][si][pi][oi]
    #                 del self.cpos[ci][pi][oi][si]
    #                 del self.cosp[ci][oi][si][pi]
    #                 
    #                 try:
    #                     self._removeNestedIndex(self.spo, si, pi, oi, ci)
    #                     self._removeNestedIndex(self.pos, pi, oi, si, ci)
    #                     self._removeNestedIndex(self.osp, oi, si, pi, ci)
    #                 except KeyError:
    #                     # the context may be a quoted one in which
    #                     # there will not be a triple in spo, pos or
    #                     # osp. So ignore any KeyErrors
    #                     pass
    #                 # TODO delete references to resources in self.forward/self.reverse
    #                 # that are not in use anymore...
    #             
    #         if subject is None and predicate is None and object is None:
    #             # remove context
    #             try:
    #                 ci = self.reverse[context]
    #                 del self.cspo[ci], self.cpos[ci], self.cosp[ci]
    #             except KeyError:
    #                 # TODO: no exception when removing non-existant context?
    #                 pass


