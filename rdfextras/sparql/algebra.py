# -*- coding: utf-8 -*-
"""
An implementation of the W3C SPARQL Algebra on top of sparql-p's expansion trees

See: http://www.w3.org/TR/rdf-sparql-query/#sparqlAlgebra

For each symbol in a SPARQL abstract query, we define an operator for evaluation.
The SPARQL algebra operators of the same name are used to evaluate SPARQL abstract
query nodes as described in the section "Evaluation Semantics".

We define eval(D(G), graph pattern) as the evaluation of a graph pattern with respect
to a dataset D having active graph G. The active graph is initially the default graph.
"""
import unittest
from rdflib.graph import ConjunctiveGraph
from rdflib.graph import Graph
from rdflib.graph import ReadOnlyGraphAggregate
from rdflib import plugin
from rdflib.term import URIRef
from rdflib.term import Variable
from rdflib.store import Store
from rdfextras.sparql import DESCRIBE
from rdfextras.sparql import graph
from rdfextras.sparql import SPARQLError
from rdfextras.sparql import query as sparql_query
from rdfextras.sparql.components import ASCENDING_ORDER
from rdfextras.sparql.components import AskQuery
from rdfextras.sparql.components import DescribeQuery
from rdfextras.sparql.components import GraphPattern
from rdfextras.sparql.components import NamedGraph
from rdfextras.sparql.components import ParsedAlternativeGraphPattern
from rdfextras.sparql.components import ParsedGraphGraphPattern
from rdfextras.sparql.components import ParsedGroupGraphPattern
from rdfextras.sparql.components import ParsedOptionalGraphPattern
from rdfextras.sparql.components import Prolog
from rdfextras.sparql.components import SelectQuery
from rdfextras.sparql.evaluate import convertTerm
from rdfextras.sparql.evaluate import createSPARQLPConstraint
from rdfextras.sparql.evaluate import unRollTripleItems
from rdfextras.sparql.graph import BasicGraphPattern
from rdfextras.sparql.query import _variablesToArray
import logging
log = logging.getLogger(__name__)

# A variable to determine whether we obey SPARQL definition of RDF dataset
# which does not allow matching of default graphs (or any graph with a BNode
# for a name)
#"An RDF Dataset comprises one graph, the default graph, which does not have
# a name" -  http://www.w3.org/TR/rdf-sparql-query/#namedAndDefaultGraph
DAWG_DATASET_COMPLIANCE = False

def ReduceGraphPattern(graphPattern,prolog):
    """
    Takes parsed graph pattern and converts it into a BGP operator

    Replace all basic graph patterns by BGP(list of triple patterns)

    """
    if isinstance(graphPattern.triples[0],list) and len(graphPattern.triples) == 1:
        graphPattern.triples = graphPattern.triples[0]
    items = []
    for triple in graphPattern.triples:
        bgp=BasicGraphPattern(list(unRollTripleItems(triple,prolog)),prolog)
        items.append(bgp)
    if len(items) == 1:
        assert isinstance(items[0],BasicGraphPattern), repr(items)
        bgp=items[0]
        return bgp
    elif len(items) > 1:
        constraints=[b.constraints for b in items if b.constraints]
        constraints=reduce(lambda x,y:x+y,constraints,[])
        def mergeBGPs(left,right):
            if isinstance(left,BasicGraphPattern):
                left = left.patterns
            if isinstance(right,BasicGraphPattern):
                right = right.patterns
            return left+right
        bgp=BasicGraphPattern(reduce(mergeBGPs,items),prolog)
        bgp.addConstraints(constraints)
        return bgp
    else:
        #an empty BGP?
        raise

