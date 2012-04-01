import warnings

try:
    set
except NameError:
    from sets import Set as set

import types
from rdflib.term import URIRef, BNode, Variable, Identifier
from rdflib.query import Result
from rdflib.graph import Graph, ConjunctiveGraph, ReadOnlyGraphAggregate
from rdflib.util import check_subject, list2set
from rdfextras.sparql import SPARQLError
from rdfextras.sparql.components import Prolog
from rdfextras.sparql.graph import SPARQLGraph
from rdfextras.sparql.graph import GraphPattern

SPARQL_XML_NAMESPACE = u'http://www.w3.org/2005/sparql-results#'


try:
    # Used in Python 2.7 and 3.x for cmp_to_key
    import functools
except ImportError:
    functools = None

class SessionBNode(BNode):
    """
    Special 'session' BNodes.  I.e., BNodes at the query side which refer to
    BNodes in persistence
    """
    pass

class EnoughAnswers(Exception):
    """Raised within expand when the specified LIMIT has been reached"""
    pass

def _checkOptionals(pattern, optionals):
    """
    The following remark in the SPARQL document is important:

    'If a new variable is mentioned in an optional block (as mbox and
    hpage are mentioned in the previous example), that variable can be
    mentioned in that block and can not be mentioned in a subsequent
    block.'

    What this means is that the various optional blocks do not
    interefere at this level and there is no need for a check whether
    a binding in a subsequent block clashes with an earlier optional
    block.

    This method checks whether this requirement is fulfilled. Raises a
    SPARQLError exception if it is not (the rest of the algorithm
    relies on this, so checking it is a good idea...)

    :param pattern: a :class:`~rdfextras.sparql.graph.GraphPattern`
    :param optionals: a :class:`~rdfextras.sparql.graph.GraphPattern`
    :raise SPARQLError: if the requirement is not fulfilled
    """
    for i in xrange(0, len(optionals)):
        for c in optionals[i].unbounds:
            if c in pattern.unbounds:
                # this is fine, an optional query variable can appear in the
                # main pattern, too
                continue
            if i > 0:
                for j in xrange(0, i):
                    if c in optionals[j].unbounds:
                        # This means that:
                        #   - the variable is not in the main pattern (because
                        #     the previous if would have taken care of it)
                        #   - the variable is in the previous optional:
                        #     ie, Error!
                        raise SPARQLError(
                            "%s is an illegal query string, it appear in a previous OPTIONAL clause" % c)


def _variablesToArray(variables, name=''):
    """
    Turn an array of Variables or query strings into an array of query strings.
    If the 'variables' arg is in fact a single string or Variable, then it is
    also put into an array.

    :param variables: a string, a unicode, or a Variable, or an array of those
        (can be mixed, actually). As a special case, if the value is "*", it
        returns None (this corresponds to the wildcard in SPARQL)
    :param name: the string to be used in the error message
    """
    if isinstance(variables,basestring):
        if variables == "*":
            return None
        else:
            return [variables]

    elif isinstance(variables,Variable):
        return [variables]

    elif type(variables) == list or type(variables) == tuple:
        retval = []
        for s in variables:
            if isinstance(s, basestring):
                retval.append(s)
            elif isinstance(s, Variable):
                retval.append(s)
            else:
                raise SPARQLError(
                    "illegal type in '%s'; must be a string, unicode, or a Variable" % name)

    else :
        raise SPARQLError(
            "'%s' argument must be a string, a Variable, or a list of those" % name)

    return retval

def _createInitialBindings(pattern):
    """
    Creates an initial binding directory for the :class:`~rdfextras.sparql.graph.GraphPattern`
    by putting a None as a value for each query variable.

    :param pattern: a :class:`~rdfextras.sparql.graph.GraphPattern`
    """
    bindings = {}
    for c in pattern.unbounds:
        bindings[c] = None

    return bindings

def _ancestorTraversal(node, selected=False):
    if selected:
        yield node
    if node.parent:
        for i in _ancestorTraversal(node.parent, selected=True):
            yield i

def _fetchBoundLeaves(node, previousBind=False, proxyTree=False):
    """
    Takes a SPARQLNode and returns a generator
    over its bound leaves (including OPTIONAL proxies)
    """
    isaProxyTree = proxyTree or node.priorLeftJoin
    if len(node.children) == 0:
        if node.bound and not node.clash:
            # An OPTIONAL proxy is an expansion descendant which was
            # bound and valid (compatible) at a prior point and thus
            # serves as the cumulative context for all subsequent operations
            proxy = False
            for optChild in reduce(lambda x,y: x+y,[
                        list(_fetchBoundLeaves(o,previousBind,isaProxyTree))
                                for o in node.optionalTrees],
                        []):
                proxy = True
                yield optChild

            if not proxy:
                yield node

        elif node.clash and previousBind and isaProxyTree:
            #prior evaluation of LeftJoin was successful but later became
            #excluded.  Note, this should not provide any bindings

            yield node

    else:

        for c in node.children:
            for proxy in _fetchBoundLeaves(c, previousBind, isaProxyTree):
                yield proxy

def isGroundQuad(quad):
    for term in quad:
        if isinstance(term,Variable):
            return False
    return True


