"""
RDF- and RDFlib-centric Graph utilities.
"""
def graph_to_dot(graph, dot):
    """ Turns graph into dot (graphviz graph drawing format) using pydot. """
    import pydot
    nodes = {}
    for s, o in graph.subject_objects():
        for i in s,o:
            if i not in nodes.keys():
                nodes[i] = i
    for s, p, o in graph.triples((None,None,None)):
        dot.add_edge(pydot.Edge(nodes[s], nodes[o], label=p))


def find_roots(graph,prop,roots=None): 
    """
    Find the roots in some sort of transitive hierarchy. 
    
    find_roots(graph, rdflib.RDFS.subClassOf) 
    will return a set of all roots of the sub-class hierarchy

    Assumes triple of the form (child, prop, parent), i.e. the direction of 
    RDFS.subClassOf or SKOS.broader 

    """

    non_roots=set()
    if roots==None: roots=set()
    for x,y in graph.subject_objects(prop): 
        non_roots.add(x)
        if x in roots: roots.remove(x)
        if y not in non_roots: 
            roots.add(y)
    return roots

def get_tree(graph, root, prop, mapper=lambda x:x, done=None, dir='down' ): 
    """
    Return a nested list/tuple structure representing the tree 
    built by the transitive property given, starting from the root given

    i.e. 
    
    get_tree(graph, 
       rdflib.URIRef("http://xmlns.com/foaf/0.1/Person"), 
       rdflib.RDFS.subClassOf) 

    will return the structure for the subClassTree below person.

    dir='down' assumes triple of the form (child, prop, parent), 
    i.e. the direction of RDFS.subClassOf or SKOS.broader 
    Any other dir traverses in the other direction
        
    """

    if done==None: done=set()
    if root in done: return
    done.add(root)
    tree=[]

    if dir=='down':
        branches=graph.subjects(prop,root)
    else:
        branches=graph.objects(root,prop)

    for branch in branches: 
        t=get_tree(graph, branch, prop, mapper, done, dir)
        if t: tree.append(t)

    return ( mapper(root), tree )