def ReduceToAlgebra(left,right):
    """

    Converts a parsed Group Graph Pattern into an expression in the algebra by recursive
    folding / reduction (via functional programming) of the GGP as a list of Basic
    Triple Patterns or "Graph Pattern Blocks"

    12.2.1 Converting Graph Patterns

    .. sourcecode:: text

        [20] GroupGraphPattern ::= '{' TriplesBlock? ( ( GraphPatternNotTriples | Filter )
             '.'? TriplesBlock? )* '}'
        [22] GraphPatternNotTriples ::= OptionalGraphPattern | GroupOrUnionGraphPattern |
             GraphGraphPattern
        [26] Filter ::= 'FILTER' Constraint
        [27] Constraint ::= BrackettedExpression | BuiltInCall | FunctionCall
        [56] BrackettedExpression  ::= '(' ConditionalOrExpression ')'


        ( GraphPatternNotTriples | Filter ) '.'? TriplesBlock?
           nonTripleGraphPattern     filter         triples


    """
    prolog = ReduceToAlgebra.prolog
    if not isinstance(right,AlgebraExpression):
        if isinstance(right,ParsedGroupGraphPattern):
            right = reduce(ReduceToAlgebra,right,None)
            log.debug(right)
        assert isinstance(right,GraphPattern),type(right)
        #Parsed Graph Pattern
        if right.triples:
            if right.nonTripleGraphPattern:
                #left is None, just return right (a GraphPatternNotTriples)
                if isinstance(right.nonTripleGraphPattern,ParsedGraphGraphPattern):
                    right = Join(ReduceGraphPattern(right,prolog),
                                 GraphExpression(
                                    right.nonTripleGraphPattern.name,
                                    reduce(ReduceToAlgebra,
                                           right.nonTripleGraphPattern.graphPatterns,
                                           None)))
                elif isinstance(right.nonTripleGraphPattern,
                                ParsedOptionalGraphPattern):
                    # Join(LeftJoin( ..left.. ,{..}),..triples..)
                    if left:
                        assert isinstance(left,(Join,BasicGraphPattern)),repr(left)
                        rightTriples = ReduceGraphPattern(right,prolog)
                        LJright = LeftJoin(left,
                                           reduce(ReduceToAlgebra,
                                                  right.nonTripleGraphPattern.graphPatterns,
                                                  None))
                        return Join(LJright,rightTriples)
                    else:
                        # LeftJoin({},right) => {}
                        rightTriples = ReduceGraphPattern(right,prolog)
                        return Join(reduce(ReduceToAlgebra,
                                                    right.nonTripleGraphPattern.graphPatterns,
                                                    None),
                                    rightTriples)

                elif isinstance(right.nonTripleGraphPattern,
                                ParsedAlternativeGraphPattern):
                    #Join(Union(..),..triples..)
                    unionList =\
                      [ reduce(ReduceToAlgebra,i.graphPatterns,None) for i in
                          right.nonTripleGraphPattern.alternativePatterns ]
                    right = Join(reduce(Union,unionList),
                                 ReduceGraphPattern(right,prolog))
                else:
                    raise Exception(right)
            else:
                if isinstance(left,BasicGraphPattern) and left.constraints:
                    if right.filter:
                        if not left.patterns:
                            #{ } FILTER E1 FILTER E2 BGP(..)
                            filter2=createSPARQLPConstraint(right.filter,prolog)
                            right = ReduceGraphPattern(right,prolog)
                            right.addConstraints(left.constraints)
                            right.addConstraint(filter2)
                            return right
                        else:
                            #BGP(..) FILTER E1 FILTER E2 BGP(..)
                            left.addConstraint(createSPARQLPConstraint(right.filter,
                                                                   prolog))
                    right = ReduceGraphPattern(right,prolog)
                else:
                    if right.filter:
                        #FILTER ...
                        filter=createSPARQLPConstraint(right.filter,prolog)
                        right = ReduceGraphPattern(right,prolog)
                        right.addConstraint(filter)
                    else:
                    #BGP(..)
                        right = ReduceGraphPattern(right,prolog)

        else:
            #right.triples is None
            if right.nonTripleGraphPattern is None:
                if right.filter:
                    if isinstance(left,BasicGraphPattern):
                        #BGP(...) FILTER
                        left.addConstraint(createSPARQLPConstraint(right.filter,
                                                                   prolog))
                        return left
                    else:
                        pattern=BasicGraphPattern()
                        pattern.addConstraint(createSPARQLPConstraint(right.filter,
                                                                      prolog))
                        if left is None:
                            return pattern
                        else:
                            right=pattern
                else:
                    raise Exception(right)
            elif right.nonTripleGraphPattern:
                if isinstance(right.nonTripleGraphPattern,ParsedGraphGraphPattern):
                    # Join(left,Graph(...))
                    right = GraphExpression(right.nonTripleGraphPattern.name,
                                            reduce(ReduceToAlgebra,
                                                   right.nonTripleGraphPattern.graphPatterns,
                                                   None))
                elif isinstance(right.nonTripleGraphPattern,ParsedOptionalGraphPattern):
                    if left:
                        # LeftJoin(left,right)
                        return LeftJoin(left,
                                        reduce(ReduceToAlgebra,
                                               right.nonTripleGraphPattern.graphPatterns,
                                               None))
                    else:
                        # LeftJoin({},right)
                        return reduce(ReduceToAlgebra,
                                      right.nonTripleGraphPattern.graphPatterns,
                                      None)
                elif isinstance(right.nonTripleGraphPattern,
                                ParsedAlternativeGraphPattern):
                    #right = Union(..)
                    unionList =\
                      map(lambda i: reduce(ReduceToAlgebra,i.graphPatterns,None),
                          right.nonTripleGraphPattern.alternativePatterns)
                    right = reduce(Union,unionList)
                else:
                    raise Exception(right)
    if not left:
        return right
    else:
        return Join(left,right)

# # Unreferenced anywhere else
# def RenderSPARQLAlgebra(parsedSPARQL,nsMappings=None):
#     nsMappings = nsMappings and nsMappings or {}
#     global prolog
#     prolog = parsedSPARQL.prolog
#     if prolog is not None:
#         prolog.DEBUG = False
#     else:
#         prolog = Prolog(None, [])
#         prolog.DEBUG=False
#     return reduce(ReduceToAlgebra,
#                   parsedSPARQL.query.whereClause.parsedGraphPattern.graphPatterns,None)

def LoadGraph(dtSet,dataSetBase,graph):
    # An RDF URI dereference, following TAG best practices
    # Need a hook (4Suite) to bypass urllib's inability
    # to implement URI RFC verbatim - problematic for descendent
    # specifications
    try:
        from Ft.Lib.Uri import UriResolverBase as Resolver
        from Ft.Lib.Uri import GetScheme, OsPathToUri
    except:
        def OsPathToUri(path):
            return path
        def GetScheme(uri):
            return None
        class Resolver:
            supportedSchemas=[None]
            def resolve(self, uriRef, baseUri):
                return uriRef
    if dataSetBase is not None:
        res = Resolver()
        scheme = GetScheme(dtSet) or GetScheme(dataSetBase)
        if scheme not in res.supportedSchemes:
            dataSetBase = OsPathToUri(dataSetBase)
        source=Resolver().resolve(str(dtSet), dataSetBase)
    else:
        source = dtSet
    # GRDDL hook here!
    try:
        # Try as RDF/XML first (without resolving)
        graph.parse(source)
    except:
        try:
            # Parse as Notation 3 instead
            source=Resolver().resolve(str(dtSet), dataSetBase)
            graph.parse(source,format='n3')
        except:
            raise
            # RDFa?
            graph.parse(dtSet,format='rdfa')

