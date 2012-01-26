try:
    import PyMySQL as MySQLdb
except ImportError:
    try:
        import MySQLdb
    except ImportError:
        from nose.exc import SkipTest
        raise SkipTest("MySQLdb not installed")
from rdflib import plugin
from rdflib import URIRef, BNode, Literal, Graph
from rdflib.store import Store
from rdfextras.store.FOPLRelationalModel.QuadSlot import normalizeValue
import sys
sys.path.append('../..')
from configstrings import mysqlconfigString as configString
sys.path.pop()

def test_dType_encoding():
    storetest = True
    correct = normalizeValue('http://www.w3.org/2001/XMLSchema#integer', 'U')
    wrong = normalizeValue('http://www.w3.org/2001/XMLSchema#integer', 'L')
    
    store = plugin.get('MySQL',Store)()
    store.destroy(configString)
    store.open(configString,create=True)
    Graph(store).add((BNode(),URIRef('foo'),Literal(1)))
    db=store._db
    cursor=db.cursor()
    cursor.execute(
    "select * from %s where data_type = '%s'"%
        (store.literalProperties, wrong))
    assert not cursor.fetchone(),"Datatype encoding bug!"
    for suffix,(relations_only,tables) in store.viewCreationDict.items():
        query='create view %s%s as %s'%(store._internedId,
                                        suffix,
        ' union all '.join([t.viewUnionSelectExpression(relations_only) 
                            for t in tables]))
        print "## Creating View ##\n",query
    
    store.rollback()
    store.close()

test_dType_encoding.non_core = True
test_dType_encoding.storetest = True
test_dType_encoding.mysql = True


# if __name__ == '__main__':
#     test_dType_encoding()

