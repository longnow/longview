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
# %n - nodeId
# %t - title
# %d - date string
# %1 [...] - positional arguments

# The HTML template used for a popup. 
popupTemplate = """
<div class="node" id="node%n" onmouseout="javascript:hideNode('%n')">
<table cellpadding="0" cellspacing="0" border="0">
<tr>
<td class="popupcell">
%d
<br />
<span class="popuptitle">%t</span><br />
<img src="img-static/no.gif" width="0" height="3" alt="" border="0" /><br />
%1 </td>
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
  }

/* links that have not yet been visited */
a:link {
  color: #333;
  text-decoration: none;
  }

/* links that have already been visited */
a:visited {
  color: #333;
  text-decoration: none;
  }

/* applied to a link when the cursor is hovering over it. */
a:hover	{
  color: #603;
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
  border-bottom: 1px solid #603;
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
  border-top: 1px solid #603;
  border-bottom: 1px solid #603;
  color: #666;
  }  

/* the table cell which holds the navigation bar & surrounding whitespace */ 
.navcell {
  border-top: 1px solid #603;
  border-bottom: 1px solid #603;
  border-left: 1px solid #603;
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
  border-top: 1px solid #603;
  border-bottom: 1px solid #603;
  padding-left: 15px;
  padding-right: 5px;
  text-align: right;
  }

/* row of dates labeling the X-axis of the timeline, at the top */
.ytabletop {
  border-bottom: 1px dotted #603;
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
  border-top: 1px dotted #603;
  border-bottom: 1px solid #603;
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

/* the body of the timeline itself */  
.data {
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
  font-family: verdana, helvetica, arial, sans-serif; /* in order of */
                                                      /* desirability */
  color: #999;
  padding-top: 2px;
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

/* Small text */
.smtxt {
  font-family: verdana, helvetica, arial, sans-serif;
  font-size: 10px;
}
      
"""