def TopEvaluate(query,dataset,passedBindings = None,DEBUG=False,exportTree=False,
                dataSetBase=None,
                extensionFunctions={},
                dSCompliance=False,
                loadContexts=False):
    """
    The outcome of executing a SPARQL is defined by a series of steps, starting
    from the SPARQL query as a string, turning that string into an abstract
    syntax form, then turning the abstract syntax into a SPARQL abstract query
    comprising operators from the SPARQL algebra. This abstract query is then
    evaluated on an RDF dataset.
    """
    if not passedBindings:
        passedBindings = {}
    if query.prolog:
        query.prolog.DEBUG = DEBUG
        prolog = query.prolog
    else:
        prolog = Prolog(None, [])
        prolog.DEBUG=False
    prolog.answerList = []
    prolog.eagerLimit = None
    prolog.extensionFunctions.update(extensionFunctions)
    ReduceToAlgebra.prolog = prolog
    query.prolog.rightMostBGPs = set()
    DAWG_DATASET_COMPLIANCE = dSCompliance

    if query.query.dataSets:
        graphs = []
        for dtSet in query.query.dataSets:
            if isinstance(dtSet, NamedGraph):
                if loadContexts:
                    newGraph = Graph(dataset.store, dtSet)
                    LoadGraph(dtSet, dataSetBase, newGraph)
                    graphs.append(newGraph)
                else:
                    continue
            else:
                # "Each FROM clause contains an IRI that indicates a graph to be
                # used to form the default graph. This does not put the graph
                # in as a named graph." -- 8.2.1 Specifying the Default Graph
                if DAWG_DATASET_COMPLIANCE:
                    # @@TODO: this should indicate a merge into the 'default' graph
                    # per http://www.w3.org/TR/rdf-sparql-query/#unnamedGraph
                    # (8.2.1 Specifying the Default Graph)
                    assert isinstance(dataset,ConjunctiveGraph)
                    memGraph = dataset.default_context
                else:
                    if loadContexts:
                        memGraph = dataset.get_context(dtSet)
                    else:
                        memStore = plugin.get('IOMemory',Store)()
                        memGraph = Graph(memStore)
                        LoadGraph(dtSet,dataSetBase,memGraph)
                if memGraph.identifier not in [g.identifier for g in graphs]:
                    graphs.append(memGraph)
        tripleStore = graph.SPARQLGraph(ReadOnlyGraphAggregate(graphs,
                                                                     store=dataset.store),
                                              dSCompliance=DAWG_DATASET_COMPLIANCE)
    else:
        tripleStore = graph.SPARQLGraph(dataset,
                                              dSCompliance=DAWG_DATASET_COMPLIANCE)
    if isinstance(query.query,SelectQuery) and query.query.variables:
        query.query.variables = [convertTerm(item,query.prolog)
                                   for item in query.query.variables]
    else:
        query.query.variables = []

    # Fix for DESCRIBE simple case, e.g. "DESCRIBE <urn:a>" with no WHERE clause
    if query.query.whereClause.parsedGraphPattern is None:
        query.query.whereClause.parsedGraphPattern = BasicGraphPattern([])
        query.query.whereClause.parsedGraphPattern.graphPatterns = ()

    expr = reduce(ReduceToAlgebra,query.query.whereClause.parsedGraphPattern.graphPatterns,
                  None)

    limit = None
    offset = 0
    if isinstance(query.query,SelectQuery) and query.query.solutionModifier.limitClause is not None:
        limit = int(query.query.solutionModifier.limitClause)
    if isinstance(query.query,SelectQuery) and query.query.solutionModifier.offsetClause is not None:
        offset = int(query.query.solutionModifier.offsetClause)
    else:
        offset = 0

    # @@TODO: consider allowing in cases where offset is nonzero
    if limit is not None and offset == 0:
        query.prolog.eagerLimit = limit
        for x in expr.fetchTerminalExpression():
            query.prolog.rightMostBGPs.add(x)
        if query.prolog.DEBUG:
            log.debug("Setting up for an eager limit evaluation (size: %s)" % \
                        query.prolog.eagerLimit)
    if DEBUG:
        log.debug("## Full SPARQL Algebra expression ##")
        log.debug(expr)
        log.debug("###################################")

    if isinstance(expr,BasicGraphPattern):
        retval = None
        bindings = sparql_query._createInitialBindings(expr)
        if passedBindings:
            bindings.update(passedBindings)
        top = sparql_query._SPARQLNode(None,bindings,expr.patterns, tripleStore,expr=expr)
        top.topLevelExpand(expr.constraints, query.prolog)

        # for tree in sparql_query._fetchBoundLeaves(top):
        #     print_tree(tree)
        # print "---------------"
        result = sparql_query.Query(top, tripleStore)
    elif expr is None and isinstance(query.query,DescribeQuery):
        # @@FIXME: unused code
        # retval = None
        bindings = {}
        top = sparql_query._SPARQLNode(None,bindings,(), tripleStore,expr=expr)
        top.topLevelExpand((), query.prolog)

        # for tree in sparql_query._fetchBoundLeaves(top):
        #     print_tree(tree)
        # print "---------------"
        result = sparql_query.Query(top, tripleStore)
    else:
        assert isinstance(expr,AlgebraExpression), repr(expr)
        if DEBUG:
            log.debug("## Full SPARQL Algebra expression ##")
            log.debug(expr)
            log.debug("###################################")
        result = expr.evaluate(tripleStore,passedBindings,query.prolog)
        if isinstance(result,BasicGraphPattern):
            # @@FIXME unused code
            # retval = None
            bindings = sparql_query._createInitialBindings(result)
            if passedBindings:
                bindings.update(passedBindings)
            top = sparql_query._SPARQLNode(None,bindings,result.patterns,
                                    result.tripleStore,expr=result)
            top.topLevelExpand(result.constraints, query.prolog)
            result = sparql_query.Query(top, tripleStore)
        assert isinstance(result,sparql_query.Query),repr(result)

    if exportTree:
        from rdfextras.sparql.Visualization import ExportExpansionNode
        if result.top:
            ExportExpansionNode(result.top,fname='out.svg',verbose=True)
        else:
            ExportExpansionNode(result.parent1.top,fname='out1.svg',verbose=True)
            ExportExpansionNode(result.parent2.top,fname='out2.svg',verbose=True)
    if result == None :
        # @@FIXME: generate some proper output for the exception :-)
        msg = "Errors in the patterns, no valid query object generated; "
        # @@FIXME basicPatterns is undefined
        # msg += ("pattern:\n%s\netc..." % basicPatterns[0])
        raise SPARQLError(msg)

    if isinstance(query.query,AskQuery):
        return result.ask()
    elif isinstance(query.query,SelectQuery):
        orderBy = None
        orderAsc = None
        if query.query.solutionModifier.orderClause:
            orderBy     = []
            orderAsc    = []
            for orderCond in query.query.solutionModifier.orderClause:
                # is it a variable?
                if isinstance(orderCond,Variable):
                    orderBy.append(orderCond)
                    orderAsc.append(ASCENDING_ORDER)
                # is it another expression, only variables are supported
                else:
                    order_expr = orderCond.expression.reduce()
                    assert isinstance(order_expr,Variable),\
                    "Support for ORDER BY with anything other than a variable is not supported: %s"%order_expr
                    orderBy.append(order_expr)
                    orderAsc.append(orderCond.order == ASCENDING_ORDER)

        if query.query.recurClause is not None:
            recursive_pattern = query.query.recurClause.parsedGraphPattern
            if recursive_pattern is None:
                recursive_expr = expr
            else:
                recursive_expr = reduce(
                  ReduceToAlgebra, recursive_pattern.graphPatterns, None)
            # @@FIXME: unused code
            # initial_recursive_bindings = result.top.bindings.copy()

            def get_recursive_results(recursive_bindings_update, select):
                recursive_bindings = result.top.bindings.copy()
                recursive_bindings.update(recursive_bindings_update)
                if isinstance(recursive_expr, BasicGraphPattern):
                    recursive_top = sparql_query._SPARQLNode(
                      None, recursive_bindings, recursive_expr.patterns,
                      tripleStore, expr=recursive_expr)
                    recursive_top.topLevelExpand(recursive_expr.constraints,
                                                 query.prolog)
                    recursive_result = sparql_query.Query(recursive_top,
                                                   tripleStore)
                else: # recursive_expr should be an AlgebraExpression
                    recursive_result = recursive_expr.evaluate(
                      tripleStore, recursive_bindings, query.prolog)
                return recursive_result.top.returnResult(select)

            recursive_maps = query.query.recurClause.maps
            result.set_recursive(get_recursive_results, recursive_maps)

        topUnionBindings=[]
        selection=result.select(query.query.variables,
             query.query.distinct,
             limit,
             orderBy,
             orderAsc,
             offset
             )
        selectionF = sparql_query._variablesToArray(query.query.variables,"selection")
        if result.get_recursive_results is not None:
            selectionF.append(result.map_from)
        vars = result._getAllVariables()
        if result.parent1 != None and result.parent2 != None :
            topUnionBindings=reduce(lambda x,y:x+y,
                                    [root.returnResult(selectionF) \
                                      for root in fetchUnionBranchesRoots(result)])
        else:
            if (limit == 0 or limit is not None or offset is not None and \
                 offset > 0):
                if prolog.answerList:
                    topUnionBindings = prolog.answerList
                    vars = prolog.answerList[0].keys()
                else:
                    topUnionBindings=[]

            else:
                topUnionBindings=result.top.returnResult(selectionF)
        if result.get_recursive_results is not None:
            topUnionBindings.extend(
              result._recur(topUnionBindings, selectionF))
            selectionF.pop()
        return   selection,\
                 _variablesToArray(query.query.variables,"selection"),\
                 vars,\
                 orderBy,query.query.distinct,\
                 topUnionBindings
    elif isinstance(query.query,DescribeQuery):
        # 10.4.3 Descriptions of Resources

        # The RDF returned is determined by the information publisher.
        # It is the useful information the service has about a resource.
        # It may include information about other resources: for example,
        # the RDF data for a book may also include details about the author.

        # A simple query such as

        # PREFIX ent:  <http://org.example.com/employees#>
        # DESCRIBE ?x WHERE { ?x ent:employeeId "1234" }
        # might return a description of the employee and some other
        # potentially useful details:

        # @prefix foaf:   <http://xmlns.com/foaf/0.1/> .
        # @prefix vcard:  <http://www.w3.org/2001/vcard-rdf/3.0> .
        # @prefix exOrg:  <http://org.example.com/employees#> .
        # @prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        # @prefix owl:    <http://www.w3.org/2002/07/owl#>

        # _:a     exOrg:employeeId    "1234" ;

        #         foaf:mbox_sha1sum   "ABCD1234" ;
        #         vcard:N
        #          [ vcard:Family       "Smith" ;
        #            vcard:Given        "John"  ] .

        # foaf:mbox_sha1sum  rdf:type  owl:InverseFunctionalProperty .
        # which includes the blank node closure for the vcard vocabulary
        # vcard:N.
        # Other possible mechanisms for deciding what information to return
        # include Concise Bounded Descriptions [CBD].

        # For a vocabulary such as FOAF, where the resources are typically
        # blank nodes, returning sufficient information to identify a node
        # such as the InverseFunctionalProperty foaf:mbox_sha1sum as well
        # as information like name and other details recorded would be
        # appropriate. In the example, the match to the WHERE clause was
        # returned, but this is not required.

        def create_result(vars, binding, graph):
            # print("Creating result %s %s %s" % (vars, binding, graph))
            # result,selectionF,allVars,orderBy,distinct,topUnion
            return (graph.n3(), [], vars, limit, offset, [])
        import rdflib
        extensionFunctions = {rdflib.term.URIRef(u'http://www.w3.org/TR/rdf-sparql-query/#describe'): create_result}

        if query.query.solutionModifier.limitClause is not None:
            limit = int(query.query.solutionModifier.limitClause)
        else:
            limit = None
        if query.query.solutionModifier.offsetClause is not None:
            offset = int(query.query.solutionModifier.offsetClause)
        else:
            offset = 0
        if result.parent1 != None and result.parent2 != None :
            rt=(r for r in reduce(lambda x,y:x+y,
                            [root.returnResult(selectionF) \
                              for root in fetchUnionBranchesRoots(result)]))
        elif limit is not None or offset != 0:
            raise NotImplemented("Solution modifiers cannot be used with DESCRIBE")
        else:
            rt=result.top.returnResult(None)
        rtGraph=Graph(namespace_manager=dataset.namespace_manager)
        # print("rt", rt, type(rt))
        for binding in rt: # Doesn't get here with simple test ...
            if binding:
                # print(query.query.describeVars,binding,tripleStore.graph)
                g = extensionFunctions[DESCRIBE](query.query.describeVars,
                                                   binding,
                                                   tripleStore.graph)
                # print("G is %s" % list(g))
                return g
        rtGraph.bind('', 'http://rdflib.net/store#')
        rtGraph.bind('rdfg', 'http://www.w3.org/2004/03/trix/rdfg-1/')
        rtGraph.add((URIRef('http://rdflib.net/store#'+tripleStore.graph.identifier),
                     rdflib.RDF.type,
                     URIRef('http://rdflib.net/store#Store')))
        return rtGraph
    else:
         # 10.2 CONSTRUCT
         # The CONSTRUCT query form returns a single RDF graph specified by a
         # graph template. The result is an RDF graph formed by taking each
         # query solution in the solution sequence, substituting for the
         # variables in the graph template, and combining the triples into a
         # single RDF graph by set union.
        if query.query.solutionModifier.limitClause is not None:
            limit = int(query.query.solutionModifier.limitClause)
        else:
            limit = None
        if query.query.solutionModifier.offsetClause is not None:
            offset = int(query.query.solutionModifier.offsetClause)
        else:
            offset = 0
        if result.parent1 != None and result.parent2 != None :
            rt=(r for r in reduce(lambda x,y:x+y,
                            [root.returnResult(selectionF) \
                              for root in fetchUnionBranchesRoots(result)]))
        elif limit is not None or offset != 0:
            raise NotImplemented("Solution modifiers cannot be used with CONSTRUCT")
        else:
            rt=result.top.returnResult(None)
        rtGraph=Graph(namespace_manager=dataset.namespace_manager)
        for binding in rt:
            for s,p,o,func in ReduceGraphPattern(query.query.triples,prolog).patterns:
                s,p,o=map(lambda x:isinstance(x,Variable) and binding.get(x) or
                                 x,[s,p,o])
                # If any such instantiation produces a triple containing an
                # unbound variable or an illegal RDF construct, such as a
                # literal in subject or predicate position, then that triple
                # is not included in the output RDF graph.
                if not [i for i in [s,p,o] if isinstance(i,Variable)]:
                    rtGraph.add((s,p,o))
        return rtGraph

