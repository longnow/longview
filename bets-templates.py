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

# HTML template substitutions
#
# %n - nodeId (aka item number)
# %t - title
# %d - date string
# %1 [...] - positional arguments

# The HTML template used for a popup. 

popupTemplate = """
<div class="node" id="node%n" onmouseout="javascript:hideNode('%n')">
<table cellpadding="0" cellspacing="0" border="0" width="100%">
<tr>
<td class="exp">
BET<br><span class="txt">%n</span></td>

<td class="exp" align="right">
%d
</td>
</tr>
</table>

<div class="txt-sm">
%1</div>

<table cellpadding="3" cellspacing="0" border="0" width="100%">
<tr>
<td class="exp" align="right">
AGREE
</td>

<td class="txt" align="left">
%2
</td>
</tr>

<tr>
<td class="exp" align="right">
DISAGREE
</td>

<td class="txt" align="left">
%3
</td>
</tr>

<tr>
<td class="exp" align="right">
STAKES
</td>

<td class="txt" align="left">
%4
</td>
</tr>
</table>
</div>
"""

notifyTemplate = """
<div class="node" id="node%n" onmouseout="javascript:hideNode('%n')">
<table cellpadding="0" cellspacing="0" border="0" width="100%">
<tr>
<td class="exp">
BET<br><span class="txt">%1</span></td>

<td class="exp" align="right">
REMEMBER AND REMIND
</td>
</tr>
</table>

<div class="txt-sm">
%2</div>

<table cellpadding="3" cellspacing="0" border="0" width="100%">
<tr>
<td class="exp" align="center">
%3
</td>
</tr>
</table>
</div>
"""

# this string gets written out in its entirety to styles.css
stylesheets = """
/* for the whole page, unless overridden */
body {     
  padding: 0;
  margin: 0;
  background-image: url("./img-static/bg.jpg");
  }

/* Long Bets specific styles */
.exp {
  font-size: 11px; 
  font-family: Verdana, Helvetica, sans-serif;
  }

.txt-lg {
  font-size: 16px; 
  font-family: Georgia, Times, serif;
  }
  
.txt {
  font-size: 14px; 
  font-family: Georgia, Times, serif;
  }
  
.txt-sm {
  font-size: 11px; 
  font-family: Georgia, Times, serif;
  }
  
.txt-lt {
  font-size: 14px; 
  font-family: Georgia, Times, serif; 
  color: #666666;
  }  

.node .txt-sm {
  padding: 5px 0;
  font-size: 12px;
  }

.key {
  width: 664px;
  margin: 10px 0;
  border: #ccc 1px solid;
  }
  
.key td {
  padding: 1px;
  font-size: 11px; 
  width: 50%;
  font-family: Verdana, Helvetica, sans-serif;
  text-align: center;
  }

/* links that have not been visited */
a:link {
  color: #930;
  text-decoration: none;
  }

/* links that have already been visited */
a:visited {
  color: #930;
  text-decoration: none;
  }

/* applied to a link when the cursor is hovering over it */
a:hover	{
  color: #c63;
  text-decoration: underline;
  }

/* the table at the very top of the page containing the logo image */
.logotable { 
  width: 100%;     /* percent of the browser window occupied by the table */
  margin: 0px;
  padding: 0px;
  }  

/* the table data cell which contains the logo image */
.logo {   
  text-align: right;
  background-color: #000;
  border-bottom: 1px solid #996;
  }

/* the table containing the title and navbar */
.titleandnav { 
  width: 100%;     /* percent of the browser window occupied by the table */
  }

/* the title cell itself */
.titlecell {
  padding: 6px 10px;    /* first value: top & bottom; second: left & right */
  font-family: verdana, helvetica, arial, sans-serif;  /* in order of */
                                                       /* desirability */ 
  font-size: 16px;
  border-top: 1px solid #996;
  border-bottom: 1px solid #996;
  color: #666;
  }  

/* the table cell which holds the navigation bar & surrounding whitespace */ 
.navcell {
  text-align: center;
  vertical-align: middle;
  padding-left: 15px;
  font-family: verdana, helvetica, arial, sans-serif; /* in order of */
                                                      /* desirability */
  font-size: 10px;
  color: #666;
  }  

/* table which holds the navigation bar & horizontal whitespace, but no
 * vertical whitespace */
.navtable {
  margin-left: auto; 
  margin-right: auto;
  }

/* the dates on both ends of the navigation bar */
.navlabel {
  font-family: verdana, helvetica, arial, sans-serif; /* in order of */
                                                      /* desirability */
  font-size: 10px;
  padding: 4px;
  } 

/* table cell that holds the "Long View Powered" image */
.power {
  padding-left: 15px;
  padding-right: 5px;
  text-align: right;
  }

/* row of dates labeling the X-axis of the timeline, at the top */
.ytabletop {
  border-bottom: 1px dotted #996;
  }

/* cell containing an individual date label on the X-axis of the timeline */
.ycell {
  text-align: center;
  vertical-align: top;
  padding: 0;
  font-family: verdana, helvetica, arial, sans-serif; /* in order of */
                                                      /* desirability */
  font-size: 10px;
  } 

/* row of dates labeling the X-axis of the timeline, at the bottom */
.ytablebottom {
  border-top: 1px dotted #996;
  border-bottom: 1px solid #996;
  }

/* table cell containing "Past", "Now", and "Future" at the top of the */
/* timeline*/
.pastnowcell {
  text-align: right;
  padding: 0;
  }

/* the table containing the body of the timeline */
#datatable {
  border-top: 1px #ddd solid;
  border-right: 1px #ddd solid;
  background-image: url('./img-generated/timeline-bg.png');
  }

/* the background of each timeline bar */  
.data {
  padding-top: 1px;
  padding-bottom: 1px;
  background-position: 200px;
  background-repeat: repeat-x;
  } 

/* the block that contains all of the timeline labels on the left side of
 * the screen. */
#labels {
  position: absolute;
  top: 26px;
  z-index: 3;
}

/* cell containing a single label on the left side of the screen */
.labelscell {
  font-size: 10px;
  font-weight: normal;
  font-family: verdana, helvetica, arial, sans-serif; /* in order of desirability */
  color: #999;
  padding-top: 3px;
  border: 0;
}

/* the popups themselves */
.node {
  position: absolute;
  visibility: hidden;
  color: #333;
  width: 200px;
  z-index: 5;
  border: 1px solid #999;
  background-image: url(./img-static/popup-bg.gif);
  padding: 6px;
}

/* The body of the popups (eg the HTML inside the table) */
.popupcell {
  font-size: 10px;
  font-weight: normal;
  font-family: verdana, helvetica, arial, sans-serif; /* in order of */
                                                      /* desirability */
}

/* Popup titles */
.popuptitle {
  font-size: 12px;
}
      
"""

