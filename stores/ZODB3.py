# # Author: Michel Pelletier

# Any = None

# from rdflib.plugins.memory import IOMemory
# # you must export your PYTHONPATH to point to a Z2.8 or Z3+ installation to 
# # get this to work!, like: export PYTHONPATH="/home/michel/dev/Zope3Trunk/src"

# import os
# from zc.lockfile import LockError
# from rdflib import ConjunctiveGraph
# import ZODB
# import logging
# from persistent import Persistent
# from rdflib.store import CORRUPTED_STORE
# from rdflib.store import NO_STORE
# from rdflib.store import VALID_STORE

# def _parse_rfc1738_args(name):
#     import re
#     import urllib
#     import cgi
#     """ parse url str into options
#     code orig from sqlalchemy.engine.url """
#     pattern = re.compile(r'''
#             (\w+)://
#             (?:
#                 ([^:/]*)
#                 (?::([^/]*))?
#             @)?
#             (?:
#                 ([^/:]*)
#                 (?::([^/]*))?
#             )?
#             (?:/(.*))?
#             '''
#             , re.X)

#     m = pattern.match(name)
#     if m is not None:
#         (name, username, password, host, port, database) = m.group(1, 2, 3, 4, 5, 6)
#         if database is not None:
#             tokens = database.split(r"?", 2)
#             database = tokens[0]
#             query = (len(tokens) > 1 and dict( cgi.parse_qsl(tokens[1]) ) or None)
#             if query is not None:
#                 query = dict([(k.encode('ascii'), query[k]) for k in query])
#         else:
#             query = None
#         opts = {'username':username,'password':password,'host':host,'port':port,'database':database, 'query':query}
#         if opts['password'] is not None:
#             opts['password'] = urllib.unquote_plus(opts['password'])
#         return (name, opts)
#     else:
#         raise ValueError("Could not parse rfc1738 URL from string '%s'" % name)

# from BTrees.IOBTree import IOBTree
# from BTrees.OIBTree import OIBTree
# from BTrees.OOBTree import OOBTree

# class ZODB3(Persistent, IOMemory):

#     def createForward(self):
#         return IOBTree()
    
#     def createReverse(self):
#         return OIBTree()
    
#     def createIndex(self):
#         return IOBTree()
    
#     def createPrefixMap(self):
#         return OOBTree()
    
#     def open(self, db_path, create=True):
#         print("Opening store %s" % db_path)
#         logging.basicConfig()
#         if db_path.endswith('.fs'): 
#             from ZODB.FileStorage import FileStorage 
#             openstr = os.path.abspath(os.path.expanduser(db_path[7:])) 
#             self.db_path = openstr
#             if create and os.path.exists(openstr):
#                 print("Deleting existing store")
#                 os.unlink(openstr)
#                 os.unlink(openstr+'.index')
#                 os.unlink(openstr+'.tmp')
#                 try:
#                     os.unlink(openstr+'.lock')
#                 except:
#                     raise Exception("File not found: %s" % openstr)
#             if not os.path.exists(openstr) and not create:
#                 raise Exception, "File not found: %s" % openstr
#             try:
#                 fs = FileStorage(openstr)
#                 print("Opening store %s" % openstr)
#             except Exception, e:
#                 # raise Exception("Only one ZODBfs connection allowed per thread")
#                 raise Exception("ZODB3 Open error %s" % e)
#         else: 
#             from ZEO.ClientStorage import ClientStorage 
#             schema,opts = _parse_rfc1738_args(db_path) 
#             fs = ClientStorage((opts['host'], int(opts['port']))) 
#         # get the Zope Database 
#         self.zdb = ZODB.DB(fs)
#         # open it 
#         self.connection = self.zdb.open() 
#         #get the root 
#         self.root = self.connection.root() 
#         # get the Conjunctive Graph 
#         # if 'rdflib' not in root and create: 
#         #     root['rdflib'] = ConjunctiveGraph('ZODB3',
#         #                         identifier = URIRef(graph_uri))
#         if 'rdflib' not in self.root and create: 
#             self.root['rdflib'] = ConjunctiveGraph('ZODB3')
#         self.graph = self.root['rdflib']
#         return VALID_STORE
    
#     def close(self, commit_pending_transaction=False):
#         print("Closing store")
#         if self.connection:
#             print("Closing connection")
#             self.connection.close()
#         if self.zdb:
#             print("Closing zdb")
#             self.zdb.close()
#         if self.db_path:
#             try:
#                 os.unlink(self.db_path+'.lock')
#                 print("Unlocked")
#             except Exception, e:
#                 print("Lock removal failed %s" % e)
#                 pass
    