class AlgebraExpression(object):
    """
    For each symbol in a SPARQL abstract query, we define an operator for
    evaluation. The SPARQL algebra operators of the same name are used
    to evaluate SPARQL abstract query nodes as described in the section
    "Evaluation Semantics".
    """
    def __repr__(self):
        return "%s(%s,%s)"%(self.__class__.__name__,self.left,self.right)

    def evaluate(self,tripleStore,initialBindings,prolog):
        """
        12.5 Evaluation Semantics

        We define eval(D(G), graph pattern) as the evaluation of a graph pattern
        with respect to a dataset D having active graph G. The active graph is
        initially the default graph.
        """
        raise Exception(repr(self))

class EmptyGraphPatternExpression(AlgebraExpression):
    """
    A placeholder for evaluating empty graph patterns - which
    should result in an empty multiset of solution bindings
    """
    def __repr__(self):
        return "EmptyGraphPatternExpression(..)"
    def evaluate(self,tripleStore,initialBindings,prolog):
        # raise NotImplementedError("Empty Graph Pattern expressions, not supported")
        if prolog.DEBUG:
            log.debug("eval(%s,%s,%s)"%(self,initialBindings,tripleStore.graph))
        empty = sparql_query._SPARQLNode(None,{},[],tripleStore)
        empty.bound = False
        return sparql_query.Query(empty, tripleStore)

