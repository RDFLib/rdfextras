#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import rdflib
from rdflib import plugin
from rdflib.store import Store

store_id='STOREIDENTIFIER'
connection_string='user=DBUSER,password=DBPASSWORD,db=DBNAME,host=HOSTNAME'

plugin.register('MySQL', rdflib.store.Store,
                        'rdfextras.store.MySQL', 'MySQL')

def main():
    store = plugin.get('MySQL',Store)(store_id)
    store.open(connection_string,create=False)
    for kb in store.createTables:
        for s in kb.createStatements():
            print(s+';')
    print("\n")
    for suffix,(relations_only,tables) in store.viewCreationDict.items():
        query='create view %s%s as %s'%(store._internedId,
                                        suffix,
        '\n union all \n'.join([t.viewUnionSelectExpression(relations_only) 
                            for t in tables]))
        print(query+';\n\n')

if __name__ == '__main__':
    main()
