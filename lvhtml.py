"""
Code fragments for longview that consist mostly or entirely of HTML.
The main reason these live in a separate file is because Emacs gets
confused by complex strings inside triple-quotes (which is the most
convenient way to define the HTML strings).  And when Emacs gets confused
then it fouls up the python indenting completely, which ends up making
editing very difficult.  So we isolate the pain to this one file.
"""

# Copyright (c) 2004, The Long Now Foundation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__ = "Dan Mosedale and James Home <timeline@list.longnow.org>"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2004 The Long Now Foundation"
__license__ = "BSD-style"


def init(filename):
    """Execute filename in the lvhtml module global namespace.

    filename -- file to execute.   Normally this is the template file.

    This allows any symbols in the lvhtml namespace to be overridden.
    """

    execfile(filename, globals())
    return


indexHtml = """<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Frameset//EN\"
        \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd\">

<html xmlns=\"http://www.w3.org/1999/xhtml\">
<head>
<title>%s</title>
</head>

<frameset rows="%s,*" border="0" frameborder="0" framepadding="0" framespacing="0">
<frame src="header.html" name="header" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" border="0" noresize="noresize" />

<frame src="timeline.html#%s" name="timeline" marginwidth="0" marginheight="0" scrolling="auto" frameborder="0" border="0" noresize="noresize" />
</frameset>

</html>
"""

headerTop = """<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>%s</title>
<link rel="stylesheet" href="./styles.css" />
<script language="javascript" type="text/javascript" src="./rollover.js"></script>
</head>

<body onload="loadimgs();">

<table class="logotable" cellpadding="0" cellspacing="0" border="0">
<tr>
<td class="logo">
<img src="img-static/ff-logo.jpg" alt="" width="247" height="30" border="0" /></td>
</tr>
<tr>
<td>
<img src="img-static/no.gif" alt="" width="1" height="1" border="0" /></td>
</tr>
</table>


<table class="titleandnav" cellpadding="0" cellspacing="0" border="0">
<tr>
<td class="titlecell" nowrap="nowrap">
%s
<div class="smtxt">%s - %s</div>
</td>

<td class="navcell">\n
<table class="navtable" cellpadding="0" cellspacing="0" border="0">
<tr>
<td class="navlabel">
%s</td>

<td nowrap="nowrap">\n"""


def buildnavcell(prefix, dateString, mouseoverImg, mouseoutImg, name):
    """Build the HTML for a single navcell.

    prefix -- the string to tack on to the front of the anchor name
    dateString -- the date, as a string, to be used in the anchor name
    mouseoverImg -- name of the image to be displayed on mouseover
    mouseoutImg -- name of the image to be displayed on mouseout
    name -- name of this navcell
    """

    return """<a
href="timeline.html#%s%s"
target="timeline" 
onclick="onimgs('%s', '%s', '%s'); return true;"
onmouseover="chimgs('%s', '%s'); return true;"
onmouseout="chimgs('%s', '%s'); return true;"><img 

src="%s" alt="" width="25" height="20" border="0" name="%s" /></a>""" \
     % (prefix, dateString, name, mouseoverImg, mouseoutImg, name,
        mouseoverImg, name, mouseoutImg, mouseoutImg, name)


headerBottom = """</td>

<td class="navlabel">%s</td>
</tr>
</table></td>

<td class="power"><img src="img-static/longview-power.gif" alt="Powered by Long View" width="89" height="22" border="0" /></td>
</tr>
</table>

</body>
</html>
"""


timelineTop="""<html>
<head>
<title>%s</title>
<link rel="stylesheet" href="./styles.css" />
<script language="javascript" type="text/javascript" src="./timeline.js"></script>

</head>

<body onload="init()">\n
"""


timelinePastNowTable = """

<table cellpadding="0" cellspacing="0">
<tr>
<td class="pastnowcell" nowrap="nowrap">
<img src="img-static/no.gif" width="%d" height="1" alt="" border="0" /><img src="img-static/past-arrow.gif" alt="" width="%d" height="13" border="0" /><img src="img-static/future-arrow.gif" alt="" width="%d" height="13" border="0" /></td>
</tr>
</table>\n
"""

timelineBottom = "</body>\n</html>\n"


def buildLabel(nodeId, labelText, labelLink):
    """Build a label cell

    nodeId -- name of the node that the popup refers to
    labelText -- text of the label itself
    labelLink -- link to follow when label is clicked (if any)
    """

    if len(labelLink) > 0:
        onClick = ''
        href = labelLink
    else:    
        onClick = '\nonclick="return false;"'
        href = 'javascript:;'

    html = """<tr>
<td class="labelscell" nowrap="nowrap">
<a
href="%s"
onmouseout="javascript:hideNode('%s')"
onmouseover="javascript:showNode('%s')"
target="_top"
class="labellink"%s>%s</a></td>
<td><img src="img-static/no.gif" width="1" height="13" alt="" border="0" /></td>
</tr>\n
""" % (href, nodeId, nodeId, onClick, labelText)

    return html

timelineCell = """<img src="img-static/no.gif" width="%d" height="1" alt="" border="0" /><a href="%s" onmouseout="javascript:hideNode('%s')" onmouseover="javascript:showNode('%s')" %sname="node%s" target="_top"><img src="%s" width="%d" height="%d" alt="" border="0" /></a>"""

generatedBar = """
<img src="./img/no.gif" width="%d" height="1" alt="" border="0" /><img 
src="./img-generated/%s.png" width="%d" height="%d" alt="" border="0" usemap="#node%smap" />"""

def buildAreaElement(shape, nodeString, x1, y1, x2, y2):
    """Build an AREA element for an imagemap

    shape -- typically either "rect" or "default"
    nodeString -- name of node to show/hide
    x1, y1, x2, y2 -- coordinates of the rectangle
    """
    
    return """<area shape="%s" alt="" coords="%d,%d,%d,%d" href="javascript:;" onmouseout="javascript:hideNode('%s')" onmouseover="javascript:showNode('%s')" onclick="return false;" />
""" % (shape, x1, y1, x2, y2, nodeString, nodeString)