def fetchUnionBranchesRoots(node):
    for parent in [node.parent1,node.parent2]:
        if parent.parent1:
            for branch_root in fetchUnionBranchesRoots(parent):
                yield branch_root
        else:
            yield parent.top

def fetchChildren(node):
    if isinstance(node,sparql_query._SPARQLNode):
        yield [c for c in node.children]
    elif isinstance(node,sparql_query.Query):
        if node.parent1 is None:
            for c in fetchChildren(node.top):
                yield c
        else:
            for parent in [node.parent1,node.parent2]:
                for c in fetchChildren(parent):
                    yield c

def walktree(top, depthfirst = True, leavesOnly = True, optProxies=False):
    #assert top.parent1 is None
    if isinstance(top,sparql_query._SPARQLNode) and top.clash:
        return
    if not depthfirst and (not leavesOnly or not top.children):
        proxies=False
        for optChild in reduce(lambda x,y: x+y,[list(sparql_query._fetchBoundLeaves(o))
                                        for o in top.optionalTrees],[]):
            proxies=True
            yield optChild
        if not proxies:
            yield top
    children=reduce(lambda x,y:x+y,list(fetchChildren(top)))
    # if isinstance(top,sparql_query._SPARQLNode) \
    #     or isinstance(top,sparql_query.Query) \
    #     and  top.parent1 is None:
    #     children = top.children
    # else:
    #     children = top.parent1.children + top.parent2.children
    for child in children:
        if child.children:
            for newtop in walktree(child, depthfirst,leavesOnly,optProxies):
                yield newtop
        else:
            proxies=False
            for optChild in reduce(lambda x,y: x+y,[list(sparql_query._fetchBoundLeaves(o))
                                            for o in child.optionalTrees],[]):
                proxies=True
                yield optChild
            if not proxies:
                yield child

    if depthfirst and (not leavesOnly or not children):
        proxies=False
        for optChild in reduce(lambda x,y: x+y,[list(sparql_query._fetchBoundLeaves(o))
                                        for o in top.optionalTrees],[]):
            proxies=True
            yield optChild
        if not proxies:
            yield top

def print_tree(node, padding=' '):
    print padding[:-1] + repr(node)
    padding = padding + ' '
    count = 0
    # _children1=reduce(lambda x,y:x+y,list(fetchChildren(node)))
    for child in node.children:# _children1:
        count += 1
        print padding + '|'
        if child.children:
            if count == len(node.children):
                print_tree(child, padding + ' ')
            else:
                print_tree(child, padding + '|')
        else:
            print padding + '+-' + repr(child) + ' ' + repr(dict([(k,v)
                    for k,v in child.bindings.items() if v]))
            optCount=0
            for optTree in child.optionalTrees:
                optCount += 1
                print padding + '||'
                if optTree.children:
                    if optCount == len(child.optionalTrees):
                        print_tree(optTree, padding + ' ')
                    else:
                        print_tree(optTree, padding + '||')
                else:
                    print padding + '+=' + repr(optTree)

    count = 0
    for optTree in node.optionalTrees:
        count += 1
        print padding + '||'
        if optTree.children:
            if count == len(node.optionalTrees):
                print_tree(optTree, padding + ' ')
            else:
                print_tree(optTree, padding + '||')
        else:
            print padding + '+=' + repr(optTree)