#     def destroy(self, db_path):
#         print("Destroying store %s" % db_path)
#         try:
#             self.close()
#         except:
#             pass
#         if db_path.endswith('.fs') and os.path.exists(db_path):
#             os.unlink(db_path)
#             os.unlink(db_path+'.index')
#             os.unlink(db_path+'.tmp')
#             try:
#                 os.unlink(db_path+'.lock')
#             except OSError:
#                 pass

#     # def remove(self, triple, context=None):
#     #     Store.remove(self, triple, context)
#     #     if context is not None:
#     #         if context == self:
#     #             context = None
#     #             
#     #     f = self.forward
#     #     r = self.reverse
#     #     if context is None:
#     #         for triple, cg in self.triples(triple):
#     #             subject, predicate, object = triple
#     #             si, pi, oi = self.identifierToInt((subject, predicate, object))
#     #             contexts = list(self.contexts(triple))
#     #             for context in contexts:
#     #                 ci = r[context]
#     #                 del self.cspo[ci][si][pi][oi]
#     #                 del self.cpos[ci][pi][oi][si]
#     #                 del self.cosp[ci][oi][si][pi]
#     #                 
#     #                 self._removeNestedIndex(self.spo, si, pi, oi, ci)
#     #                 self._removeNestedIndex(self.pos, pi, oi, si, ci)
#     #                 self._removeNestedIndex(self.osp, oi, si, pi, ci)
#     #                 # grr!! hafta ref-count these before you can collect them dumbass!
#     #                 #del f[si], f[pi], f[oi]
#     #                 #del r[subject], r[predicate], r[object]
#     #     else:
#     #         subject, predicate, object = triple
#     #         ci = r.get(context, None)
#     #         if ci:
#     #             for triple, cg in self.triples(triple, context):
#     #                 si, pi, oi = self.identifierToInt(triple)
#     #                 del self.cspo[ci][si][pi][oi]
#     #                 del self.cpos[ci][pi][oi][si]
#     #                 del self.cosp[ci][oi][si][pi]
#     #                 
#     #                 try:
#     #                     self._removeNestedIndex(self.spo, si, pi, oi, ci)
#     #                     self._removeNestedIndex(self.pos, pi, oi, si, ci)
#     #                     self._removeNestedIndex(self.osp, oi, si, pi, ci)
#     #                 except KeyError:
#     #                     # the context may be a quoted one in which
#     #                     # there will not be a triple in spo, pos or
#     #                     # osp. So ignore any KeyErrors
#     #                     pass
#     #                 # TODO delete references to resources in self.forward/self.reverse
#     #                 # that are not in use anymore...
#     #             
#     #         if subject is None and predicate is None and object is None:
#     #             # remove context
#     #             try:
#     #                 ci = self.reverse[context]
#     #                 del self.cspo[ci], self.cpos[ci], self.cosp[ci]
#     #             except KeyError:
#     #                 # TODO: no exception when removing non-existant context?
#     #                 pass


# # def opendb(url, graph_uri="", create = False):
# #     import os
# #     from zc.lockfile import LockError
# #     from rdflib import ConjunctiveGraph
# #     from rdflib import URIRef
# #     import ZODB
# #     import logging
# #     logging.basicConfig()
# #     from sqlalchemy.engine.url import _parse_rfc1738_args
# #     if url.endswith('.fs'): 
# #         from ZODB.FileStorage import FileStorage 
# #         openstr = os.path.abspath(os.path.expanduser(url[7:])) 
# #         if create and os.path.exists(openstr):
# #             os.unlink(openstr)
# #             os.unlink(openstr+'.index')
# #             os.unlink(openstr+'.tmp')
# #             try:
# #                 os.unlink(openstr+'.lock')
# #             except OSError:
# #                 pass
# #         if not os.path.exists(openstr) and not create:
# #             raise Exception, "File not found: %s" % openstr
# #         try:
# #             fs=FileStorage(openstr)
# #         except LockError:
# #             raise Exception("Only one ZODBfs connection allowed per thread")
# #     else: 
# #         from ZEO.ClientStorage import ClientStorage 
# #         schema,opts = _parse_rfc1738_args(url) 
# #         fs=ClientStorage((opts['host'],int(opts['port']))) 
# #     # get the Zope Database 
# #     zdb=ZODB.DB(fs) 
# #     # open it 
# #     connection=zdb.open() 
# #     #get the root 
# #     root=connection.root() 
# #     # get the Conjunctive Graph 
# #     if 'rdflib' not in root and create: 
# #         root['rdflib'] = ConjunctiveGraph('ZODB3',
# #                             identifier = URIRef(graph_uri))
# #     root['rdflib'].connection = connection
# #     root['rdflib'].zdb = zdb
# #     return root['rdflib'] 
