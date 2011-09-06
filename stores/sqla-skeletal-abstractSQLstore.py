"""
SQLAlchemy-based implementation skeleton for rdflib Store, based on 
AbstractSQLStore and using SQLA/elixir to handle SQL/DB ops.
"""

import logging
from rdfextras.store.AbstractSQLStore import AbstractSQLStore
from elixir import Entity

logging.basicConfig(level=logging.ERROR,format="%(message)s")
_logger = logging.getLogger('rdfextras.store.SQLAlchemyORM')
_logger.setLevel(logging.ERROR)

class SQLAlchemy(AbstractSQLStore):
    """
    SQLAchemy store formula-aware implementation.  It stores its triples in the
    following partitions:
    
    - Asserted non rdf:type statements
    - Asserted rdf:type statements (in a table which models Class membership)
      The motivation for this partition is primarily query speed and scalability
      as most graphs will always have more rdf:type statements than others
    - All Quoted statements
    
    In addition it persists namespace mappings in a separate table.
    """
    
    class AssertedStatement(Entity):
        def __init__(self):
            raise Exception("Not implemented")

    class AssertedTypeStatement(Entity):
        def __init__(self):
            raise Exception("Not implemented")

    class LiteralStatement(Entity):
        def __init__(self):
            raise Exception("Not implemented")

    class QuotedStatement(Entity):
        def __init__(self):
            raise Exception("Not implemented")

    class Namespace(Entity):
        def __init__(self):
            raise Exception("Not implemented")

    def __init__(self, identifier=None, configuration=None):
        """
        :param identifier: URIRef of the Store. Defaults to CWD
        :param configuration: string containing infomation that `open` can 
        use to connect to datastore.
        """
        raise Exception("Not implemented")

    def open(self, home, create=True):
        """
        Opens the store specified by the configuration string. If
        create is True a store will be created if it does not already
        exist. If create is False and a store does not already exist
        an exception is raised. An exception is also raised if a store
        exists but there are insufficient permissions to open the
        store.

        - Parameters
        :param home: a string
        :param create: a Boolean 

        """
        raise Exception("Not implemented")
    
    def destroy(self, home):
        """
        Destroy the underlying persistence for this store.
        """
        raise Exception("Not implemented")
    
    def triples(self, (subject, predicate, obj), context=None):
        """
        A generator over all the triples that match the provided (s, p, o) 
        pattern. The pattern can encompass any objects for comparing to nodes 
        in the store, for example: ``RegExLiteral``, Date? DateRange?
        
        quoted table:                   <id>_quoted_statements
        asserted rdf:type table:        <id>_type_statements
        asserted non rdf:type table:    <id>_asserted_statements
        
        triple columns: subject, predicate, object, context, 
                        termComb, objLanguage, objDatatype
        class membership columns: member, klass, context termComb
        
        FIXME:  These "union all" selects *might* be further optimized 
        by using joins.
        
        """
        raise Exception("Not implemented")

    def triples_choices(self, (subject, predicate, obj), context=None):
        """
        A variant of ``triples`` that can take a list of terms instead of a 
        single term in any slot. Stores can implement this to optimize the
        response time from the import default "fallback" implementation, 
        which will iterate over each term in the list and dispatch to 
        ``triples``.
        """
        raise Exception("Not implemented")

    # Namespace persistence interface implementation
    def namespaces(self):
        raise Exception("Not implemented")

    def bind(self, prefix, namespace):
        raise Exception("Not implemented")

    def prefix(self, namespace):
        raise Exception("Not implemented")

    def namespace(self, prefix):
        raise Exception("Not implemented")


    def executeSQL(self, cursor, qstr, params=None, paramlist=False):
        """
        Takes the query string and the parameters and, depending on the SQL
        implementation, either fills in the parameter in-place or passes it
        to the Python DB impl - if the latter supports this. The default
        behaviour is to fill the parameters in-place, surrounding each 
        parameter with quote characters appropriate to the Python DB impl.
        """
        raise Exception("Not implemented")

    def normalizeTerm(self,term):
        """
        This is overridden here to leave unicode terms "as is" instead of 
        converting them to ascii (the default behavior).
        """
        raise Exception("Not implemented")

    # Where Clause utility Functions

    def buildSubjClause(self, subject, table_name):
        raise Exception("Not implemented")
    
    # The predicate and object clause builders are modified in order to
    # optimize subject and object utility functions which can take lists
    # as their last argument (object, predicate - respectively)
    
    # Capable of taking a list of predicates as well (in which case
    # subclauses are joined with 'OR')
    def buildPredClause(self, predicate, table_name):
        raise Exception("Not implemented")
    
    # Capable of taking a list of objects as well (in which case
    # subclauses are joined with 'OR')
    def buildObjClause(self, obj, table_name):
        raise Exception("Not implemented")
    
    def buildContextClause(self, context, table_name):
        raise Exception("Not implemented")
    
    def buildTypeMemberClause(self, subject, table_name):
        raise Exception("Not implemented")
    
    def buildTypeClassClause(self, obj, table_name):
        raise Exception("Not implemented")
    
    # Optional Namespace methods
    # Placeholder for optimized interfaces
    def subjects(self, predicate=None, obj=None):
        """
        A generator of subjects with the given predicate and object.
        """
        raise Exception("Not implemented")
    
    # Capable of taking a list of predicate terms instead of a single term
    def objects(self, subject=None, predicate=None):
        """
        A generator of objects with the given subject and predicate.
        """
        raise Exception("Not implemented")
    
    # Optimized interfaces (others)
    def predicate_objects(self, subject=None):
        """
        A generator of (predicate, object) tuples for the given subject.
        """
        raise Exception("Not implemented")
    
    def subject_objects(self, predicate=None):
        """
        A generator of (subject, object) tuples for the given predicate.
        """
        raise Exception("Not implemented")
    
    def subject_predicates(self, object=None):
        """
        A generator of (subject, predicate) tuples for the given object.
        """
        raise Exception("Not implemented")
    
    def value(self, subject, predicate=u'http://www.w3.org/1999/02/22-rdf-syntax-ns#value', object=None, default=None, any=False):
        """
        Get a value for a subject/predicate, predicate/object, or
        subject/object pair -- exactly one of subject, predicate,
        object must be None. Useful if one knows that there may only
        be one value.
        
        It is one of those situations that occur a lot, hence this
        "macro-like" utility.
        
        :param subject: 
        :param predicate:
        :param object:
        :param default: value to be returned if no values found
        :param any: if true, return any value in the case there is 
                       more than one, else raise a UniquenessError
        """
        raise Exception("Not implemented")
    
    def EscapeQuotes(self, qstr):
        raise Exception("Not implemented")