def _ExpandJoin(node,expression,tripleStore,prolog,optionalTree=False):
    """
    Traverses to the leaves of expansion trees to implement the Join
    operator
    """
    if prolog.DEBUG:
        print_tree(node)
        log.debug("-------------------")
    # for node in BF_leaf_traversal(node):
    currExpr = expression
    for node in walktree(node):
        if node.clash:
            continue
        assert len(node.children) == 0
        if prolog.DEBUG:
            log.debug("Performing Join(%s,..)"%node)
        if isinstance(currExpr,AlgebraExpression):
            # If an algebra expression, evaluate it passing on the leaf bindings
            if prolog.DEBUG:
                log.debug("passing on bindings to %s\n:%s"%(currExpr,node.bindings.copy()))
            expression = currExpr.evaluate(tripleStore,node.bindings.copy(),prolog)
        else:
            expression = currExpr
        if isinstance(expression,BasicGraphPattern):
            tS = tripleStore
            if hasattr(expression,'tripleStore'):
                if prolog.DEBUG:
                    log.debug("has tripleStore: %s " % expression.tripleStore)
                tS = expression.tripleStore
            if prolog.DEBUG:
                log.debug("Evaluated left node and traversed to leaf, expanding with %s" % expression)
                log.debug(node.tripleStore.graph)
                log.debug("expressions bindings: %s" % sparql_query._createInitialBindings(expression))
                log.debug("node bindings: %s" % node.bindings)
            exprBindings = sparql_query._createInitialBindings(expression)
            exprBindings.update(node.bindings)
            # An indicator for whether this node has any descendant optional
            # expansions we should consider instead in Join(LeftJoin(A,B),X),
            # if the inner LeftJoin is successful, then X is joined against
            # the cumulative bindings ( instead of just A )
            descendantOptionals = node.optionalTrees and \
                [o for o in node.optionalTrees if list(sparql_query._fetchBoundLeaves(o))]
            if not descendantOptionals:
                top = node
            else:
                if prolog.DEBUG:
                    log.debug("descendant optionals: %s" % descendantOptionals)
                top = None
            child = None
            if not node.clash and not descendantOptionals:
                # It has compatible bindings and either no optional expansions
                # or no *valid* optional expansions
                child = sparql_query._SPARQLNode(top,
                                          exprBindings,
                                          expression.patterns,
                                          tS,
                                          expr=node.expr)
                child.topLevelExpand(expression.constraints, prolog)
                if prolog.DEBUG:
                    log.debug("Has compatible bindings and no valid optional expansions")
                    log.debug("Newly bound descendants: ")
                    for c in sparql_query._fetchBoundLeaves(child):
                        log.debug("\t%s %s" % (c, c.bound))
                        log.debug(c.bindings)
        else:
            assert isinstance(expression,sparql_query.Query)
            if not expression.top:
                # Already evaluated a UNION - fetch UNION branches
                child = list(fetchUnionBranchesRoots(expression))
            else:
                # Already been evaluated (non UNION), just attach the SPARQLNode
                child = expression.top
        if isinstance(child,sparql_query._SPARQLNode):
            if node.clash == False and child is not None:
                node.children.append(child)
                if prolog.DEBUG:
                    log.debug("Adding %s to %s (a UNION branch)"%(child,node))
        else:
            assert isinstance(child,list)
            for newChild in child:
                # if not newChild.clash:
                node.children.append(newChild)
                if prolog.DEBUG:
                    log.debug("Adding %s to %s"%(child,node))
        if prolog.DEBUG:
            print_tree(node)
            log.debug("-------------------")
        for optTree in node.optionalTrees:
            #Join the optional paths as well - those that are bound and valid
            for validLeaf in sparql_query._fetchBoundLeaves(optTree):
                _ExpandJoin(validLeaf,
                            expression,
                            tripleStore,
                            prolog,
                            optionalTree=True)

class NonSymmetricBinaryOperator(AlgebraExpression):
    def fetchTerminalExpression(self):
        if isinstance(self.right,BasicGraphPattern):
            yield self.right
        else:
            for i in self.right.fetchTerminalExpression():
                yield i

class Join(NonSymmetricBinaryOperator):
    """
    .. sourcecode:: text

        [[(P1 AND P2)]](D,G) = [[P1]](D,G) compat [[P2]](D,G)

        Join(Ω1, Ω2) = { merge(μ1, μ2) | μ1 in Ω1 and μ2 in Ω2, and μ1 and μ2 are \
                         compatible }

    Pseudocode implementation:

    Evaluate BGP1
    Traverse to leaves (expand and expandOption leaves) of BGP1, set 'rest' to
    triple patterns in BGP2 (filling out bindings).
    Trigger another round of expand / expandOptions (from the leaves)
    """
    def __init__(self,BGP1,BGP2):
        self.left  = BGP1
        self.right = BGP2

    def evaluate(self,tripleStore,initialBindings,prolog):
        if prolog.DEBUG:
            log.debug("eval(%s,%s,%s)"%(self,initialBindings,tripleStore.graph))
        if isinstance(self.left,AlgebraExpression):
            left = self.left.evaluate(tripleStore,initialBindings,prolog)
        else:
            left = self.left
        if isinstance(left,BasicGraphPattern):
            # @@FIXME unused code
            # retval = None
            bindings = sparql_query._createInitialBindings(left)
            if initialBindings:
                bindings.update(initialBindings)
            if hasattr(left,'tripleStore'):
                #Use the prepared tripleStore
                lTS = left.tripleStore
            else:
                lTS = tripleStore
            top = sparql_query._SPARQLNode(None,
                                    bindings,
                                    left.patterns,
                                    lTS,
                                    expr=left)
            top.topLevelExpand(left.constraints, prolog)
            _ExpandJoin(top,self.right,tripleStore,prolog)
            return sparql_query.Query(top, tripleStore)
        else:
            assert isinstance(left,sparql_query.Query), repr(left)
            if left.parent1 and left.parent2:
                #union branch.  We need to unroll all operands (recursively)
                for union_root in fetchUnionBranchesRoots(left):
                    _ExpandJoin(union_root,self.right,tripleStore,prolog)
            else:
                for b in sparql_query._fetchBoundLeaves(left.top):
                    _ExpandJoin(b,self.right,tripleStore,prolog)
            return left

