Long View -- a utility for generating HTML timelines
====================================================
longview.py is a python script with associated files for generating
HTML timelines from simple datafiles.


INSTALLATION
------------
Long View itself is easy to install, but has a few dependencies.  In
particular, it depends on the python GD module, available at
<http://newcenturycomputers.net/projects/gdmodule.html>.  If you get a
version earlier than 0.53, you will need to apply gdmodule-0.51.diff
in this directory before compiling.  Most testing has been done with a
patched version 0.51.  Note that the python GD module itself depends
on Thomas Boutell's GD library (linked to from the python GD module
home page).  Additionally, Python version 2.3 or newer is required.

Long View is packaged with the standard python Distutils.  This means
that the simplest way to install it is simply to execute this command:

python setup.py install

http://docs.python.org/inst/inst.html describes in great detail how to
customize your install.



HOW TO USE
----------
The simplest thing to do is copy one of the examples.  Find the
"examples" directory in your install.  If you did the simple
installation, chances are good that this will be either
/usr/longview/examples or /usr/share/longview/examples.  Copy the
biotech-* files somewhere where you can easily edit and modify them.
You'll probably want to rename them to something more appropriate for
your purpose.


RUNNING THE SCRIPT
------------------
Execute 

     longview.py parameter-file-name

from a command-line prompt to generate the HTML for your timeline into
a subdirectory of the current directory named "html".  See the output
of

     longview.py

for a listing of options that are supported.


PARAMETER FILE
--------------
The first thing to edit is the params file in a spreadsheet.  Make
sure the TIMELINE.datafile and TIMELINE.templatefile parameters point
to the new names, if you've changed them.

In Long View, dates (and durations, unless otherwise noted) are
generally written as YYYYY/MM.  However, for ease of data entry, they
can be abbreviated: leading 0s can be dropped, and it is not necessary
to specify the month (January is assumed).  So the dates "01940/01"
and "1940" are considered equivalent.  To specify a year before the
year 0, append "BCE" or "BC", as in "8000BCE".

Most parameters present in the examples are required.


PARAMETERS
----------
Many of the parameters are fairly self-explanatory, but some are not
quite so obvious.  Some notes:

All sizes (eg margins, widths, heights) are specified in pixels.

A color is specified as 3 hexadecimal numbers representing its red,
green, and blue components.

TIMELINE.nowdate: if you specify this parameter (rather than letting
the script calculate the nowdate based on the current system clock),
it MUST be the first parameter specified in the file.

TIMELINE.5digityears: Set this to True if years in the HTML should
be zero-padded so that they are always five digits long.

TIMELINE.section: The set of section parameters describes all the
sections of the timeline.  One section is needed for each chunk of
time that has a different number of years per horizontal interval of
TIMELINE.intervalsize pixels.  This allows long spans of time where
not much happens to appear condensed down to a visually palatable
size.  The three parameters for this are start-date, end-date, and
interval.  Interval is the number of years per intervalsize pixels.
The end-date is normally given as a date, but, in the case of the
end-date of the last section on the graph, may also be specified as
the string "Ongoing".  This indicates that the graph should end two
intervals past the now date.

The parameters with "diamond" in the name refer to the diamond that is
drawn in an eventbar to represent a subitem.

TIMELINE.navcell: The set of navcell parameters define the pieces of
the navigation bar displayed above the timeline.  Each cell takes
three parameters: the first is the name of the year in the timeline
that it should jump the viewer to.  The second is whether it should
jump the viewer to the top or the bottom of the page.  And the third
is for only the navcell that represents the chunk of time where
TIMELINE.nowdate is being rendered, as it is visually slightly
different from the other cells.  Note that if no navcells are specified, 
the script will generate them automatically.

TIMELINE.resolutioninmonths tells how much time a specific date is
intended to represent.  Values usually will be either "1" for a month,
or "12" for a year.  Note that this parameter does NOT apply to
notifications and interest data, both of which are always assumed to
have a resolution of 1 month.

TIMELINE.labelresolution can be either "months" or "years".  It
dictates whether date labels on the timline are written as
"year/month" or just "year".

TIMELINE.staticimage allows extra images (such as might be used by
template HTML or CSS) to be placed in the generated tree.  The first
parameter is the original filename, and the second is the name that
the file should have in the img-static sub-directory of the generated
tree.

TEMPLATE FILE
-------------
The template file is actually a file containing Python code.  The only
two things that MUST be specified in the template file are the
popupTemplate variable (which contains the templated HTML for the
popup), and the stylesheets variable (which contains all the
stylesheets used by the page).  Most fonts and colors used in the HTML
can be set by editing the stylesheets.  Additionally, any of the
variables or functions that are present in lvhtml.py can be overridden
simply by supplying a new value or define here.

