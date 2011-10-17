<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0"
    xmlns="http://www.w3.org/1999/xhtml"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xunit="http://reflex.gforge.inria.fr/xunit.html"
>

    <xsl:template match="/">
        <html>
            <head>
                <title>XUnit report</title>
                <style type="text/css">
table.xunit, table.xunit tr, table.xunit th, table.xunit td {
    border: thin solid #000099;
    border-collapse: collapse;
    border-spacing: 0
}
table.xunit th {
    background-color: #000099;
    color: white;
    padding-left: 10px;
    padding-right: 10px;
}
table.xunit th.head {
    border: 3px groove #000099
}
strike { color: #bbb;}
pre.console {
    background-color: #090909;
    border-color: #808080;
    color: #EEEEFF;
    width: 100%;
    max-height:350px;
    overflow:auto;
}
.select {
    background: #DDDDFF;
}
span.fail { color: #0000ff}
span.error { color: #ff0000}
span.pass {color: #00ff00}
                </style>
            </head>
            <body>
                <h1>XUnit report</h1>
                <xsl:call-template name="xunit:html-report"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template name="xunit:html-report">
        <!-- <xsl:param name="report" select="."/> -->

        <table class="xunit" width="100%">
            <tr><th class="xunit">&#160;</th><th><div style="float: right; padding-left: 10px">Skip</div>Test name</th><th class="xunit">Tests</th><th class="xunit">Errors</th><th class="xunit">Failure</th></tr>
            <!-- <xsl:apply-templates select="$report" mode="xunit"/> -->
            <xsl:apply-templates mode="xunit"/>
        </table>
    </xsl:template>

    <xsl:template match="testsuite" mode="xunit">
        <tr>
            <td colspan="2" class="select" valign="top">
                <div style="float: right; padding-left: 10px"><xsl:value-of select="@skip"/><xsl:comment>skip</xsl:comment></div>
                <xsl:value-of select="@name"/>
            </td>
            <td class="select" style="text-align: right">
                <xsl:value-of select="@testcases"/><br/>
                (<xsl:value-of select="@tests"/>)</td>
            <td class="select" style="text-align: right">
                <xsl:value-of select="@errors"/><br/>
                (<xsl:value-of select="@errors-detail"/>)</td>
            <td class="select" style="text-align: right">
                <xsl:value-of select="@failures"/><br/>
                (<xsl:value-of select="@failures-detail"/>)</td>
        </tr>
        <xsl:apply-templates select="testcase" mode="xunit"/>
    </xsl:template>

    <xsl:template match="testcase" mode="xunit">
        <!-- <xsl:variable name="testname" select="substring(@classname, 0, string-length(@classname))"/> -->
        <xsl:variable name="testname" select="@classname"/>
        <xsl:variable name="rows" select="1 + count( skip[text()] | comment[text()] | sysout[text()] | syserr[text()]) + not(not( .//nodes[error] | error )) + not(not( .//nodes[failure] | failure ))"/>
        <tr>
            <td valign="top" rowspan="{ $rows }"><b><xsl:value-of select="position()"/>/<xsl:value-of select="../@testcases"/></b></td>
            <xsl:choose>
                <xsl:when test="local-name(child::node())='skipped'">
                    <td colspan="4">
                        <strike><xsl:value-of select="@name"/></strike>
                    </td>
                </xsl:when>
                <xsl:otherwise>
                    <td>
                        <xsl:element name="a">
                            <xsl:attribute name="href"><xsl:text>http://www.w3.org/2001/sw/DataAccess/tests/data-r2/</xsl:text><xsl:value-of select="$testname"/><xsl:text>.rq</xsl:text></xsl:attribute>
                            <xsl:choose>
                                <xsl:when test="local-name(child::node())='failure'">
                                        <span class="fail"><xsl:value-of select="$testname"/></span>
                                </xsl:when>
                                <xsl:when test="local-name(child::node())='error'">
                                        <span class="error"><xsl:value-of select="$testname"/></span>
                                </xsl:when>
                                <xsl:otherwise>
                                            <span class="pass"><xsl:value-of select="$testname"/></span>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:element>
                    </td>
                    <td style="text-align: right"><xsl:value-of select="@tests"/></td>
                    <td style="text-align: right"><xsl:if test="local-name(child::node())='error'">
                            <xsl:attribute name="style">background-color: #FF8F8F; color: #660000; font-weight: bold; text-align: right</xsl:attribute>
                        </xsl:if>
                        <xsl:value-of select="@errors"/></td>
                    <td style="text-align: right"><xsl:if test="local-name(child::node())='failure'">
                            <xsl:attribute name="style">background-color: #000000; color: #FFFFFF; font-weight: bold; text-align: right</xsl:attribute>
                            <xsl:value-of select="@failures"/>
                        </xsl:if>
                    </td>
                </xsl:otherwise>
            </xsl:choose>
        </tr>
        <xsl:variable name="error-nodes" select=".//nodes[error] | error"/>
        <xsl:variable name="failure-nodes" select=".//nodes[failure] | failure"/>
        <xsl:choose>
            <xsl:when test="count( $failure-nodes ) &gt; 0">
                <tr><td colspan="4">
                      <div id="{ generate-id() }-err" align="right">[<a href="#" onclick="document.getElementById('{ generate-id() }-err').style.display='none'; document.getElementById('err-{ generate-id() }').style.display='block'; return false;">Display failure</a>]</div>
                      <div style="display:none" id="err-{ generate-id() }">
                        <div align="right">[<a href="#" onclick="document.getElementById('err-{ generate-id() }').style.display='none'; document.getElementById('{ generate-id() }-err').style.display='block'; return false;">Close failure</a>]</div>
                        <div style="overflow: auto; border: 1">
                            <table>
                                <xsl:apply-templates mode="xunit" select="$failure-nodes"/>
                            </table>
                        </div>
                      </div>
                    </td>
                </tr>
            </xsl:when>
            <xsl:when test="count( $error-nodes ) &gt; 0">
                <tr><td colspan="4">
                      <div id="{ generate-id() }-err" align="right">[<a href="#" onclick="document.getElementById('{ generate-id() }-err').style.display='none'; document.getElementById('err-{ generate-id() }').style.display='block'; return false;">Display error</a>]</div>
                      <div style="display:none" id="err-{ generate-id() }">
                        <div align="right">[<a href="#" onclick="document.getElementById('err-{ generate-id() }').style.display='none'; document.getElementById('{ generate-id() }-err').style.display='block'; return false;">Close error</a>]</div>
                        <div style="overflow: auto; border: 1">
                            <table>
                                <xsl:apply-templates mode="xunit" select="$error-nodes"/>
                            </table>
                        </div>
                      </div>
                    </td>
                </tr>
            </xsl:when>
        </xsl:choose>
        <xsl:apply-templates select="skip | comment | sysout | syserr" mode="xunit"/>
    </xsl:template>

    <xsl:template match="skip | skip[not(text())] | comment[not(text())] | sysout[not(text())] | syserr[not(text())]" mode="xunit"/>
    <xsl:template match="skip[text()] | comment[text()]" mode="xunit">
        <tr>
            <td colspan="4">
                <xsl:apply-templates/>
            </td>
        </tr>
    </xsl:template>
    <xsl:template match="sysout[text()] | syserr[text()]" mode="xunit">
        <tr>
            <td colspan="4">
                <div id="{ generate-id() }-{ name() }" align="right">[<a href="#" onclick="document.getElementById('{ generate-id() }-{ name() }').style.display='none'; document.getElementById('{ name() }-{ generate-id() }').style.display='block'; return false;">Display <xsl:value-of select="name()"/></a>]</div>
                <div style="display:none" id="{ name() }-{ generate-id() }">
                    <div align="right">[<a href="#" onclick="document.getElementById('{ name() }-{ generate-id() }').style.display='none'; document.getElementById('{ generate-id() }-{ name() }').style.display='block'; return false;">Close <xsl:value-of select="name()"/></a>]</div>
                    <pre class="console">
                        <xsl:apply-templates/>
                    </pre>
                </div>
            </td>
        </tr>
    </xsl:template>

    <xsl:template match="nodes" mode="xunit">
        <tr><td>Node expected :&#160;</td><td><tt><xsl:value-of select="@expected"/></tt></td></tr>
        <tr><td>Result node :&#160;</td><td><tt><xsl:value-of select="@result"/></tt></td></tr>
        <xsl:variable name="ns" select="namespace::*[name()!='xml']"/>
        <xsl:if test="count( $ns ) &gt; 0">
            <xsl:for-each select="$ns">
                <tr><td align="right"><tt><xsl:value-of select="name(.)"/> =&gt; </tt></td><td><tt><xsl:value-of select="string(.)"/></tt></td></tr>
            </xsl:for-each>
        </xsl:if>
        <xsl:apply-templates mode="xunit" select="error"/>
    </xsl:template>

    <xsl:template match="error" mode="xunit">
        <tr>
            <td><b><xsl:value-of select="@type"/></b></td>
            <td><pre><xsl:apply-templates/></pre></td>
        </tr>
    </xsl:template>

    <xsl:template match="failure" mode="xunit">
        <tr>
            <td><b><xsl:value-of select="@type"/></b></td>
            <td><pre><xsl:apply-templates/></pre></td>
        </tr>
    </xsl:template>

</xsl:stylesheet>
