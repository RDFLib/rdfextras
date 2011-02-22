import rdflib
import StringIO

bookrdf="""
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix book: <http://example.org/book/> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix vcard: <http://www.w3.org/2001/vcard-rdf/3.0#> .

<http://example.org/book/book1> a book:Book ; 
    dc:creator "J.K. Rowling";
    dc:title "Harry Potter and the Philosopher\'s Stone" .

<http://example.org/book/book2> a book:Book ;
    dc:creator _:RDhmeZZC15;
    dc:title "Harry Potter and the Chamber of Secrets" .

<http://example.org/book/book3> a book:Book ;
    dc:creator _:RDhmeZZC15;
    dc:title "Harry Potter and the Prisoner Of Azkaban" .

<http://example.org/book/book4> dc:title "Harry Potter and the Goblet of Fire" .

<http://example.org/book/book5> a book:Book ;
    dc:creator "J.K. Rowling";
    dc:title "Harry Potter and the Order of the Phoenix" .

<http://example.org/book/book6> a book:Book ;
    dc:creator "J.K. Rowling";
    dc:title "Harry Potter and the Half-Blood Prince" .

<http://example.org/book/book7> a book:Book ;
    dc:creator "J.K. Rowling";
    dc:title "Harry Potter and the Deathly Hallows" .

_:RDhmeZZC16 vcard:Family "Rowling";
    vcard:Given "Joanna" .

_:RDhmeZZC15 vcard:FN "J.K. Rowling";
    vcard:N _:RDhmeZZC16 .

"""

bookdb=rdflib.Graph()
bookdb.load(StringIO.StringIO(bookrdf),format='n3')