class _SPARQLNode(object):
    """
    The SPARQL implementation is based on the creation of a tree, each
    level for each statement in the 'where' clause of SPARQL.

    Each node maintains a 'binding' dictionary, with the variable
    names and either a None if not yet bound, or the binding
    itself. The method 'expand' tries to make one more step of binding
    by looking at the next statement: it takes the statement of the
    current node, binds the variables if there is already a binding,
    and looks at the triple store for the possibilities. If it finds
    valid new triplets, that will bind some more variables, and
    children will be created with the next statement in the 'where'
    array with a new level of bindings. This is done for each triplet
    found in the store, thereby branching off the tree. If all
    variables are already bound but the statement, with the bound
    variables, is not 'true' (ie, there is no such triple in the
    store), the node is marked as 'clash' and no more expansion is
    made; this node will then be thrown away by the parent. If I{all}
    children of a node is a clash, then it is marked as a clash
    itself.

    At the end of the process, the leaves of the tree are searched; if
    a leaf is such that:

      - all variables are bound
      - there is no clash

    then the bindings are returned as possible answers to the query.

    The optional clauses are treated separately: each 'valid' leaf is
    assigned an array of expansion trees that contain the optional
    clauses (that may have some unbound variables bound at the leaf,
    though).

    :ivar parent: parent in the tree, a _SPARQLNode
    :ivar children: the children (in an array of _SPARQLNodes)
    :ivar bindings:  copy of the bindings dictionary locally
    :ivar statement:  the current statement, a (s,p,o,f) tuple ('f'
        is the local filter or None)
    :ivar rest:  the rest of the statements (an array)
    :ivar clash: Boolean, intialized to False
    :ivar bound: Boolean True or False depending on whether all variables are bound
        in self.binding
    :ivar optionalTrees: array of _SPARQLNode instances forming expansion trees
        for optional statements
    """

    __slots__ = ("queryProlog",
                 "expr",
                 "tripleStore",
                 "bindings",
                 "optionalTrees",
                 "bound",
                 "clash",
                 "priorLeftJoin",
                 "dontSpawn",
                 "children",
                 "parent",
                 "statement",
                 "rest")

    def __init__(self, parent, bindings, statements, tripleStore, expr=None):
        """
        :param parent: parent node
        :param bindings: a dictionary with the bindings that are already done
            or with ``None`` value if no binding yet
        :param statements: array of statements from the 'where' clause. The
            first element is for the current node, the rest for the children.
            If empty, then no expansion occurs (ie, the node is a leaf)
        :param tripleStore: the 'owner' :class:`rdfextras.sparql.graph.SPARQLGraph` triple store
        """
        self.priorLeftJoin = False
        self.expr = expr
        self.tripleStore = tripleStore
        self.bindings = bindings
        self.optionalTrees = []
        self.dontSpawn = False

        if None in bindings.values():
            self.bound = False
        else:
            self.bound = True

        self.clash     = False

        self.parent    = parent
        self.children  = []

        if len(statements) > 0:
            self.statement = statements[0]
            self.rest = statements[1:]
        else:
            self.statement = None
            self.rest = None

        # Instead of global queryProlog
        self.queryProlog = Prolog(None, [])
        self.queryProlog.DEBUG = False
        self.queryProlog.answerList = []
        self.queryProlog.eagerLimit = None
        self.queryProlog.rightMostBGPs = []


    def __reduce__(self):
        if self.statement:
            statements = [self.statement] + self.rest
        else:
            statements = []
        return (_SPARQLNode,
                (self.parent,
                 self.bindings,
                 statements,
                 self.tripleStore,
                 self.expr),
                 self.__getstate__())

    def __getstate__(self):
        if self.statement:
            statements = [self.statement] + self.rest
        else:
            statements = []
        return (self.clash,
                self.optionalTrees,
                self.children,
                self.parent,
                self.bindings,
                statements,
                self.tripleStore,
                self.expr,
                self.bound,
                self.priorLeftJoin,
                self.dontSpawn)

    def __setstate__(self, arg):
        clash, optionals, children, parent, bindings, \
        statements, tripleStore, expr, bound, plj, spawn = arg
        # clash,optionals,children,proxy,spawn = arg
        self.priorLeftJoin = plj
        self.dontSpawn = spawn
        self.bound = bound
        self.clash = clash
        self.optionalTrees = optionals
        self.children = children
        self.parent = parent
        self.bindings = bindings

        if len(statements) > 0:
            self.statement = statements[0]
            self.rest = statements[1:]
        else:
            self.statement = None
            self.rest = None

        self.tripleStore = tripleStore

        self.expr = expr

    def __repr__(self):
        return "<SPARQLNode %s. %s children, %s OPTs.  clash: %s. bound: %s>" % (
                id(self), len(self.children), len(self.optionalTrees), self.clash,
                [k for k in
                    self.bindings.keys() if self.bindings[k] is not None]
                )

    def setupGraph(self, store):
        self.tripleStore.setupGraph(store)

    def returnResult(self, select):
        """
        Collect the result by search the leaves of the the tree. The
        variables in the select are exchanged against their bound
        equivalent (if applicable). This action is done on the valid
        leaf nodes only, the intermediate nodes only gather the
        children's results and combine it in one array.

        :param select: the array of unbound variables in the original
            select that do not appear in any of the optionals. If None,
            the full binding should be considered (this is the case for
            the SELECT * feature of SPARQL)
        :return: an array of dictionaries with non-None bindings.

        """
        if len(self.children) > 0:

            # combine all the results of all the kids into one array
            retval = []
            for c in self.children:
                res = c.returnResult(select)
                # res is a list of dictionaries, so each tuple should be taken
                # out and added to the result
                for t in res:
                    retval.append(t)
            return retval

        else:
            retval = []
            if self.bound == True and self.clash == False:
                # This node should be able to contribute to the final results
                # if it doesn't have any OPTIONAL proxies:
                result = {}

                #Determine if this node has an OPTIONAL 'proxy'
                proxies = []
                if self.optionalTrees:
                    proxies = reduce(lambda x,y: x+y,[list(_fetchBoundLeaves(o))
                                                for o in self.optionalTrees],[])
                # This where the essential happens: the binding values are
                # used to construct the selection result
                # sparql-p fix: A node with valid optional expansion trees
                # should not contribute to bindings (the OPTIONAL expansion
                # trees already account for its bindings)
                # see: http://chatlogs.planetrdf.com/swig/2007-06-07.html#T19-28-43
                if not proxies:
                    # @@FIXME: unused code
                    # prevBound = reduce(lambda x,y: x+y,
                    #            [list(_fetchBoundLeaves(o,previousBind=True))
                    #                             for o in self.optionalTrees],[])
                    if self.optionalTrees \
                          and reduce(lambda x,y: x+y,
                               [list(_fetchBoundLeaves(o, previousBind=True))
                                                for o in self.optionalTrees],[]):
                        pass

                    elif select:
                        for a in select:
                            if a in self.bindings:
                                result[a] = self.bindings[a]

                    else :
                        result = self.bindings.copy()

                    # Initial return block. If there is no optional processing,
                    # that is the result, in fact, because the for cycle below
                    # will not happen
                    retval = [result]

                else:
                    retval = reduce(lambda x,y: x+y,[
                                o.returnResult(select) for o in proxies]
                                )

            return retval

    def expandSubgraph(self,subTriples,pattern) :
        """
        Method used to collect the results. There are two ways to
        invoke the method:

          1. if the pattern argument is not None, then this means the
          construction of a separate triple store with the results.
          This means taking the bindings in the node, and constructing the
          graph via the :meth:`~rdfextras.sparql.graph.GraphPattern.construct`
          method. This happens on the valid leaves; intermediate nodes
          call the same method recursively
          2. otherwise, a leaf returns an array of the bindings, and
          intermediate methods aggregate those.

        In both cases, leaf nodes may successively expand the optional
        trees that they may have.

        :param subTriples: the triples so far as a :class:`rdfextras.sparql.graph.SPARQLGraph`
        :param pattern: a :class:`~rdfextras.sparql.graph.GraphPattern` used to construct a graph
        :return: if pattern is not None, an array of binding dictionaries
        """

        def b(r, bind):
            if type(r) == str:

                val = bind[r]
                if val == None:
                    raise RuntimeError()
                return bind[r]

            else:
                return r

        if len(self.children) > 0 :
            # all children return an array of bindings (each element being
            # a dictionary)
            if pattern == None:

                retval = reduce(lambda x,y: x+y, [
                            x.expandSubgraph(subTriples, None)
                                for x in self.children],
                            [])
                (s,p,o,func) = self.statement

                for bind in retval:
                    try:
                        st = (b(s, bind), b(p, bind), b(o, bind))
                        subTriples.add(st)
                    except :
                        # any exception means a None value creeping in, or
                        # something similar..
                        pass
                return retval

            else:
                for x in self.children :
                    x.expandSubgraph(subTriples, pattern)
        else :
            # return the local bindings if any. Not the optional trees should
            # be added, too!
            if self.bound == True and self.clash == False:
                # Get the possible optional branches:
                for t in self.optionalTrees:
                    t.expandSubgraph(subTriples, pattern)

                if pattern == None:
                    return [self.bindings]
                else:
                    pattern.construct(subTriples, self.bindings)

            else:
                return []


    def _bind(self, r):
        """
        :param r: string
        :return: returns None if no bindings occured yet, the binding otherwise
        """
        if isinstance(r, basestring) and not isinstance(r, Identifier) \
              or isinstance(r, Variable):

            if self.bindings[r] == None:
                return None
            else:
                return self.bindings[r]

        elif isinstance(r, (SessionBNode)):
            return r

        elif isinstance(r, (BNode)):
            return self.bindings.get(r)

        else:
            return r

    def topLevelExpand(self, constraints, prolog):
        self.queryProlog = prolog

        try:
            self.expand(constraints)
        except EnoughAnswers:
            pass

        return None

    def expand(self, constraints):
        if self.tripleStore.graph.store.batch_unification:
            patterns = []

            if self.statement:
                self.checkForEagerTermination()

                for statement in [self.statement] + self.rest:
                    (s,p,o,func) = statement

                    searchTerms = [self._bind(term) is not None \
                                    and self._bind(term) \
                                    or term
                                        for term in [s,p,o]]

                    (search_s, search_p,search_o) = searchTerms # (self._bind(s),self._bind(p),self._bind(o))

                    if self.tripleStore.graphVariable:
                        graphName = self.bindings.get(
                                self.tripleStore.graphVariable,
                                self.tripleStore.graphVariable)

                    elif isinstance(self.tripleStore.graph, ConjunctiveGraph) \
                          and self.tripleStore.DAWG_DATASET_COMPLIANCE:

                        # For query-constructed datasets, match against the
                        # 'default graph' - the first Graph with a non-URIRef
                        # identifier (or an empty, default graph)
                        if isinstance(self.tripleStore.graph,
                                      ReadOnlyGraphAggregate):
                            graphName = None

                            for g in self.tripleStore.graph.graphs:
                                # @@FIXME: unused code
                                # searchRT = []
                                if isinstance(g.identifier, BNode):
                                    graphName = g.identifier
                                    break

                            if graphName is None:
                                # No default graph was created and the active
                                # graph is supposed to be the default graph
                                # so we should have no answers
                                continue

                        else:
                            # match against the default graph
                            graphName = self.tripleStore.graph.default_context.identifier

                    elif isinstance(self.tripleStore.graph, ConjunctiveGraph):
                        # match all graphs
                        graphName = Variable(BNode())

                    else:
                        # otherwise, the default graph is the graph queried
                        graphName = self.tripleStore.graph.identifier

                    patterns.append((search_s, search_p, search_o,graphName))

                # expand at server, accumulating results
                rt = []
                nonGroundPatterns = [pattern for pattern in patterns
                                            if not isGroundQuad(pattern)]

                if nonGroundPatterns:

                    # Only evaluate at the server if not all the terms are ground
                    for rtDict in self.tripleStore.graph.store.batch_unify(patterns):
                        self.checkForEagerTermination()

                        if self.tripleStore.graphVariable:

                            if isinstance(rtDict[self.tripleStore.graphVariable],BNode) \
                                and self.tripleStore.DAWG_DATASET_COMPLIANCE:
                                # We can't match the default graph when the active
                                # graph is set via the GRAPH expression
                                continue

                        rt.append(rtDict)

                        # create a copy of the current bindings, by also adding
                        # the new ones from result of the search
                        new_bindings = self.bindings.copy()
                        new_bindings.update(rtDict)

                        child = _SPARQLNode(self, new_bindings, [],
                                            self.tripleStore, expr=self.expr)
                        self.children.append(child)

                        assert not child.clash and child.bindings

                        for func in constraints:

                            try:
                                if func(new_bindings) == False:
                                    child.clash = True
                                    break

                            except TypeError:
                                child.clash=True

                        if not child.clash and self.expr in self.queryProlog.rightMostBGPs:
                            child.noteTopLevelAnswer(self.queryProlog)

                else:
                    #If all the patterns are ground, there is no need
                    #to invoke server-side unification (no variables to batch unify)
                    self.expandAtClient(constraints)
                    return

            if self.statement:
                if nonGroundPatterns and len(self.children) == 0:
                    self.clash = True

            else:

                for func in constraints:
                    try:
                        if func(self.bindings) == False:
                            self.clash = True
                            break
                    except TypeError:
                        self.clash = True

                if not self.clash and self.expr in self.queryProlog.rightMostBGPs:
                    self.noteTopLevelAnswer(self.queryProlog)

        else:
            self.expandAtClient(constraints)

    def noteTopLevelAnswer(self, prolog):
        # At this point, self.bindings will be a new top-level answer
        prolog.answerList.append(self.bindings)

    def checkForEagerTermination(self):
        if self.queryProlog.eagerLimit is not None:

            if self.queryProlog.DEBUG:
                print "Checking for eager termination.  No. of top-level answers: ", len(self.queryProlog.answerList)
                from pprint import pprint
                pprint(self.queryProlog.answerList)

            if len(self.queryProlog.answerList) >= self.queryProlog.eagerLimit:
                if self.queryProlog.DEBUG:
                    print "Reached eager termination!"
                # We've reached the LIMIT so halt processing
                raise EnoughAnswers()

    def expandAtClient(self, constraints):
        """
        The expansion itself. See class comments for details.

        :param constraints: array of global constraining (filter) methods
        """
        self.checkForEagerTermination()

        # if there are no more statements, that means that the constraints
        # have been fully expanded
        if self.statement :
            # decompose the statement into subject, predicate and object
            # default setting for the search statement
            # see if subject (resp. predicate and object) is already bound. This
            # is done by taking over the content of self.dict if not None and replacing
            # the subject with that binding
            # the (search_subject,search_predicate,search_object) is then created
            (s,p,o,func) = self.statement
            # put the bindings we have so far into the statement; this may add None values,
            # but that is exactly what RDFLib uses in its own search methods!
            (search_s,search_p,search_o) = (self._bind(s),self._bind(p),self._bind(o))
            # We need to keep track of the original Graph associated with the tripleStore
            # so we can switch back to it after changing the active graph (if we do)
            # otherwise we will effect later evaluations which use the same tripleStore instance
            originalGraph = None

            if self.tripleStore.graphVariable:
                if hasattr(self.tripleStore.graph, 'quads'):
                    if self.tripleStore.graphVariable not in self.bindings:
                        searchRT = self.tripleStore.graph.quads(
                                (search_s, search_p,search_o)
                                )
                    else:
                        graphName = self.bindings[self.tripleStore.graphVariable]
                        assert not self.tripleStore.DAWG_DATASET_COMPLIANCE \
                           or isinstance(graphName,URIRef), \
                           "Cannot formally return graph name solutions for the default graph!"

                        unifiedGraph = Graph(self.tripleStore.graph.store, identifier=graphName)

                        originalGraph = self.tripleStore.graph
                        self.tripleStore.graph = unifiedGraph

                        searchRT = [(_s,_p,_o,unifiedGraph)
                                     for _s,_p,_o in unifiedGraph.triples(
                                                (search_s,search_p,search_o))]

                else:
                    assert not self.tripleStore.DAWG_DATASET_COMPLIANCE \
                       or isinstance(self.tripleStore.graph.identifier,URIRef),\
                       "Cannot formally return graph name solutions for the default graph"

                    searchRT = [(_s,_p,_o,self.tripleStore.graph)
                                  for _s,_p,_o in self.tripleStore.graph.triples(
                                        (search_s, search_p, search_o))]

            elif self.tripleStore.DAWG_DATASET_COMPLIANCE \
                 and isinstance(self.tripleStore.graph,ConjunctiveGraph):

                # For query-constructed datasets, match against the 'default graph' -
                # the first Graph with a non-URIRef identifier (or an empty, default graph)
                if isinstance(self.tripleStore.graph, ReadOnlyGraphAggregate):

                        for g in self.tripleStore.graph.graphs:
                            searchRT = []
                            if isinstance(g.identifier, BNode):
                                searchRT = g.triples((search_s, search_p, search_o))
                                break

                else:
                    # match against the default graph
                    searchRT = self.tripleStore.graph.default_context.triples(
                                       (search_s, search_p, search_o))
            else:
                #otherwise, the default graph is the graph queried
                searchRT = self.tripleStore.graph.triples(
                                        (search_s,search_p,search_o))

            if originalGraph:
                self.tripleStore.graph = originalGraph

            for tripleOrQuad in searchRT:

                if self.tripleStore.graphVariable:
                    (result_s,result_p,result_o,parentGraph) = tripleOrQuad
                    if isinstance(self.tripleStore.graph,ConjunctiveGraph) \
                       and self.tripleStore.DAWG_DATASET_COMPLIANCE \
                       and isinstance(parentGraph.identifier, BNode):
                        continue

                    assert isinstance(parentGraph.identifier,URIRef)

                else:
                    (result_s,result_p,result_o) = tripleOrQuad

                # if a user defined constraint has been added, it should be checked now
                if func != None and func(result_s, result_p, result_o) == False:
                    # Oops, this result is not acceptable, jump over it!
                    continue

                # create a copy of the current bindings, by also adding the new
                # ones from result of the search
                new_bindings = self.bindings.copy()
                # @@FIXME: unused code
                # queryTerms = [s,p,o]

                preClash = False
                for searchSlot,searchTerm,result in [
                                (search_s, s, result_s),
                                (search_p, p, result_p),
                                (search_o, o, result_o)]:

                    # searchSlot is what we searched with (variables become none)
                    # searchTerm is the term in the triple pattern
                    # result is the unified term from the dataset
                    if searchSlot == None:

                        # An unknown
                        currBound = new_bindings.get(searchTerm)
                        if currBound is not None:
                            if currBound != result:
                                preClash = True
                        else:
                            new_bindings[searchTerm] = result

                if self.tripleStore.graphVariable:
                    new_bindings[self.tripleStore.graphVariable] = parentGraph.identifier

                # Recursion starts here: create and expand a new child
                child = _SPARQLNode(self, new_bindings, self.rest,
                                    self.tripleStore, expr=self.expr)

                if preClash:
                    child.clash = True
                else:
                    child.expand(constraints)

                # if the child is a clash then no use adding it to the tree,
                # it can be forgotten
                if self.clash == False:
                    self.children.append(child)

            if len(self.children) == 0:
                # this means that the constraints could not be met at all
                # with this binding!!!!
                self.clash = True

        else:
            # this is if all bindings are done; the conditions (ie, global
            # constraints) are still to be checked
            if self.bound == True and self.clash == False:

                for func in constraints:

                    try:
                        if func(self.bindings) == False:
                            self.clash = True
                            break

                    except TypeError:
                        self.clash=True

                if not self.clash and self.expr in self.queryProlog.rightMostBGPs:
                    self.noteTopLevelAnswer(self.queryProlog)

    def expandOptions(self, bindings, statements, constraints):
        """
        Managing optional statements. These affect leaf nodes only, if
        they contain 'real' results. A separate Expansion tree is
        appended to such a node, one for each optional call.

        :param bindings: current bindings dictionary

        :param statements: array of statements from the 'where'
            clause. The first element is for the current node, the rest
            for the children. If empty, then no expansion occurs (ie, the
            node is a leaf). The bindings at this node are taken into
            account (replacing the unbound variables with the real
            resources) before expansion

        :param constraints: array of constraint (filter) methods

        """
        def replace(key, resource, tupl):
            s,p,o,func = tupl
            if key == s:
                s = resource
            if key == p:
                p = resource
            if key == o:
                o = resource
            return (s,p,o,func)

        if len(self.children) == 0:

            # this is a leaf in the original expansion
            if self.bound == True and self.clash == False:

                # see if the optional bindings can be reduced because they are already
                # bound by this node
                toldBNodeLookup = {}
                for key in self.bindings:
                    normalizedStatements = []

                    for t in statements:
                        val = self.bindings[key]

                        if isinstance(val,BNode) and val not in toldBNodeLookup:
                            toldBNodeLookup[val] = val

                        normalizedStatements.append(replace(key,self.bindings[key],t))

                    statements = normalizedStatements

                    if key in bindings :
                        del bindings[key]

                bindings.update(toldBNodeLookup)

                optTree = _SPARQLNode(None, bindings, statements,
                                      self.tripleStore, expr=self.expr)

                self.optionalTrees.append(optTree)
                optTree.expand(constraints)

        else:
            for c in self.children:
                c.expandOptions(bindings, statements, constraints)

