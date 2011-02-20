import rdflib
import StringIO

bookrdf="""@prefix dc: <http://purl.org/dc/elements/1.1/> .\n@prefix vcard: <http://www.w3.org/2001/vcard-rdf/3.0#> .\n\n<http://example.org/book/book1> dc:creator "J.K. Rowling";\n    dc:title "Harry Potter and the Philosopher\'s Stone" .\n\n<http://example.org/book/book2> dc:creator _:RDhmeZZC15;\n    dc:title "Harry Potter and the Chamber of Secrets" .\n\n<http://example.org/book/book3> dc:creator _:RDhmeZZC15;\n    dc:title "Harry Potter and the Prisoner Of Azkaban" .\n\n<http://example.org/book/book4> dc:title "Harry Potter and the Goblet of Fire" .\n\n<http://example.org/book/book5> dc:creator "J.K. Rowling";\n    dc:title "Harry Potter and the Order of the Phoenix" .\n\n<http://example.org/book/book6> dc:creator "J.K. Rowling";\n    dc:title "Harry Potter and the Half-Blood Prince" .\n\n<http://example.org/book/book7> dc:creator "J.K. Rowling";\n    dc:title "Harry Potter and the Deathly Hallows" .\n\n_:RDhmeZZC16 vcard:Family "Rowling";\n    vcard:Given "Joanna" .\n\n_:RDhmeZZC15 vcard:FN "J.K. Rowling";\n    vcard:N _:RDhmeZZC16 .\n\n"""

bookdb=rdflib.Graph()
bookdb.load(StringIO.StringIO(bookrdf),format='n3')