def _ExpandLeftJoin(node,expression,tripleStore,prolog,optionalTree=False):
    """
    Traverses to the leaves of expansion trees to implement the LeftJoin
    operator
    """
    currExpr = expression
    if prolog.DEBUG:
        log.debug("DFS and LeftJoin expansion of ")
        print_tree(node)
        log.debug("---------------------")
        log.debug(node.bindings)
    for node in walktree(node,optProxies=True):
        if node.clash:
            continue
        assert len(node.children) == 0
        # This is a leaf in the original expansion
        if prolog.DEBUG:
            log.debug("Performing LeftJoin(%s,..)"%node)
        if isinstance(currExpr,AlgebraExpression):
            # If a Graph pattern evaluate it passing on the leaf bindings
            # (possibly as solutions to graph names
            if prolog.DEBUG:
                log.debug("evaluating B in LeftJoin(A,B)")
                log.debug("passing on bindings to %s\n:%s"%(
                                    currExpr,node.bindings.copy()))
            expression = currExpr.evaluate(tripleStore,node.bindings.copy(),
                                           prolog)
        else:
            expression = currExpr
        if isinstance(expression,BasicGraphPattern):
            rightBindings = sparql_query._createInitialBindings(expression)
            rightBindings.update(node.bindings)
            optTree = sparql_query._SPARQLNode(None,
                                        rightBindings,
                                        expression.patterns,
                                        tripleStore,
                                        expr=expression)
            if prolog.DEBUG:
                log.debug("evaluating B in LeftJoin(A,B) - a BGP: %s" % expression)
                log.debug("Passing on bindings %s" % rightBindings)
            optTree.topLevelExpand(expression.constraints, prolog)
            for proxy in sparql_query._fetchBoundLeaves(optTree):
                # Mark a successful evaluation of LeftJoin (new bindings were added)
                # these become proxies for later expressions
                proxy.priorLeftJoin=True
        else:
            if prolog.DEBUG:
                log.debug("Attaching previously evaluated node: %s" % expression.top)
            assert isinstance(expression,sparql_query.Query)
            if not expression.top:
                # Already evaluated a UNION - fetch UNION branches
                optTree = list(fetchUnionBranchesRoots(expression))
            else:
                # Already been evaluated (non UNION), just attach the SPARQLNode
                optTree = expression.top
        if prolog.DEBUG:
            log.debug("Optional tree: %s" % optTree)
        if isinstance(optTree,sparql_query._SPARQLNode):
            if optTree.clash == False and optTree is not None:
                node.optionalTrees.append(optTree)
                if prolog.DEBUG:
                    log.debug("Adding %s to %s (a UNION branch)"%(
                                optTree, node.optionalTrees))
        else:
            assert isinstance(optTree,list)
            for newChild in optTree:
                # if not newChild.clash:
                node.optionalTrees.append(newChild)
                if prolog.DEBUG:
                    log.debug("Adding %s to %s"%(newChild,node.optionalTrees))
        if prolog.DEBUG:
            log.debug("DFS after LeftJoin expansion ")
            print_tree(node)
            log.debug("---------------------")


class LeftJoin(NonSymmetricBinaryOperator):
    """
    .. code-block:: text

        Let Ω1 and Ω2 be multisets of solution mappings and F a filter. We define:
        LeftJoin(Ω1, Ω2, expr) =
            Filter(expr, Join(Ω1, Ω2)) set-union Diff(Ω1, Ω2, expr)

        LeftJoin(Ω1, Ω2, expr) =
        { merge(μ1, μ2) | μ1 in Ω1 and μ2 in Ω2, and
                          μ1 and μ2 are compatible, and
                          expr(merge(μ1, μ2)) is true }
        set-union
        { μ1 | μ1 in Ω1 and μ2 in Ω2, and
               μ1 and μ2 are not compatible }
        set-union
        { μ1 | μ1 in Ω1and μ2 in Ω2, and μ1 and μ2 are compatible and
               expr(merge(μ1, μ2)) is false }

    """
    def __init__(self,BGP1,BGP2,expr=None):
        self.left  = BGP1
        self.right = BGP2

    def evaluate(self,tripleStore,initialBindings,prolog):
        if prolog.DEBUG:
            log.debug("eval(%s,%s,%s)"%(self,initialBindings,tripleStore.graph))
        if isinstance(self.left,AlgebraExpression):
            #print "evaluating A in LeftJoin(A,B) - an expression"
            left = self.left.evaluate(tripleStore,initialBindings,prolog)
        else:
            left = self.left
        if isinstance(left,BasicGraphPattern):
            # print "expanding A in LeftJoin(A,B) - a BGP: ", left
            # @@FIXME: unused code
            # retval = None
            bindings = sparql_query._createInitialBindings(left)
            if initialBindings:
                bindings.update(initialBindings)
            if hasattr(left,'tripleStore'):
                #Use the prepared tripleStore
                tripleStore = left.tripleStore
            top = sparql_query._SPARQLNode(None,
                                    bindings,
                                    left.patterns,
                                    tripleStore,
                                    expr=left)
            top.topLevelExpand(left.constraints, prolog)
            for b in sparql_query._fetchBoundLeaves(top):
                _ExpandLeftJoin(b,self.right,tripleStore,prolog)
            #_ExpandLeftJoin(top,self.right,tripleStore,prolog)
            return sparql_query.Query(top, tripleStore)
        else:
            assert isinstance(left,sparql_query.Query), repr(left)
            if left.parent1 and left.parent2:
                for union_root in fetchUnionBranchesRoots(left):
                    _ExpandLeftJoin(union_root,self.right,tripleStore,prolog)
            else:
                for b in sparql_query._fetchBoundLeaves(left.top):
                    _ExpandLeftJoin(b,self.right,tripleStore,prolog)
            #_ExpandLeftJoin(left.top,self.right,tripleStore,prolog)
            return left