def _processResults(select, arr):
    '''
    The result in an expansion node is in the form of an array of
    binding dictionaries.  The caller should receive an array of
    tuples, each tuple representing the final binding (or None) *in
    the order of the original select*. This method is the last step of
    processing by processing these values to produce the right result.

    :param select: the original selection list. If None, then the
        binding should be taken as a whole (this corresponds to the SELECT *
        feature of SPARQL)
    :param arr: the array of bindings dictionaries
    :return: a list of tuples with the selection results
    '''
    retval = []

    if select:
        for bind in arr:
            # each result binding must be taken separately
            qresult = []

            for s in select:
                if s in bind:
                    qresult.append(bind[s])
                else:
                    qresult.append(None)

            # as a courtesy to the user, if the selection has one single
            # element only, then we do not put in a tuple, just add it
            # that way:
            if len(select) == 1:
                retval.append(qresult[0])
            else:
                retval.append(tuple(qresult))
    else:

        # this is the case corresponding to a SELECT * query call
        for bind in arr:
            qresult = [val for key,val in bind.items()]
            if len(qresult) == 1:
                retval.append(qresult[0])
            else:
                retval.append(tuple(qresult))

    return retval


def query(graph, selection, patterns, optionalPatterns=[], initialBindings = {},
          dSCompliance=False, loadContexts=False):
    """
    A shorthand for the creation of a :class:`~rdfextras.sparql.query.Query` instance, returning
    the result of a :meth:`~rdfextras.sparql.query.Query.select` right away.
    Good for most of the usage, when no more action (clustering, etc) is required.

    :param selection: a list or tuple with the selection criteria,
        or a single string. Each entry is a string that begins with "?".

    :param patterns: either a :class:`~rdfextras.sparql.graph.GraphPattern`
        instance or a list of :class:`~rdfextras.sparql.graph.GraphPattern`
        instances. Each pattern in the list represent an 'OR' (or 'UNION')
        branch in SPARQL.

    :param optionalPatterns: either a :class:`~rdfextras.sparql.graph.GraphPattern`
        instance or a list of :class:`~rdfextras.sparql.graph.GraphPattern`
        instances. Each of the elements in the 'patterns' parameter is
        combined with each of the optional patterns and the results are
        concatenated. The list may be empty.

    :return: list of query results as a list of tuples
    """
    result = queryObject(graph, patterns, optionalPatterns,
                         initialBindings, dSCompliance, loadContexts)
    if result == None:

        # generate some proper output for the exception :-)
        msg = "Errors in the patterns, no valid query object generated; "
        if isinstance(patterns, GraphPattern):
            msg += ("pattern:\n%s" % patterns)
        else :
            msg += ("pattern:\n%s\netc..." % patterns[0])

        raise SPARQLError(msg)

    return result.select(selection)

