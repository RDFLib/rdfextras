from rdflib.query import ResultSerializer
from rdflib.serializer import Serializer

import warnings

from jinja2 import Template


GRAPH_TEMPLATE="""
<table>
<thead>
 <tr>
  <th>subject</th>
  <th>predicate</th>
  <th>object</th>
 </tr>
</thead>
<tbody>
 {% for t in graph %}
  <tr>
  {% for x in t %}
   <td>{{x}}</td>
  {% endfor %}
  </tr>
 {% endfor %}
</tbody>
</table>
"""

SELECT_TEMPLATE="""
<table>
<thead>
 <tr>
 {% for var in result.vars %}
  <th>{{var}}</th>
 {% endfor %}
 </tr>
</thead>
<tbody>
 {% for row in result.bindings %}
  <tr>
  {% for var in result.vars %}
   <td>{{row[var]}}</td>
  {% endfor %}
  </tr>
 {% endfor %}
</tbody>
</table>

"""
class HTMLResultSerializer(ResultSerializer):

    def __init__(self, result): 
        ResultSerializer.__init__(self, result)

    def serialize(self, stream, encoding="utf-8"):
        if self.result.type=='ASK':
            stream.write("<strong>true</strong>".encode(encoding))
            return
        if self.result.type=='SELECT':
            template = Template(SELECT_TEMPLATE)
            stream.write(template.render(result=self.result).encode(encoding))


            



class HTMLSerializer(Serializer):
    """
    Serializes RDF graphs as HTML tables
    """

    def serialize(self, stream, base=None, encoding=None, **args):
        if base is not None:
            warnings.warn("HTMLSerializer does not support base.")
        if encoding is not None:
            warnings.warn("HTMLSerializer does not use custom encoding.")

        template = Template(GRAPH_TEMPLATE)
        stream.write(template.render(graph=self.store).encode(encoding))


