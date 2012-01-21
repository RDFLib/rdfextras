import sys, os, time, datetime

ns_rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
ns_rdfs = "http://www.w3.org/2000/01/rdf-schema#"

##########################################################################
# XML Schema datatypes
type_integer  = "http://www.w3.org/2001/XMLSchema#integer"
type_double   = "http://www.w3.org/2001/XMLSchema#double"
type_float    = "http://www.w3.org/2001/XMLSchema#float"
type_decimal  = "http://www.w3.org/2001/XMLSchema#decimal"
type_dateTime = "http://www.w3.org/2001/XMLSchema#dateTime"


from rdflib import Namespace

ns_foaf   = Namespace("http://xmlns.com/foaf/0.1/")
ns_ns     = Namespace("http://example.org/ns#")
ns_book   = Namespace("http://example.org/book")
ns_person = Namespace("http://example.org/person#")
ns_dt     = Namespace("http://example.org/datatype#")
ns_dc0    = Namespace("http://purl.org/dc/elements/1.0/")
ns_dc     = Namespace("http://purl.org/dc/elements/1.1/")
ns_vcard  = Namespace("http://www.w3.org/2001/vcard-rdf/3.0#")