def queryObject(graph, patterns, optionalPatterns=[], initialBindings = None,
                dSCompliance=False, loadContexts=False) :
    """
    Creation of a :class:`~rdfextras.sparql.query.Query` instance.

    :param patterns: either a :class:`~rdfextras.sparql.graph.GraphPattern`
        instance or a list of :class:`~rdfextras.sparql.graph.GraphPattern`
        instances. Each pattern in the list represent an 'OR' (or 'UNION')
        branch in SPARQL.

    :param optionalPatterns: either a :class:`~rdfextras.sparql.graph.GraphPattern`
        instance or a list of :class:`~rdfextras.sparql.graph.GraphPattern`
        instances. Each eof the elements in the 'patterns' parameter is
        combined with each of the optional patterns and the results are
        concatenated.
        The list may be empty.

    :return: a :class:`~rdfextras.sparql.query.Query` object
    """
    def checkArg(arg, error):
        if arg == None:
            return []

        elif isinstance(arg, GraphPattern):
            return [arg]

        elif type(arg) == list or type(arg) == tuple:
            for p in arg:
                if not isinstance(p, GraphPattern):
                    raise SPARQLError(
                        "'%s' argument must be a GraphPattern or a list of those" % error)
            return arg

        else:
            raise SPARQLError(
                "'%s' argument must be a GraphPattern or a list of those" % error)

    finalPatterns = checkArg(patterns,"patterns")
    finalOptionalPatterns = checkArg(optionalPatterns,"optionalPatterns")

    retval = None

    if not initialBindings:
        initialBindings = {}

    for pattern in finalPatterns :
        # Check whether the query strings in the optional clauses are fine.
        # If a problem occurs, an exception is raised by the function
        _checkOptionals(pattern, finalOptionalPatterns)
        bindings = _createInitialBindings(pattern)

        if initialBindings:
            bindings.update(initialBindings)

        # This is the crucial point: the creation of the expansion tree and
        # the expansion. That is where the real meal is, we had only an
        # appetizer until now :-)
        top = _SPARQLNode(None, bindings, pattern.patterns, graph)
        top.expand(pattern.constraints)

        for opt in finalOptionalPatterns:
            bindings = _createInitialBindings(opt)
            if initialBindings:
                bindings.update(initialBindings)

            top.expandOptions(bindings,opt.patterns,opt.constraints)

        r = Query(top, graph)

        if retval == None:
            retval = r

        else:
            # This branch is, effectively, the UNION clause of the draft
            retval = retval + r

    return retval


