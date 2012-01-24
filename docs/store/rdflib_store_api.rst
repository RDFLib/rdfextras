
A "pseudocode" distillation of the API calls
============================================

All Stores subclass the main RDFLib Store class which presents the following 
triple- and namespace-oriented API:

.. code-block:: python

    class Store(object):
        """"""
        context_aware = False
        formula_aware = False
        transaction_aware = False
        batch_unification = False
        
        def __init__(self, configuration=None, identifier=None):
            """ """
            pass

        # Basic store management        
        def create(self, configuration):
            """ """
            pass

        def open(self, configuration, create=False):
            """ """
            pass

        def close(self, commit_pending_transaction=False):
            """ """
            pass

        def destroy(self, configuration):
            """ """
            pass

        def gc(self):
            """ """
            pass

        # The RDF API
        def add(self, (subject, predicate, object), context, quoted=False):
            """
            Adds the given statement to a specific context or to the model. The
            quoted argument is interpreted by formula-aware stores to indicate this
            statement is quoted/hypothetical It should be an error to not specify a
            context and have the quoted argument be True. It should also be an error
            for the quoted argument to be True when the store is not formula-aware.
            """
            pass

        def addN(self, quads):
            """
            Adds each item in the list of statements to a specific context. The
            quoted argument is interpreted by formula-aware stores to indicate this
            statement is quoted/hypothetical. Note that the default implementation
            is a redirect to add
            """
            pass

        def remove(self, (subject, predicate, object), context=None):
            """
            Remove the set of triples matching the pattern from the store
            """
            pass

        def triples_choices(self, (subject, predicate, object_),context=None):
            """
            A variant of triples that can take a list of terms instead of a single
            term in any slot.  Stores can implement this to optimize the response
            time from the default 'fallback' implementation, which will iterate over
            each term in the list and dispatch to triples.
            """
            pass

        def triples(self, (subject, predicate, object), context=None):
            """
            A generator over all the triples matching the pattern. Pattern can
            include any objects for used for comparing against nodes in the store,
            for example, REGEXTerm, URIRef, Literal, BNode, Variable, Graph,
            QuotedGraph, Date? DateRange?

            A conjunctive query can be indicated by either providing a value of None
            for the context or the identifier associated with the Conjunctive Graph
            (if it is context-aware).
            """
            pass

        def __len__(self, context=None):
            """
            Number of statements in the store. This should only account for non-
            quoted (asserted) statements if the context is not specified, otherwise
            it should return the number of statements in the formula or context
            given.
            """
            pass

        def contexts(self, triple=None):
            """
            Generator over all contexts in the graph. If triple is specified, a
            generator over all contexts the triple is in.
            """
            pass

        # Optional Namespace methods
        def bind(self, prefix, namespace):
            """ """
            pass

        def prefix(self, namespace):
            """ """
            pass

        def namespace(self, prefix):
            """ """
            pass

        def namespaces(self):
            """ """
            pass

        # Optional Transactional methods
        def commit(self):
            """ """
            pass

        def rollback(self):
            """ """
            pass

