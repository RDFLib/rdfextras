===========================================================
AbstractSQLStore :: a SQL-92 formula-aware Store
===========================================================

A SQL-92 formula-aware implementation of an RDFLib Store, contributed by 
Chimezie Ogbuji. It stores its triples in the following partitions: 

i) Asserted ``non rdf:type`` statements 
ii) Asserted ``literal`` statements, 
iii) Asserted ``rdf:type`` statements (in a table which models Class membership). The motivation for this partition is primarily query speed and scalability as most graphs will always have more rdf:type statements than others
iv) All Quoted statements. 

Namespace mappings are persisted in a separate table.

Chimezie explains the design rationale for this implementation in his blog post
of October 28 2005, `Addressing the RDF Scalability bottleneck <http://copia.posterous.com/addressing-the-rdf-scalability-bottleneck>`_ , shamelessly reproduced below.


Addressing the RDF Scalability bottleneck
------------------------------------------

I've been building RDF persistence stores for some time (it's gone from
something of a hobby to the primary responsibility in my current work capacity)
and have come to the conclusion that RDF stores will almost always be
succeptible to the physical limitations of database scalability.

I recall when I was at the Semantic Technology Conference this spring and asked
one of the presenters there what he thought about this problem that all RDF
databases face and the reason why most don't function effectively beyond 5-10
million triples. I liked his answer:

"It's an engineering problem."

Consider the amount of information an adult has stored (by whatever mechanism
the human brain uses to persist information) in his or her noggin. We often take
it for granted - as we do all other aspects of biology we know very little about
- but it's worth considering when thinking about why scalability is a ubiquitous
hurdle for RDF databases.

Some basic Graph theory is relevant to this point:

The size of a graph is the number of edges and the order of a graph is the
number of nodes within the graph. RDF is a Resource Description Framework (where
what we know about resources is key - not so much the resouces themselves) so
it's not surprising that RDF graphs will almost always have a much larger size
than order. It's also not suprising that most performance analysis made across
RDF implementations (such as LargeTripleStores for instance) focus mostly on
triple size.

I've been working on a SQL-based persistence schema for RDF content (for rdflib)
that is a bit different from the standard approaches taken by most RDBMS
implementations of RDF stores I'm familiar with (including those I've written).
Each of the tables are prefixed with a SHA1-hashed digest of the identifier
associated with the 'localized universe' (AKA,the boundary for a closed world
assumptions). The schema is below:

.. sourcecode:: sql

	CREATE TABLE %s_asserted_statements (
	     subject       text not NULL,
	     predicate     text not NULL,
	     object        text,
	     context       text not NULL,
	     termComb      tinyint unsigned not NULL,    
	     objLanguage   varchar(3),
	     objDatatype   text,
	     INDEX termComb_index (termComb),    
	     INDEX spoc_index (subject(100),predicate(100),object(50),context(50)),
	     INDEX poc_index (predicate(100),object(50),context(50)),
	     INDEX csp_index (context(50),subject(100),predicate(100)),
	     INDEX cp_index (context(50),predicate(100))) TYPE=InnoDB
    

.. sourcecode:: sql

	 CREATE TABLE %s_type_statements (
	     member        text not NULL,
	     klass         text not NULL,
	     context       text not NULL,
	     termComb      tinyint unsigned not NULL,
	     INDEX termComb_index (termComb),
	     INDEX memberC_index (member(100),klass(100),context(50)),
	     INDEX klassC_index (klass(100),context(50)),
	     INDEX c_index (context(10))) TYPE=InnoDB
    
.. sourcecode:: sql

	 CREATE TABLE %s_quoted_statements (
	     subject       text not NULL,
	     predicate     text not NULL,
	     object        text,
	     context       text not NULL,
	     termComb      tinyint unsigned not NULL,
	     objLanguage   varchar(3),
	     objDatatype   text,
	     INDEX termComb_index (termComb),
	     INDEX spoc_index (subject(100),predicate(100),object(50),context(50)),
	     INDEX poc_index (predicate(100),object(50),context(50)),
	     INDEX csp_index (context(50),subject(100),predicate(100)),
	     INDEX cp_index (context(50),predicate(100))) TYPE=InnoDB
    

The first thing to note is that statements are partitioned into logical groupings:

``Asserted non rdf:type statements:`` where all asserted RDF statements where the predicate isn't ``rdf:type`` are stored

``Asserted rdf:type statements:`` where all asserted ``rdf:type`` statements are stored

``Quoted statements:`` where all quoted/hypothetical statements are stored

Statement quoting is a `Notation 3 <http://www.w3.org/DesignIssues/Notation3.html>`_  concept and an extension of the RDF model for
this purpose. The most significant partition is the ``rdf:type`` grouping. The idea
is to have class membership modeled at the store level instead of at a level
above it. RDF graphs are as different as the applications that use them but the
primary motivating factor for making this seperation was the assumption that in
most RDF graphs a majority of the statements (or a significant portion) would
consist of ``rdf:type`` statements (statements of class membership).

Class membership can be considered an unstated RDF modelling best practice since
it allows an author to say a lot about a resource simply by associating it with a
class that has its semantics completely spelled out in a separate, supporting
ontology.

The ``rdf:type`` table models class membership explicitly with two columns: ``klass``
and ``member``. This results in a savings of 43 characters per ``rdf:type`` statement.
The implementation takes note of the predicate submitted in triple-matching
pattern and determines which tables to search

