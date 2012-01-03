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