# override the default header top matter from the lvhtml module
headerTop = """<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>%s</title>
<link rel="stylesheet" href="./styles.css" />
<script language="javascript" type="text/javascript" src="./rollover.js"></script>
</head>

<body onload="loadimgs();">

<img src="./img-static/no.gif" alt="" width="1" height="25" border="0"><br>

<div align="center">

<table cellpadding="0" cellspacing="0" border="0" width="664">
<tr>
<td colspan="3">
<img src="./img-static/timeline.gif" alt="Timeline" width="664" height="38" border="0"></td>
</tr>

<tr>
<td class="exp" nowrap>
<img src="./img-static/no.gif" alt="" width="5" height="1" border="0">
<span class="txt"><b>%s</b></span><br>
<!-- longview.py unused value hack: %s - %s -->

&laquo; On the Record: <a href="http://www.longbets.com/bets" target="_top">Bets</a> | <a href="http://www.longbets.com/predictions" target="_top">Predictions</a></td>

<td class="navcell" align="right" nowrap>
<table class="navtable" cellpadding="0" cellspacing="0" border="0">
<tr>
<td class="navlabel">
%s</td>

<td nowrap="nowrap">\n"""


# another override
headerBottom = """</td>

<td class="navlabel">%s</td>
</tr>
</table></td>

<td class="power"><img src="img-static/longview-power.gif" alt="Powered by Long View" width="89" height="22" border="0" /></td>
</td>
</tr>
</table>

<table class="key">
<tr>
<td>
Votes:  YES <img src="img-generated/key1.png" alt="" width="65" height="12"> NO</td>

<td>
Discussion Intensity: LESS <img src="img-generated/key2.png" alt="" width="65" height="12"> MORE</td>
</tr>
</table>
</div>

</body>
</html>
"""