class Union(AlgebraExpression):
    """
    II. [[(P1 UNION P2)]](D,G) = [[P1]](D,G) OR [[P2]](D,G)

    Union(Ω1, Ω2) = { μ | μ in Ω1 or μ in Ω2 }

    """
    def __init__(self,BGP1,BGP2):
        self.left  = BGP1
        self.right = BGP2

    def fetchTerminalExpression(self):
        for item in [self.left,self.right]:
            if isinstance(item,BasicGraphPattern):
                yield item
            else:
                for i in item.fetchTerminalExpression():
                    yield i

    def evaluate(self,tripleStore,initialBindings,prolog):
        if prolog.DEBUG:
            log.debug("eval(%s,%s,%s)"%(self,initialBindings,tripleStore.graph))
        if isinstance(self.left,AlgebraExpression):
            left = self.left.evaluate(tripleStore,initialBindings,prolog)
        else:
            left = self.left
        if isinstance(left,BasicGraphPattern):
            # The left expression has not been evaluated
            # @@FIXME: unused code
            # retval = None
            bindings = sparql_query._createInitialBindings(left)
            if initialBindings:
                bindings.update(initialBindings)
            top = sparql_query._SPARQLNode(None,
                                    bindings,
                                    left.patterns,
                                    tripleStore,
                                    expr=left)
            top.topLevelExpand(left.constraints, prolog)
            top = sparql_query.Query(top, tripleStore)
        else:
            #The left expression has already been evaluated
            assert isinstance(left,sparql_query.Query), repr(left)
            top = left
        #Now we evaluate the right expression (independently)
        if isinstance(self.right,AlgebraExpression):
            #If it is a GraphExpression, 'reduce' it
            right = self.right.evaluate(tripleStore,initialBindings,prolog)
        else:
            right = self.right
        tS = tripleStore
        if isinstance(right,BasicGraphPattern):
            if hasattr(right,'tripleStore'):
                tS = right.tripleStore
            rightBindings = sparql_query._createInitialBindings(right)
            if initialBindings:
                rightBindings.update(initialBindings)
            rightNode = sparql_query._SPARQLNode(None,
                                          rightBindings,
                                          right.patterns,
                                          tS,
                                          expr=right)
            rightNode.topLevelExpand(right.constraints, prolog)
        else:
            assert isinstance(right,sparql_query.Query), repr(right)
            rightNode = right.top
        # if prolog.DEBUG:
        #    print "### Two UNION trees ###"
        #    print self.left
        #    print_tree(top.top)
        #    print self.right
        #    print_tree(rightNode)
        #    print "#######################"

        #The UNION semantics are implemented by the overidden __add__ method
        return top + sparql_query.Query(rightNode, tS)

class GraphExpression(AlgebraExpression):
    """
    .. sourcecode:: text

        [24] GraphGraphPattern ::=  'GRAPH'  VarOrIRIref  GroupGraphPattern
        eval(D(G), Graph(IRI,P)) = eval(D(D[i]), P)
        eval(D(G), Graph(var,P)) =
            multiset-union over IRI i in D : Join( eval(D(D[i]), P) , Omega(?v->i) )

    """
    def __init__(self,iriOrVar,GGP):
        self.iriOrVar  = iriOrVar
        self.GGP = GGP

    def __repr__(self):
        return "Graph(%s,%s)"%(self.iriOrVar,self.GGP)

    def fetchTerminalExpression(self):
        if isinstance(self.GGP,BasicGraphPattern):
            yield self.GGP
        else:
            for i in self.GGP.fetchTerminalExpression():
                yield i

    def evaluate(self,tripleStore,initialBindings,prolog):
        """
        The GRAPH keyword is used to make the active graph one of all of the
        named graphs in the dataset for part of the query.
        """
        if prolog.DEBUG:
            log.debug("eval(%s,%s,%s)"%(self,initialBindings,tripleStore.graph))
        if isinstance(self.iriOrVar,Variable):
            #A variable:
            if self.iriOrVar in initialBindings:
                #assert initialBindings[self.iriOrVar], "Empty binding for GRAPH variable!"
                if prolog.DEBUG:
                    log.debug("Passing on unified graph name: %s" % initialBindings[self.iriOrVar])
                tripleStore = graph.SPARQLGraph(
                                            Graph(tripleStore.graph.store,
                                                  initialBindings[self.iriOrVar])
                                            ,dSCompliance=DAWG_DATASET_COMPLIANCE)
            else:
                if prolog.DEBUG:
                    log.debug("Setting up BGP to return additional bindings for %s"%self.iriOrVar)
                tripleStore = graph.SPARQLGraph(tripleStore.graph,
                                                      graphVariable = self.iriOrVar,
                                                      dSCompliance=DAWG_DATASET_COMPLIANCE)
        else:
            graphName =  self.iriOrVar
            graphName  = convertTerm(graphName,prolog)
            if isinstance(tripleStore.graph,ReadOnlyGraphAggregate):
                targetGraph = [g for g in tripleStore.graph.graphs
                                 if g.identifier == graphName]
                #assert len(targetGraph) == 1
                targetGraph = targetGraph[0]
            else:
                targetGraph = Graph(tripleStore.graph.store,graphName)
            tripleStore = graph.SPARQLGraph(targetGraph,
                                                  dSCompliance=\
                                                  DAWG_DATASET_COMPLIANCE)
        if isinstance(self.GGP,AlgebraExpression):
            #Dont evaluate
            return self.GGP.evaluate(tripleStore,initialBindings,prolog)
        else:
            assert isinstance(self.GGP,BasicGraphPattern),repr(self.GGP)
            #Attach the prepared triple store to the BGP
            self.GGP.tripleStore = tripleStore
            return self.GGP

if __name__ == '__main__':
    unittest.main()

# from rdfextras.sparql.algebra import ReduceGraphPattern
# from rdfextras.sparql.algebra import ReduceToAlgebra
# from rdfextras.sparql.algebra import RenderSPARQLAlgebra
# from rdfextras.sparql.algebra import LoadGraph
# from rdfextras.sparql.algebra import TopEvaluate
# from rdfextras.sparql.algebra import fetchUnionBranchesRoots
# from rdfextras.sparql.algebra import fetchChildren
# from rdfextras.sparql.algebra import walktree
# from rdfextras.sparql.algebra import print_tree
# from rdfextras.sparql.algebra import AlgebraExpression
# from rdfextras.sparql.algebra import EmptyGraphPatternExpression
# from rdfextras.sparql.algebra import NonSymmetricBinaryOperator
# from rdfextras.sparql.algebra import Join
# from rdfextras.sparql.algebra import LeftJoin
# from rdfextras.sparql.algebra import Union
# from rdfextras.sparql.algebra import GraphExpression

