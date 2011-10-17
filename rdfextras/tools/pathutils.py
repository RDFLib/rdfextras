"""
RDF- and RDFlib-centric file and URL path utilities.
"""

from os.path import splitext
import sys
import getopt
import rdflib
import codecs

def uri_leaf(uri):
    """
    Get the "leaf" - fragment id or last segment - of a URI. Useful e.g. for
    getting a term from a "namespace like" URI. Examples:

        >>> uri_leaf('http://example.org/ns/things#item')
        'item'
        >>> uri_leaf('http://example.org/ns/stuff/item')
        'item'
        >>> uri_leaf('http://example.org/ns/stuff/')
        ''
    """
    return uri.rsplit('/', 1)[-1].rsplit('#', 1)[-1]


SUFFIX_FORMAT_MAP = {
    'rdf': 'xml',
    'rdfs': 'xml',
    'owl': 'xml',
    'n3': 'n3',
    'ttl': 'n3',
    'nt': 'nt',
    'trix': 'trix',
    'xhtml': 'rdfa',
    'html': 'rdfa',
    'svg': 'rdfa',
    'nq': 'nquads',
    'trig': 'trig'
}

def guess_format(fpath, fmap=None):
    """
    Guess RDF serialization based on file suffix. Uses
    ``SUFFIX_FORMAT_MAP`` unless ``fmap`` is provided. Examples:

        >>> guess_format('path/to/file.rdf')
        'xml'
        >>> guess_format('path/to/file.owl')
        'xml'
        >>> guess_format('path/to/file.ttl')
        'n3'
        >>> guess_format('path/to/file.xhtml')
        'rdfa'
        >>> guess_format('path/to/file.svg')
        'rdfa'
        >>> guess_format('path/to/file.xhtml', {'xhtml': 'grddl'})
        'grddl'

    This also works with just the suffixes, with or without leading dot, and
    regardless of letter case::

        >>> guess_format('.rdf')
        'xml'
        >>> guess_format('rdf')
        'xml'
        >>> guess_format('RDF')
        'xml'
    """
    fmap = fmap or SUFFIX_FORMAT_MAP
    return fmap.get(_get_ext(fpath)) or fmap.get(fpath.lower()) 


def _get_ext(fpath, lower=True):
    """
    Gets the file extension from a file(path); stripped of leading '.' and in
    lower case. Examples:

        >>> _get_ext("path/to/file.txt")
        'txt'
        >>> _get_ext("OTHER.PDF")
        'pdf'
        >>> _get_ext("noext")
        ''
        >>> _get_ext(".rdf")
        'rdf'
    """
    ext = splitext(fpath)[-1]
    if ext == '' and fpath.startswith("."): 
        ext = fpath
    if lower:
        ext = ext.lower()
    if ext.startswith('.'):
        ext = ext[1:]
    return ext

def _help(): 
    sys.stderr.write("""
program.py [-f <format>] [-o <output>] [files...]
Read RDF files given on STDOUT - does something to the resulting graph
If no files are given, read from stdin
-o specifies file for output, if not given stdout is used
-f specifies parser to use, if not given it is guessed from extension

""")
    

def main(target, _help=_help): 
    args, files=getopt.getopt(sys.argv[1:], "hf:o:")
    args=dict(args)

    if "-h" in args: 
        _help()
        sys.exit(-1)
                     
    g=rdflib.Graph()

    if "-f" in args: 
        f=args["-f"]
    else: 
        f=None

    if "-o" in args: 
        sys.stderr.write("Output to %s\n"%args["-o"])
        out=codecs.open(args["-o"], "w","utf-8")
    else: 
        out=sys.stdout

    if len(files)==0: 
        sys.stderr.write("Reading RDF/XML from stdin...\n")
        g.load(sys.stdin, format="xml")
    else: 
        for x in files:
            f=guess_format(x)
            sys.stderr.write("Loading %s as %s... "%(x,f))
            g.load(x, format=f)
            sys.stderr.write("[done]\n")

    sys.stderr.write("Loaded %d triples.\n"%len(g))
    
    target(g,out)