class Query:
    """
    Result of a SPARQL query. It stores to the top of the query tree, and
    allows some subsequent inquiries on the expanded tree. **This class
    should not be instantiated by the user**, it is done by the
    :func:`~rdfextras.sparql.query.queryObject` function.

    """
    def __init__(self, sparqlnode, triples, parent1=None, parent2=None):
        """
        :param sparqlnode: top of the expansion tree, a _SPARQLNode
        :param triples: triple store, a :class:`~rdfextras.sparql.graph.SPARQLGraph`
        :param parent1: possible parent :class:`~rdfextras.sparql.query.Query`
          when queries are combined by summing them up
        :param parent2: possible parent :class:`~rdfextras.sparql.query.Query`
          when queries are combined by summing them up
        """
        self.top = sparqlnode
        self.triples = triples
        # if this node is the result of a sum...
        self.parent1 = parent1
        self.parent2 = parent2

        self.get_recursive_results = None

    def __add__(self, other):
        """
        This may be useful when several queries are performed and
        one wants the 'union' of those.
        Caveat: the triple store must be the same for each argument.
        This method is used internally only anyway...

        Efficiency trick (I hope it works): the various additions
        on subgraphs are not done here; the results are calculated
        only if really necessary, ie, in a lazy evaluation manner.
        This is achieved by storing self and the 'other' in the
        new object
        """

        return Query(None, self.triples, self,other)

    def _getFullBinding(self):
        """Retrieve the full binding, ie, an array of binding dictionaries
        """
        if self.parent1 != None and self.parent2 != None:
            return self.parent1._getFullBinding() + self.parent2._getFullBinding()

        else:
            # remember: returnResult returns an array of dictionaries
            return self.top.returnResult(None)

    def _getAllVariables(self):
        """Retrieve the list of all variables, to be returned"""
        if self.parent1 and self.parent2:
            return list2set(self.parent1._getAllVariables() + self.parent2._getAllVariables())

        else:
            maxKeys = []

            for bound in _fetchBoundLeaves(self.top):
                maxKeys.extend(bound.bindings.keys())

            return list2set(maxKeys)

    def _orderedSelect(self, selection, orderedBy, orderDirection):
        """
        The variant of the selection (as below) that also includes the
        sorting. Because that is much less efficient, this is separated into
        a distinct method that is called only if necessary. It is called
        from the :meth:`select` method.

        Because order can be made on variables that are not part of the final
        selection, this method retrieves a *full* binding from the result to
        be able to order it (whereas the core :meth:`select` method retrieves
        only the selected bindings from the result). The full binding is an
        array of (binding) dictionaries; the sorting sorts this array by
        comparing the bound variables in the respective dictionaries. Once
        this is done, the final selection is done.

        :param selection: Either a single query string, or an array or tuple
            of query strings.
        :param orderBy: either a function or a list of strings (corresponding
            to variables in the query). If None, no sorting occurs on the
            results. If the parameter is a function, it must take two
            dictionary arguments (the binding dictionaries), return -1, 0,
            and 1, corresponding to smaller, equal, and greater, respectively.
        :param orderDirection: if not None, then an array of integers of the
            same length as orderBy, with values the constants ASC or DESC
            (defined in the module). If None, an ascending order is used.
        :return: selection results as a list of tuples
        :raise SPARQLError: invalid sorting arguments
        """
        fullBinding = self._getFullBinding()

        if type(orderedBy) is types.FunctionType:
            _sortBinding = orderedBy
        else:
            orderKeys = _variablesToArray(orderedBy,"orderBy")
            # see the direction
            oDir = None # this is just to fool the interpreter's error message

            if orderDirection is None :
                oDir = [True for i in xrange(0, len(orderKeys))]

            elif type(orderDirection) is types.BooleanType:
                oDir = [orderDirection]

            elif type(orderDirection) is not types.ListType \
                and type(orderDirection) is not types.TupleType:
                raise SPARQLError(
                    "'orderDirection' argument must be a list")

            elif len(orderDirection) != len(orderKeys) :
                raise SPARQLError(
                    "'orderDirection' must be of an equal length to 'orderBy'")

            else :
                oDir = orderDirection

            def _sortBinding(b1, b2):
                """
                The sorting method used by the array sort, with return values
                as required by the Python run-time
                The to-be-compared data are dictionaries of bindings.
                """

                for i in xrange(0, len(orderKeys)):
					# each key has to be compared separately. If there is a
                    # clear comparison result on that key then we are done,
                    # but when that is not the case, the next in line should
                    # be used
                    key = orderKeys[i]
                    direction = oDir[i]
                    if key in b1 and key in b2:
                        val1 = b1[key]
                        val2 = b2[key]
                        if val1 != None and val2 != None:
                            if direction:
                                if val1 < val2:
                                    return -1
                                elif val1 > val2:
                                    return 1
                            else:
                                if val1 > val2:
                                    return -1
                                elif val1 < val2:
                                    return 1

                return 0

        # get the full Binding sorted

        try:
            keyfunc = functools.cmp_to_key(_sortBinding)
            fullBinding.sort(key=keyfunc)

        except AttributeError:
            # Python < 2.7
            fullBinding.sort(cmp=_sortBinding)

        # remember: _processResult turns the expansion results (an array of
        # dictionaries) into an array of tuples in the right, original order
        retval = _processResults(selection,fullBinding)

        return retval

    def select(self, selection, distinct=True, limit=None,
               orderBy=None, orderAscend=None, offset=0):
        """
        Run a selection on the query.

        :param selection: Either a single query string, or an array or tuple of
            query strings.
        :param distinct: Boolean - if True, identical results are filtered out.
        :param limit: if set to a(non-negative) integer value, the first
            'limit' number of results are returned, otherwise all the
            results are returned.
        :param orderBy: either a function or a list of strings (corresponding
            to variables in the query). If None, no sorting occurs on the
            results. If the parameter is a function, it must take two
            dictionary arguments (the binding dictionaries), return -1, 0, and
            1, corresponding to smaller, equal, and greater, respectively.
        :param orderAscend: if not None, then an array of booleans of the
            same length as orderBy, True for ascending and False for
            descending. If None, an ascending order is used.
        :param offset: the starting point of return values in the array of
            results. This parameter is only relevant when some sort of order
            is defined.
        :return: selection results as a list of tuples
        :raise SPARQLError: invalid selection argument
        """

        def _uniquefyList(lst):
            """
            Return a copy of the list but possible duplicate elements are
            taken out. Used to post-process the outcome of the query

            :param lst: input list
            :return: result list
            """
            if len(lst) <= 1:
                return lst
            else:
                # must be careful! Using the quick method of Sets destroy the order. Ie, if this was ordered, then
                # a slower but more secure method should be used
                if orderBy != None:
                    retval = []

                    for i in xrange(0, len(lst)):
                        v = lst[i]
                        skip = False

                        for w in retval:
                            if w == v:
                                skip = True
                                break

                        if not skip:
                            retval.append(v)

                    return retval

                else:
                    return list(set(lst))

        # Select may be a single query string, or an array/tuple thereof
        selectionF = _variablesToArray(selection, "selection")

        if type(offset) is not types.IntType or offset < 0:
            raise SPARQLError("'offset' argument is invalid")

        if limit != None:
            if type(limit) is not types.IntType or limit < 0:
                raise SPARQLError("'offset' argument is invalid")

        if orderBy != None:
            results = self._orderedSelect(selectionF, orderBy, orderAscend)

        else:

            if self.parent1 != None and self.parent2 != None:
                results = self.parent1.select(selectionF) \
                          + self.parent2.select(selectionF)

            else:
                # remember: _processResult turns the expansion results
                # (an array of dictionaries) into an array of tuples in
                # the right, original order
                if self.get_recursive_results is not None:
                    selectionF.append(self.map_from)

                node_results = self.top.returnResult(selectionF)

                if self.get_recursive_results is not None:
                    node_results.extend(
                      self._recur(node_results, selectionF))
                    selectionF.pop()

                results = _processResults(selectionF, node_results)

        if distinct:
            retval = _uniquefyList(results)

        else:
            retval = results

        if limit != None:

            if limit == 0:
                return []

            return retval[offset:limit + offset]

        elif offset > 0:
            return retval[offset:]

        else:
            return retval

    def _recur(self, previous_results, select, last_history=None,
               first_result=None):
        results = []
        for result in previous_results:

            new_val = result[self.map_from]

            base_result = first_result

            if base_result is None:
                base_result = result

            if last_history is None:
                history = set()
            else:
                history = last_history.copy()

            if new_val not in history:

                history.add(new_val)

                recursive_initial_binding = {
                    self.map_to: result[self.map_from]}

                new_results = self.get_recursive_results(
                    recursive_initial_binding, select)

                results.extend(self._recur(
                        new_results, select, history, base_result))

                for new_result in new_results:
                    new_result[self.map_to] = base_result[self.map_to]
                    results.append(new_result)

        return results

    def set_recursive(self, get_recursive_results, variable_maps):
        self.get_recursive_results = get_recursive_results
        # We only currently use the first mapping.  Remember, this is all
        # experimental.  ;-)
        self.map_from, self.map_to = variable_maps[0]

    def construct(self, pattern=None):
        """
        Expand the subgraph based on the pattern or, if None, the
        internal bindings.

        In the former case the binding is used to instantiate the
        triplets in the patterns; in the latter, the original
        statements are used as patterns.

        The result is a separate triple store containing the subgraph.

        :param pattern: a :class:`rdfextras.sparql.graph.GraphPattern` instance or None
        :return: a new triple store of type :class:`rdfextras.sparql.graph.SPARQLGraph`
        """
        if self.parent1 != None and self.parent2 != None:
            return self.parent1.construct(pattern) \
                    + self.parent2.construct(pattern)

        else:
            subgraph = SPARQLGraph()
            self.top.expandSubgraph(subgraph,pattern)
            return subgraph

    def ask(self):
        """
        Whether a specific pattern has a solution or not.
        :rtype: Boolean
        """
        return len(self.select('*')) != 0

    #########################################################################################################
    # The methods below are not really part of SPARQL, or may be used to a form of DESCRIBE. However, that latter
    # is still in a flux in the draft, so we leave it here, pending

    def clusterForward(self, selection):
        """
        Forward clustering, using all the results of the query as
        seeds (when appropriate). It is based on the usage of the
        :meth:`rdfextras.sparql.graph.SPARQLGraph.clusterForward`
        method for triple store.

        :param selection: a selection to define the seeds for
            clustering via the selection; the result of select used for
            the clustering seed

        :return: a new triple store of type :class:`rdfextras.sparql.graph.SPARQLGraph`

        """
        if self.parent1 != None and self.parent2 != None:

            return self.parent1.clusterForward(selection) \
                    + self.parent2.clusterForward(selection)

        else:

            clusterF = SPARQLGraph()

            for r in reduce(lambda x,y: list(x) + list(y), self.select(selection), ()):
                try:
                    check_subject(r)
                    self.triples.clusterForward(r,clusterF)
                except:
                    # no real problem, this is a literal, just forget about it
                    continue

            return clusterF

    def clusterBackward(self, selection) :
        """
        Backward clustering, using all the results of the query as
        seeds (when appropriate). It is based on the usage of the
        :meth:`rdfextras.sparql.graph.SPARQLGraph.clusterBackward`
        method for triple store.

        :param selection: a selection to define the seeds for
            clustering via the selection; the result of select used for
            the clustering seed

        :return: a new triple store of type :class:`rdfextras.sparql.graph.SPARQLGraph`

        """
        if self.parent1 != None and self.parent2 != None:
            return self.parent1.clusterBackward(selection) \
                    + self.parent2.clusterBackward(selection)

        else:
            clusterB = SPARQLGraph()
            # to be on the safe side, see if the query has been properly
            # finished
            for r in reduce(lambda x,y: list(x) + list(y),self.select(selection), ()):
                self.triples.clusterBackward(r, clusterB)

            return clusterB

    def cluster(self, selection):
        """
        cluster: a combination of :meth:`~rdfextras.sparql.query.Query.clusterBackward`
        and :meth:`~rdfextras.sparql.query.Query.clusterForward`.

        :param selection: a selection to define the seeds for clustering
         via the selection; the result of select used for the clustering seed
        """
        return self.clusterBackward(selection) \
                + self.clusterForward(selection)

    def describe(self, selection, forward=True, backward=True):
        """
        The DESCRIBE Form in the SPARQL draft is still in state of
        flux, so this is just a temporary method, in fact.  It may not
        correspond to what the final version of describe will be (if
        it stays in the draft at all, that is).  At present, it is
        simply a wrapper around :meth:`~rdfextras.sparql.query.Query.cluster`.

        :param selection: a selection to define the seeds for
          clustering via the selection; the result of select used for
          the clustering seed

        :param forward: cluster forward Boolean, yes or no
        :param backward: cluster backward Boolean yes or no
        """
        if forward and backward:
            return self.cluster(selection)

        elif forward:
            return self.clusterForward(selection)

        elif backward:
            return self.clusterBackward(selection)

        else:
            return SPARQLGraph()

