<?xml version="1.0" ?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:earl="http://www.w3.org/2001/03/earl/0.95#" 
    xmlns:dc="http://purl.org/dc/elements/1.1/" 
    xmlns:foaf="http://xmlns.com/0.1/foaf/" 
    xmlns="http://www.w3.org/1999/xhtml" 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >

<!-- A neat little XSLT file for scraping XHTML from EARL XML RDF files -->

<xsl:param name="xmlfile"/>

<xsl:template match="/">
   <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
       <title>EARL Output</title>
       <link rel="stylesheet" type="text/css" 
             href="http://web.archive.org/web/20011124104053/http://infomesh.net/sbp/style.css" />
     </head>
     <body>
        <h1>EARL Output</h1>
        <h2>Source: <xsl:value-of select="$xmlfile"/></h2>
        <xsl:apply-templates/>
        <p>Transformed by the <a 
           href="http://infomesh.net/2001/09/earl/earl2xhtml.xsl">EARL 
           XSLT deeley</a>.</p>
        <address>
           <a href="http://purl.org/net/sbp/">Sean B. Palmer</a>
        </address>
     </body>
   
</html>
</xsl:template>

<xsl:template match="/rdf:RDF/earl:Tool">
 <h2>Tool(s)</h2>
 <dl>
  <dt>Id</dt><dd><xsl:value-of select="(@rdf:about)"/></dd>
  <xsl:for-each select=".//earl:name">
  <dt>Name</dt><dd><xsl:value-of select="(.)"/></dd>
  </xsl:for-each>
  <xsl:for-each select=".//earl:testSubject">
  <dt>URI</dt><dd><a><xsl:attribute name="href" 
     value="@rdf:resource"/><xsl:value-of 
     select="(@rdf:resource)"/></a></dd>
  </xsl:for-each>
  <xsl:for-each select=".//earl:date">
  <dt>Date</dt><dd><xsl:value-of select="(.)"/></dd>
  </xsl:for-each>
  </dl>
</xsl:template>

<xsl:template match="/rdf:RDF/earl:Assertor">
 <h2>Assertor/Assertions</h2>
 <dl>
  <xsl:if 
  test=".//rdf:type[@rdf:resource='http://www.w3.org/2001/03/earl/0.95#Person']">
  <dt>Person</dt><dd><xsl:for-each select=".//earl:name"><xsl:value-of 
   select="(.)"/></xsl:for-each><xsl:for-each select=".//foaf:mbox"> &#32; 
   &lt;<a><xsl:attribute name="href"><xsl:value-of 
   select="(@rdf:resource)"/></xsl:attribute><xsl:value-of 
   select="substring-after(@rdf:resource,':')"/></a>&gt;</xsl:for-each></dd>
  </xsl:if>
  <xsl:for-each select=".//earl:date">
  <dt>Date</dt><dd><xsl:value-of select="(.)"/></dd>
  </xsl:for-each>
  </dl>
  <xsl:if test=".//earl:asserts">
  <h3>asserts...</h3>
  <xsl:apply-templates/>
  </xsl:if>
</xsl:template>

<xsl:template match="//earl:asserts">
   <div><xsl:for-each select=".//rdf:subject">
   <code><xsl:value-of select="(@rdf:resource)"/></code> - 
   </xsl:for-each>
   <xsl:for-each select=".//rdf:predicate">
   <a><xsl:attribute name="href"><xsl:value-of 
     select="(@rdf:resource)"/></xsl:attribute><xsl:value-of 
     select="substring-after(@rdf:resource,'#')"/></a> - 
   </xsl:for-each>
   <xsl:for-each select=".//rdf:object">
    <xsl:call-template name="testId"><xsl:with-param 
     name="id" select="(@rdf:resource)"/></xsl:call-template>
   </xsl:for-each></div>
</xsl:template>

<xsl:template name="testId">
<xsl:param name="id"/>
<xsl:choose>
<xsl:when test="//rdf:Description[@rdf:about=$id]">
<xsl:for-each select="//rdf:Description[@rdf:about=$id]">
<xsl:for-each select=".//earl:testId">
   <a><xsl:attribute name="href"><xsl:value-of 
     select="(@rdf:resource)"/></xsl:attribute>
   <xsl:choose><xsl:when test="contains($id,'#')"><xsl:value-of 
     select="substring-after($id,'#')"/></xsl:when><xsl:otherwise><xsl:value-of 
     select="$id"/></xsl:otherwise></xsl:choose></a>
</xsl:for-each>
</xsl:for-each>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="$id"/>
</xsl:otherwise>
</xsl:choose>
</xsl:template>

<!-- Don't pass text through -->
<xsl:template match="text()|@*">
</xsl:template>
</xsl:stylesheet>
