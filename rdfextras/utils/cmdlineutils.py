import sys
import getopt
import rdflib
import codecs

from rdfextras.utils.pathutils import guess_format

def _help(): 
    sys.stderr.write("""
program.py [-f <format>] [-o <output>] [files...]
Read RDF files given on STDOUT - does something to the resulting graph
If no files are given, read from stdin
-o specifies file for output, if not given stdout is used
-f specifies parser to use, if not given it is guessed from extension

""")
    

def main(target, _help=_help, options="", stdin=True): 
    """
    A main function for tools that read RDF from files given on commandline
    or from STDIN (if stdin parameter is true)
    """

    args, files=getopt.getopt(sys.argv[1:], "hf:o:"+options)
    dargs=dict(args)

    if "-h" in dargs: 
        _help()
        sys.exit(-1)
                     
    g=rdflib.Graph()

    if "-f" in dargs: 
        f=dargs["-f"]
    else: 
        f=None

    if "-o" in dargs: 
        sys.stderr.write("Output to %s\n"%dargs["-o"])
        out=codecs.open(dargs["-o"], "w","utf-8")
    else: 
        out=sys.stdout

    if len(files)==0 and stdin: 
        sys.stderr.write("Reading from stdin...\n")
        g.load(sys.stdin, format=f)
    else: 
        for x in files:
            if f==None: 
                f=guess_format(x)
            sys.stderr.write("Loading %s as %s... "%(x,f))
            g.load(x, format=f)
            sys.stderr.write("[done]\n")

    sys.stderr.write("Loaded %d triples.\n"%len(g))
    
    target(g,out,args)