The popupTemplate can contain a number of "escape sequences" that have
special meaning to the code that generates the HTML:

%n is the nodeId of a particular item.  This must be used at least
once in each popup to generate an HTML node with an id attribute so
that the specific popup can be referenced from JavaScript.

%t is the title of the popup.

%d is a string representing the date or dates that this item covers.

The rest of the arguments (%1 through %9) are simply extra arguments
that will be supplied for each item in the datafile, allowing for the
HTML to be arbitrarily customized.

The notifyTemplate is used for popups over the diamonds used to
display notifications.  It can be customized in the same way that the
popupTemplate can.


DATA FILE
---------
Like the parameter file, this file will typically be created or edited
using a spreadsheet.  Each line in the data file represents a single
eventbar item or subitem.

The fields for an item are, in order:

item-number, start-date, end-date, clickthrough-link, title,
template-argument, [...]

Note that the string "?" can be used as an end-date, and will cause
the event bar to end at the "now date", and will render in popups as
"?".

If the item-number is blank, this line is assumed to contain a subitem
of the most recently specified item.  Eventbar subitems are specific
events that happen during (and as part of) a particular eventbar item.
They are drawn as diamonds inside the eventbar of their parent item
(which is assumed to be the most recently specified item).  Their
fields are, in order:

(empty), date, clickthrough-link, template-argument, [...]

The first template argument given as part of any item or sub-itemline
is assigned the escape sequence %1.  The next: %2, and so forth.  Each
template argument is substituted into the popup HTML template in place
of the appropriate escape sequence.


NOTIFICATIONS FILE
------------------
Long View can optionally provide notifications about specific events.
By providing several NOTIFY parameters in the param file (see the
biotech example for the exact parameters), you can cause Long View to
read through a data file each time it runs, and send out a
notification for each line in the file that matches the current date.

Note that the data file itself and the directory the data file lives
in must be writable by the user running the longview.py script.  The
script re-writes the file each time it runs to keep track of which
notifications have already been sent, so they don't get sent out
multiple times (since the date resolution for notification in Long
View is a month).

The notifications data file is a CSV file.  Each line in the file has
up to five fields.  They are, in order:

item-id, date, email-addrs-to-notify, notification-text[, status]

item-id is the ID of the item in the timeline data file that this notification
corresponds to ("None" is a valid value).  Notifications will be displayed
as diamonds with popups in the timeline bar of the corresponding item.

email-addrs-to-notify is a double-quoted, comma-separated list

notification text is sent in the body of the notification email

status begins with one of "Sent", "Unsent", or "Retrying".  If an
attempt to send a notification fails, a warning is printed to stdout,
and "Retrying will be written to the status field so that the script
tries again on the next run.  If status is not specified, "Unsent" is
assumed.

The notification classes can be overridden or inherited from by using
the NOTIFY.hookfile parameter to execute the given file in the lvnotify
module namespace.  NOTIFY.notifierclass and NOTIFY.notificationclass
can be used to overide those things.


INTEREST FILE
-------------
By providing TIMELINE.interestfile, EVENTBAR.nocolor,
EVENTBAR.yescolor, and EVENTBAR.saturation parameters in the parameter
file, Long View can be made to generate discussion data for Long Bets
timelines in visual form.  It colors slices of the eventbar such that
height of the bottom part of each slice represents the number of NO
votes, the height of the top part represents the number of YES votes,
and the darkness of the entire slice represents the intensity of
discussion.  The interest file is a CSV file.  Each line represents a
single month's worth of discussion and votes, using the following fields:

item-Id, date, yes-vote-count, no-vote-count, discussion-post-count

The itemId assigns a given line to a specific event bar on the
timeline.

The date is expected to be in year/month format and represents a
single month.

The rest of the fields should be fairly self-explanatory.


OTHER HOOKS
-----------
If you need to override one or more functions in longview.py, simply
specify a TIMELINE.hookfile in the param file.  This is simply a
python file that will be read in near the beginning of execution, and
any symbols will override those with the same name in longview.py.


KNOWN PROBLEMS
--------------
For some X configurations (Red Hat's Fedora Core 2 case is an observed
instance of this problem), the Linux/UNIX versions of Mozilla and
Mozilla Firefox render the timeline with the wrong font size, which
causes the labels to be out of sync with background guidelines and the
event bars.  The current theory is that this is caused by a bug in the
glue between Mozilla's Gecko rendering engine and the GTK2 toolkit:
<http://bugzilla.mozilla.org/show_bug.cgi?id=190778>


LICENSING
---------
These files can be redistributed and/or modified under a BSD-style license
(included in the accompanying BSD-LICENSE.txt file).


QUESTIONS/FEEDBACK
------------------
Questions and/or feedback should be addressed to the Long View mailing list
<timeline@list.longnow.org>.


