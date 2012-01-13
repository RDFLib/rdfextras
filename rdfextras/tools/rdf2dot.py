#!/usr/bin/env python

import rdflib
import rdfextras, rdfextras.tools

import sys
import cgi
import collections

from rdflib import XSD, RDFS


XSDTERMS=[ XSD[x] for x in "anyURI", "base64Binary", "boolean", "byte", "date", "dateTime", "decimal", "double", "duration", "float", "gDay", "gMonth", "gMonthDay", "gYear", "gYearMonth", "hexBinary", "ID", "IDREF", "IDREFS", "int", "integer", "language", "long", "Name", "NCName", "negativeInteger", "NMTOKEN", "NMTOKENS", "nonNegativeInteger", "nonPositiveInteger", "normalizedString", "positiveInteger", "QName", "short", "string", "time", "token", "unsignedByte", "unsignedInt", "unsignedLong", "unsignedShort" ]

EDGECOLOR="blue"
NODECOLOR="black"
ISACOLOR="black"

def rdf2dot(g, stream, opts={}):
    """
    Convert the RDF graph to DOT
    writes the dot output to the stream
    """

    fields=collections.defaultdict(set)
    nodes={}
    def node(x): 

        if x not in nodes: 
            nodes[x]="node%d"%len(nodes)
        return nodes[x]

    def label(x,g): 

        l=g.value(x,RDFS.label)
        if l==None: 
            try: 
                l=g.namespace_manager.compute_qname(x)[2]
            except: 
                pass
        return l

    def formatliteral(l,g):
        v=cgi.escape(l)
        if l.datatype: 
            return u'&quot;%s&quot;^^%s'%(v,qname(l.datatype,g))
        elif l.language: 
            return u'&quot;%s&quot;@%s'%(v,l.language)
        return u'&quot;%s&quot;'%v

    def qname(x,g): 
        try: 
            q=g.compute_qname(x)
            return q[0]+":"+q[2]
        except: 
            return x

    def color(p): 
        return "BLACK"

    stream.write(u"digraph { \n node [ fontname=\"DejaVu Sans\" ] ; \n")

    for s,p,o in g:
        sn=node(s)
        if isinstance(o, (rdflib.URIRef,rdflib.BNode)): 
            on=node(o)
            stream.write(u"\t%s -> %s [ color=%s, label=< <font point-size='10' color='#336633'>%s</font> > ] ;\n"%(sn,on, color(p), qname(p,g)))
        else: 
            fields[sn].add((qname(p,g),formatliteral(o,g)))
        
    for u,n in nodes.items():
        stream.write(u"# %s %s\n"%(u,n))
        f=[u"<tr><td align='left'>%s</td><td align='left'>%s</td></tr>"%x for x in sorted(fields[n])]
        stream.write(u"%s [ shape=none, color=%s label=< <table color='#666666' cellborder='0' cellspacing='0' border='1'><tr><td colspan='2' bgcolor='grey'><B>%s</B></td></tr><tr><td href='%s' bgcolor='#eeeeee' colspan='2'><font point-size='10' color='#6666ff'>%s</font></td></tr>%s</table> > ] \n"%(n, NODECOLOR, label(u,g), u, u, u"".join(f)))

    stream.write("}\n")


def _help(): 
    sys.stderr.write("""
rdf2dot.py [-f <format>] files...
Read RDF files given on STDOUT, writes a graph of the RDFS schema in DOT language to stdout
-f specifies parser to use, if not given, 

""")

if __name__=='__main__':
    rdfextras.tools.cmdline.main(rdf2dot, _help)