class SPARQLQueryResult(Result):
    """
    Query result class for SPARQL

    Returns, variously:
    * xml - as an XML string conforming to the `SPARQL XML result <http://www.w3.org/TR/rdf-sparql-XMLres/>`_ format.
    * python - as Python objects
    * json - as JSON
    * graph - as an RDFLib Graph, for CONSTRUCT and DESCRIBE queries

    """
    def __init__(self, qResult):
        """
        The constructor is the result straight from sparql. It is tuple of
        1) a list of tuples (in select order, each item is the valid binding
           for the corresponding variable or 'None') for SELECTs, a SPARQLGraph
           for DESCRIBE/CONSTRUCT, and a boolean for ASK
        2) the variables selected
        3) *all* of the variables in the Graph Patterns
        4) the ORDER clause
        5) the DISTINCT clause
        """

        if isinstance(qResult, bool):
            type_ = 'ASK'

        elif isinstance(qResult, Graph):
            type_ = 'CONSTRUCT'

        else:
            type_ = 'SELECT'

        Result.__init__(self, type_)

        if self.type == 'ASK':
            self.askAnswer = qResult

        elif self.type == 'SELECT':
            result, selectionF, allVars, orderBy, distinct, topUnion = qResult

            if topUnion == None:
                raise Exception("No top union! %s"%topUnion)

            if selectionF == []: # select *
                self.vars = allVars
            else:
                self.vars = selectionF

            # self.bindings = [ dict( [ (v, b.get(v)) for v in self.vars ] ) for b in topUnion ]

            if len(self.vars) == 1:
                self.bindings = [dict(zip(self.vars, [b])) for b in result]

            else:
                self.bindings = [dict(zip(self.vars, b)) for b in result]

            # remove rows where all bindings are None
            self.bindings = filter(
                    lambda x: x.values() != [None]*len(x), self.bindings)

        else:
            self.graph = qResult

    def _get_selectionF(self):
        """Method for 'selectionF' property."""
        warnings.warn("the 'selectionF' attribute is deprecated, "
                      "please use 'vars' instead.",
                      DeprecationWarning, stacklevel=2)
        return self.vars

    selectionF = property(_get_selectionF,
                        doc="access the 'selectionF' attribute; "
                            "deprecated and provided only for "
                            "backwards compatibility")