Consider the following triple pattern::

     http://metacognition.info ?predicate ?object

The persistence layer would know it needs to check against the table that
persists non ``rdf:type`` statements as well as the class membership table. However,
patterns that match against a specific predicate (other than ``rdf:type``) or class
membership queries only need to check within one partition (or table)::

     http://metacognition.info rdf:type ?klass

In general, I've noticed that being able to partition your SQL search space
(searching within a named graph / context or searching within a single table)
goes along way in query response.

The other thing worth noting is the ``termComb`` column, which is an integer value
representing the 40 unique ways the following RDF terms could appear in a
triple:

* URI Ref
* Blank Node
* Formula
* Literal
* Variable

I'm certain there are many other possible optimizations that can be made in a
SQL schema for RDF triple persistence (there isn't much precedent in this regard
- and Oracle has only recently joined the foray) but partitioning rdf:type
statements seperately is one such thought I've recently had.

[Chimezie Ogbuji]

Typical Usage
-------------

Typical usage is via subclassing to provide an RDFLib Store API in support of 
persistence-specific implementations of RDFLib Store, e.g. the SQLite Store, 
from which the following illustration is drawn:

.. sourcecode:: python

    from sqlite3 import dbapi2

    class SQLite(AbstractSQLStore):
        """
        SQLite store formula-aware implementation.  It stores its triples in the 
        following partitions:
        
        - Asserted non rdf:type statements
        - Asserted rdf:type statements (in a table which models Class membership)
            The motivation for this partition is primarily query speed and 
            scalability as most graphs will always have more rdf:type statements 
            than others
        - All Quoted statements
        
        In addition it persists namespace mappings in a seperate table
        """
        context_aware = True
        formula_aware = True
        transaction_aware = True
        regex_matching = PYTHON_REGEX
        autocommit_default = False
        _Store__node_pickler = None
        
        def open(self, db_path, create=True):
            """
            Opens the store specified by the configuration string. If
            create is True a store will be created if it does not already
            exist. If create is False and a store does not already exist
            an exception is raised. An exception is also raised if a store
            exists, but there is insufficient permissions to open the
            store.
            """
            if create:
                db = dbapi2.connect(db_path)
                c = db.cursor()
                # Only create tables if they don't already exist.  If the first
                # exists, assume they all do.
                try:
                    c.execute(CREATE_ASSERTED_STATEMENTS_TABLE % self._internedId)
                except dbapi2.OperationalError, e:
                    # Raise any error aside from existing table.
                    if (str(e) != 'table %s_asserted_statements already exists' 
                            % self._internedId):
                        raise dbapi2.OperationalError, e
                else:
                    c.execute(CREATE_ASSERTED_TYPE_STATEMENTS_TABLE %
                            self._internedId)
                    c.execute(CREATE_QUOTED_STATEMENTS_TABLE % self._internedId)
                    c.execute(CREATE_NS_BINDS_TABLE % self._internedId)
                    c.execute(CREATE_LITERAL_STATEMENTS_TABLE % self._internedId)
                    for tblName, indices in [
                        (
                            "%s_asserted_statements",
                            [
                                ("%s_A_termComb_index",('termComb',)),
                                ("%s_A_s_index",('subject',)),
                                ("%s_A_p_index",('predicate',)),
                                ("%s_A_o_index",('object',)),
                                ("%s_A_c_index",('context',)),
                            ],
                        ),
                        (
                            "%s_type_statements",
                            [
                                ("%s_T_termComb_index",('termComb',)),
                                ("%s_member_index",('member',)),
                                ("%s_klass_index",('klass',)),
                                ("%s_c_index",('context',)),
                            ],
                        ),
                        (
                            "%s_literal_statements",
                            [
                                ("%s_L_termComb_index",('termComb',)),
                                ("%s_L_s_index",('subject',)),
                                ("%s_L_p_index",('predicate',)),
                                ("%s_L_c_index",('context',)),
                            ],
                        ),
                        (
                            "%s_quoted_statements",
                            [
                                ("%s_Q_termComb_index",('termComb',)),
                                ("%s_Q_s_index",('subject',)),
                                ("%s_Q_p_index",('predicate',)),
                                ("%s_Q_o_index",('object',)),
                                ("%s_Q_c_index",('context',)),
                            ],
                        ),
                        (
                            "%s_namespace_binds",
                            [
                                ("%s_uri_index",('uri',)),
                            ],
                        )]:
                        for indexName, columns in indices:
                            c.execute("CREATE INDEX %s on %s (%s)" %
                                    (indexName % self._internedId,
                                    tblName % self._internedId,
                                    ','.join(columns)))
                    c.close()
                    db.commit()
                    db.close()
            
            self._db = dbapi2.connect(db_path)
            self._db.create_function("regexp", 2, regexp)
            
            if os.path.exists(db_path):
                c = self._db.cursor()
                c.execute("SELECT * FROM sqlite_master WHERE type='table'")
                tbls = [rt[1] for rt in c.fetchall()]
                c.close()
                
                missing = 0
                for tn in [tbl%(self._internedId) for tbl in table_name_prefixes]:
                    if tn not in tbls:
                        missing +=1
            
                if missing == len(table_name_prefixes):
                    return NO_STORE
                elif missing > 0:
                    return CORRUPTED_STORE
                else:
                    return VALID_STORE
                            
            # The database doesn't exist - nothing is there
            return NO_STORE

