.. _rdfextras_tools_csv2rdf: RDFExtras tools CSV to RDF

|today|

=======
CSV2RDF
=======

csv2rdf.py -b <instance-base> -p <property-base> [-c <classname>] [-i <identity column(s)>] [-l <label columns>] [-s <N>] [-o <output>] [-f configfile] [--col<N> <colspec>] [--prop<N> <property>] <[-d <delim>] [-C] [files...]"

.. code-block:: text

    Reads csv files from stdin or given files
    
    if -d is given, use this delimiter
    
    if -s is given, skips N lines at the start
    
    Creates a URI from the columns given to -i, or automatically by
    numbering if none is given
    
    Outputs RDFS labels from the columns given to -l
    
    if -c is given adds a type triple with the given classname 
    
    if -C is given, the class is defined as rdfs:Class
    
    Outputs one RDF triple per column in each row. 
    
    Output is in n3 format. 
    
    Output is stdout, unless -o is specified

Long options also supported: --base, --propbase, --ident, --class, --label, 
--out, --defineclass

Long options --col0, --col1, ... can be used to specify conversion for 
columns. Conversions can be: float(), int(), split(sep, [more]), 
uri(base, [class]), date(format) 

Long options --prop0, --prop1, ... can be used to use specific properties,
rather than ones auto-generated from the headers

-f says to read config from a .ini/config file - the file must contain one
section called ``csv2rdf``, with keys like the long options, i.e.: 

.. code-block:: ini

    [csv2rdf]
    out=output.n3
    base=http://example.org/
    col0=split(";")
    col1=split(";", uri("http://example.org/things/","http://xmlns.com/foaf/0.1/Person"))
    col2=float()
    col3=int()
    col4=date("%Y-%b-%d %H:%M:%S")


.. currentmodule:: rdfextras.tools

.. automodule:: rdfextras.tools.csv2rdf
   
.. autoclass:: CSV2RDF
   :members:
