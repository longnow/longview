#!/usr/bin/env python

"""longview.py: Takes CSV data and generates Long View HTML pages.

Usage: ``./longview.py parameter-file``
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

from __future__ import absolute_import, division, with_statement

import csv
import datetime
import math
import os
import shutil
import sys

from optparse import OptionParser
from tempfile import mkdtemp

import lvhtml
import lvnotify
import lvutils
import sliceMaker

__author__ = "Dan Mosedale, James Home, and Ben Keating"
__maintainer__ = "Ben Keating"
__email__ = "oss+longview@longnow.org"

__version__ = "1.1"
__license__ = "BSD-style"
__status__ = "Beta"

#### CONSTANTS

# must match the widths of the actual image files used
pastArrowImageWidth = 56
futureArrowImageWidth = 67

# generate one navcell per this many pixels of timeline space
idealPixelsPerNavCell = 500

# width in pixels of a single navcell
navCellWidth = 25

# minimum and maximum allowed number of nav cells
minNavCells = 2
maxNavCells = 12


#### GLOBALS

navCellsManuallySpecified = False
pixelsPerNavCell = idealPixelsPerNavCell

# maximum number of discussion posts in a month about any topic
maxPosts = 0

# global parameters
params = {}

# assumed to be ordered and contiguous
timelineSections = []

# assumed to be ordered
navcells = []

# a dictionary of dictionaries of dictionaries
interestData = {}

# an array of extra images to include
extraStaticImages = []

def loadhooks(filename):
    """Execute filename in the longview.py global namespace.

    filename -- file to execute.   Normally this is the template file.

    This allows almost all symbols in longview.py to be overridden.
    """

    execfile(filename, globals())
    return


def writeNowNavCells(outputDir):
    """Write out the PNGs for the "now" navcell.

    outputDir -- toplevel dir where output is being generated
    """

    # what horizontal pixel in the timeline does "now" start at?
    nowTimelineXCoord = getNowBarStartXCoord()

    # let's get this as a percent of the area represented by the navcell
    startPixelAsPercentage = (
        (nowTimelineXCoord - int(params['TIMELINE.leftmargin'])) %
        pixelsPerNavCell) / pixelsPerNavCell

    # which pixel in the navcell will this be?
    navCellNowStart = int(math.floor(startPixelAsPercentage * navCellWidth))

    # draw the "onmouseover" cell
    navCellOn = lvutils.NowCellPNG(
        os.path.join(outputDir, "img-generated", "nav-now-on.png"), True,
        navCellNowStart)
    navCellOn.generate()

    # draw the "onmouseout" cell
    navCellOff = lvutils.NowCellPNG(
        os.path.join(outputDir, "img-generated", "nav-now-off.png"), False,
        navCellNowStart)
    navCellOff.generate()
    
    return


def writePopups(outfileObject, rows):

    for row in rows:

        # if this is a subitem, or an item with identical start and end dates
        # only write out a single date
        if row['startDate'] == row['endDate']:
            dates = row['endDate'].toString(True, True)
        else: 
            # otherwise write both dates as a range
            dates = row['startDate'].toString(True, True) + " - " + \
                    row['endDate'].toString(True,True)

        outfileObject.write(
            buildPopup(lvhtml.popupTemplate, row['nodeId'], dates,
                       row['title'], row['args']))

        # if we have subitems, write out the popups for them
        subitemLetter = 97 # 'a'
        for subitem in row['subitems']:

            if subitem.has_key('isNotification'):
                template = lvhtml.notifyTemplate
            else:
                template = lvhtml.popupTemplate
                
            outfileObject.write(
                buildPopup(template, row['nodeId'] + chr(subitemLetter),
                           subitem['date'].toString(True, True),
                           row['title'], subitem['args']))
            subitemLetter += 1
                                         
    return


def buildPopup(template, nodeId, dateString, title, args):
    """Interpolate relevant values into the popup HTML.

    template -- HTML template to use for the popup
    nodeId -- the node this popup is for
    dateString -- the dates represented by the popup, in string form
    args -- any additional values from data file to be interpolated
    """

    import textwrap
    import re
    
    popupHtml = re.sub(r'\\n', "\n", template)
    popupHtml = re.sub("%d", dateString, popupHtml)
    popupHtml = re.sub("%n", str(nodeId), popupHtml)
    popupHtml = re.sub("%t", title, popupHtml)
    
    argNum = 1
    for arg in args:
        popupHtml = re.sub("%" + str(argNum), textwrap.fill(arg, 71), 
                           popupHtml)
        argNum += 1

    return popupHtml


def writeLabels(outfileObject, rows):

    outfileObject.write("""<div id="labels">
<table class="labelstable" cellpadding="0" cellspacing="0" border="0">
""")

    for row in rows:
        outfileObject.write(
            lvhtml.buildLabel(row['nodeId'], row['title'], row['link']))

    outfileObject.write("</table>\n</div>\n\n")
    
    return


def generateNavCellList():
    """Automatically populate the nav cell list if it doesn't exist."""

    global navcells
    global minNavCells
    global maxNavCells

    # This code generates navcells based partly on the assumption that the
    # the area represented by the navcell starts at the anchor the navcell
    # links to, and ends just before the anchor linked to by the next navcell
    # in the list.  Because of the way browsers (or Mozilla Firefox, at least)
    # implement scrolling to anchors, this is probably not the best assumption.
    # I suspect we could do better by acting as though the linked-to anchor
    # represents the center of the cell.
    
    # figure out number of navcells
    numNavCells = int(math.floor(totalWidth / idealPixelsPerNavCell))

    # set upper and lower bounds on the number of navcells
    if numNavCells < minNavCells:
        numNavCells = minNavCells
    elif numNavCells > maxNavCells:
        numNavCells = maxNavCells

    pixelsPerNavCell = math.floor(totalWidth / numNavCells)

    # start at the left margin
    nextIdealStartPoint = int(params['TIMELINE.leftmargin'])

    # iterate through the timeline sections
    for section in timelineSections:

        # iterate through all the anchors
        date = section['startDate']
        while date <= section['endDate']:

            # if this is the appropriate anchor (ie it's the closest
            # anchor to the right of (or at) the ideal pixel)...
            if getStartXCoordFromDate(date) >= nextIdealStartPoint:

                # generate navcell with this anchor (we'll modify the
                # 'now' cell later)
                navcells.append({'date': lvutils.LVDate(date),
                                 'now': False})

                # bump up nextIdealStartPoint
                nextIdealStartPoint = nextIdealStartPoint + pixelsPerNavCell
                
            # prepare for the next iteration
            date = date + section['interval']
    
    # mark the "now" cell as such
    i = numNavCells - 1
    while i >= 0:
        if getnowdate() >= navcells[i]['date']:
            navcells[i]['now'] = True
            break
        i -= 1
        
    # iterate through the navcell list, setting the location on each cell
    for i in range(len(navcells)):

        if i == len(navcells) - 1:
            end = timelineSections[-1]['endDate']
        else:
            end = navcells[i+1]['date'] \
                  - int(params['TIMELINE.resolutioninmonths'])

        navcells[i]['location'] = getNavCellLocation(navcells[i]['date'], end)

    # figure out the last date anchor
    for section in timelineSections:
        date = section['startDate']
        while date <= section['endDate']:
            date = date + section['interval']

    # because of the way anchors work (they only guarantee that the anchor in
    # question will be on screen) we really want the last navcell to
    # point to the far right of the timeline.
    navcells[numNavCells-1]['date'] = date - section['interval']

    return


def getNavCellLocation(startDate, endDate):
    """Returns location ("top" or "bottom") for a given navcell to point to.

    The decision is made based on which whether more timeline bars are visible
    in the top or the bottom section of the timeline between the given dates.
    
    startDate -- LVDate of the start date
    endDate -- LVDate of the end date
    """

    lastTopRow = int(math.floor(len(rows) / 2))

    # iterate through top timeline bars to count how many intersect with the
    # timespan of this navcell
    topRowsVisible = 0
    for i in range(0, lastTopRow):
        if rows[i]['startDate'] < endDate and rows[i]['endDate'] > startDate:
            topRowsVisible += 1

    # iterate through bottom timeline bars
    bottomRowsVisible = 0
    for i in range(lastTopRow+1, len(rows)):
        if rows[i]['startDate'] < endDate and rows[i]['endDate'] > startDate:
            bottomRowsVisible += 1
    
    # return whichever half has more
    if topRowsVisible >= bottomRowsVisible:
        return "top"
    else:
        return "bottom"


def writeDateTable(outfileObject, tableClass, namePrefix):

    outfileObject.write("""
<table class="%s" cellpadding="0" cellspacing="0" border="0">
<tr>
<td class="ycell">
<img src="img-static/no.gif" width="5" height="1" alt="" border="0" /></td>\n
""" % tableClass)

    for section in timelineSections:

        # print out all the labels in this section
        date = section['startDate']
        while date <= section['endDate']:

            label = date.toString(monthSeparator="/")
            name = date.toString(monthSeparator="_")

            outfileObject.write("""<td class="ycell">
<a name="%s%s">%s</a><br />
<img src="img-static/no.gif" width="%d" height="1" alt="" border="0" /></td>\n
""" % (namePrefix, name, label, int(params['TIMELINE.intervalsize'])))
            date = date + section['interval']
        
    outfileObject.write("</tr>\n</table>")

    return


def getSectionFromDate(date):

    for section in timelineSections:
        if date >= section['startDate'] and date <= section['endDate']:
            return section

    warning = "warning: date %d is not contained in any section\n" % date
    sys.stderr.write(warning)
    raise IndexError, warning

    
def getStartXCoordFromDate(date):
    """Return the starting X pixel for a given date"""

    section = getSectionFromDate(date)
    
    return int(round(section['startPixel'] + (date - section['startDate']) \
               * section['pixelsPerMonth']))


def getNowBarStartXCoord():
    """Return the starting X coordinate for the now bar"""

    return getStartXCoordFromDate(getnowdate())
    

def getBarWidth(startDate, endDate):
    """Return the width, in pixels, of this timeline bar"""

    endSection = getSectionFromDate(endDate)
    width = getStartXCoordFromDate(endDate) \
            + int(params['TIMELINE.resolutioninmonths']) \
            * endSection['pixelsPerMonth'] - getStartXCoordFromDate(startDate)

    return max(int(round(width)), int(params['TIMELINE.minbarwidth']))


def buildTimelineBar(nodeId, startDate, endDate, link, imagePath, args):
    """Return the HTML for a timeline bar

    nodeId -- node in string form of the associated popup
    startDate -- starting date of the bar as an LVDate
    startDate -- ending date of the bar as an LVDate
    link -- clickthrough URL.  may be zero-length, meaning no clickthrough
    imagePath -- pathname of the image to be used for this bar
    args -- any additional arguments from the data file
    """

    startPixel = getStartXCoordFromDate(startDate)
    width = getBarWidth(startDate, endDate)

    if len(link) == 0:
        onClick = 'onclick="return false;" '
        href = 'javascript:;'
    else:
        onClick = ''
        href = link

    return lvhtml.timelineCell % (startPixel, href, nodeId, nodeId, onClick,
                                  nodeId, imagePath, width, getbarheight())


def writeTimelineBars(outfileObject, rows, outputDir, imageSubDir):
    """Write out the timeline bars, both HTML and PNGs.

    outfileObject -- file handle to write to
    rows -- the list of timeline bars
    outputDir -- directory to write output to
    imageSubDir -- the subdir of outputDir to write any generated images to
    """

    tableWidth = getBarWidth(gettimelinestartdate(), gettimelineenddate()) \
                 + int(params['TIMELINE.leftmargin'])
    
    outfileObject.write("""<table id="datatable" cellpadding="0" cellspacing="0" border="0" width="%dpx">\n""" % tableWidth)

    colorNum = 2
    futureFirstPixel = getNowBarStartXCoord() + getnowbarwidth()
    
    for row in rows:

        # alternate the colors of the bars
        if colorNum == 1:
            colorNum = 2
        else:
            colorNum = 1

        # calculate the last pixel in this bar; we need to see if this
        # overlaps with the future area, in which case we need to render
        # this bar as an image.
        startPixel = getStartXCoordFromDate(row['startDate'])
        barLastPixel = getBarWidth(row['startDate'], row['endDate']) \
                        + startPixel - 1

        outfileObject.write('<tr>\n<td class="data" nowrap="nowrap">\n')

        if len(row['subitems']) > 0 or barLastPixel >= futureFirstPixel or \
               interestData.has_key(row['nodeId']):
            writeImageBar(outfileObject, row, outputDir, imageSubDir,
                          colorNum)
        else:
            try:
                outfileObject.write(
                    buildTimelineBar(row['nodeId'], row['startDate'],
                                     row['endDate'], row['link'],
                                     "%s/color%d.png" %
                                     (imageSubDir, colorNum), row['args']))
            except IndexError:
                sys.stderr.write("; timeline bar skipped")

        outfileObject.write("</td>\n</tr>\n\n")

    outfileObject.write("</table>\n")
    return


def writeSubItems(outfileObject, row, barImage):
    """Write all the subitem diamonds and area elements for this row

    outfileObject -- file object to write to
    row -- from the global rows[] array
    barImage -- SlicedImage object for this event bar
    """

    barWidth = getBarWidth(row['startDate'], row['endDate'])
    startPixel = getStartXCoordFromDate(row['startDate'])
    
    # we do want an imagemap if there are subitems
    outfileObject.write('<map name="node%smap" id="node%smap">\n' %
                        (row['nodeId'], row['nodeId']))

    # generate an area for each subitem
    subitemLetter = 97 # 'a'

    for subitem in row['subitems']:

        x1 = getStartXCoordFromDate(subitem['date']) - startPixel

        # if the diamond would be off the right end of the bar, nudge it
        # to the left just enough
        if x1 > barWidth - int(params['EVENTBAR.diamondwidth']):
            x1 -= int(params['EVENTBAR.diamondwidth'])
                
        x2 = x1 + int(params['EVENTBAR.diamondwidth'])

        # generate the HTML for this <area>
        outfileObject.write(
            lvhtml.buildAreaElement("rect", row['nodeId'] + chr(subitemLetter),
                                    x1, 0, x2, getbarheight() - 1))

        # draw the diamond into the bar
        barImage.drawDiamond(x1)
        
        subitemLetter += 1
        
    # imagemap default area
    outfileObject.write(
        lvhtml.buildAreaElement("default", row['nodeId'], 0, 0, barWidth,
                                getbarheight()))

    # imagemap footer
    outfileObject.write('</map>\n')

    # html for the bar itself
    outfileObject.write(lvhtml.generatedBar %
                        (startPixel, row['nodeId'], barWidth,
                         getbarheight(), row['nodeId']))
    return

def writeInterestSlices(barImage, row):
    """Write the interest slices for this into the given image

    barImage -- image to render slices into
    row -- data for this event bar
    """

    # build a slice for every month in the bar until now
    leapPixels = 0        
    month = row['startDate']
    while month <= min(getnowdate(), row['endDate']):

        # need this to for figuring out month width
        sliceSection = getSectionFromDate(month)

        # keep track of the amount of pixels lost to rounding errors
        fraction, integer = math.modf(sliceSection['pixelsPerMonth'])
        if fraction < .5:
            leapPixels += fraction
        else:
            leapPixels -= 1-fraction

        # if the number of pixels lost/gained >= 1, compensate
        paddingPixels = 0
        if leapPixels >= 1.0:
            paddingPixels = 1
            leapPixels -= 1.0
        elif leapPixels <= -1.0:
            paddingPixels = -1
            leapPixels += 1.0

        # if we're at the last interest slice, which is drawn over the
        # now bar, we may need to add some pixels of padding to
        # compensate for the fact that the now bar may be bigger than
        # it ought to because of the minimum bar width
        if month == min(getnowdate(), row['endDate']): 
            paddingPixels += int(round((getnowbarwidth() -
                                        getnowbarvirtualwidth()))) - 1

        if not interestData[row['nodeId']].has_key(month):

            # build "no-data" slice
            barImage.addSlice(
                {'height': getbarheight(),
                 'width': int(round(sliceSection['pixelsPerMonth']))
                 + paddingPixels, 'lowerSize': 1.0,
                 'lowerColor': params['EVENTBAR.nodatacolor'],
                 'dividerColor': params['EVENTBAR.nodatacolor'],
                 'upperColor': params['EVENTBAR.nodatacolor'],
                 'saturation': 1.0, 'brightness': 1.0})

            month += 1
            continue

        interestSlice = interestData[row['nodeId']][month]
            
        # figure out the ratio of "no" votes, avoiding zero division
        if interestSlice['noVotes'] == 0 and interestSlice['yesVotes'] == 0:
            noRatio = 0.5 # should perhaps actually do a different bg
        elif interestSlice['noVotes'] == 0:
            noRatio = 0.0
        elif interestSlice['yesVotes'] == 0:
            noRatio = 1.0
        else:
            noRatio = interestSlice['noVotes'] / \
                      (interestSlice['noVotes']+interestSlice['yesVotes'])

        # figure out relative discussion intensity
        if not interestSlice.has_key('discussionPosts'):
            relativePosts = 0.5 # if there's no data, fake it
        elif interestSlice['discussionPosts'] == 0:
            relativePosts = 0.0
        else:
            global maxPosts
            relativePosts = interestSlice['discussionPosts'] / maxPosts
            
        barImage.addSlice(
            {'height': getbarheight(),
             'width': int(round(sliceSection['pixelsPerMonth'])) \
             + paddingPixels, 'lowerSize': noRatio,
             'lowerColor': params['EVENTBAR.nocolor'],
             'dividerColor': params['EVENTBAR.nocolor'],
             'upperColor': params['EVENTBAR.yescolor'],
             'saturation': float(params['EVENTBAR.saturation']),
             'brightness': 1 - relativePosts})

        month +=1

    return


def writeImageBar(outfileObject, row, outputDir, imageSubDir,
                  colorNum):
    """Write the HTML and PNG for a bar image, possibly with subitem popups

    outfileObject -- file handle to be written to
    row -- dictionary of the properties of this row
    outputDir -- directory where all output is written
    imageSubDir -- subdirectory of outputDir to write generated images to
    colorNum -- which of the bar colors (either 1 or 2) is the background
    """
    
    startPixel = getStartXCoordFromDate(row['startDate'])

    barWidth = getBarWidth(row['startDate'], row['endDate'])

    # do we need a future section?
    futureAbsoluteStartXCoord = getNowBarStartXCoord() + getnowbarwidth()
    if futureAbsoluteStartXCoord <= startPixel + barWidth:
        futureStartXCoord = max(futureAbsoluteStartXCoord - startPixel, 0)
    else:
        futureStartXCoord = None

    # create the image
    barImage = sliceMaker.SlicedImage(barWidth, getbarheight())

    barImage.diamondWidth = int(params['EVENTBAR.diamondwidth'])
    barImage.diamondLeftMargin = int(params['EVENTBAR.diamondleftmargin'])
    barImage.diamondVerticalMargin = int(
        params['EVENTBAR.diamondverticalmargin'])

    # if this bar has interest data, use slicemaker to construct it
    if (interestData.has_key(row['nodeId'])):

        writeInterestSlices(barImage, row)
                 
    else: # there's no interest data, just add a single slice 
        
        if futureStartXCoord is None:
            nonFutureSliceWidth = barWidth
        else:
            nonFutureSliceWidth = futureStartXCoord
            
        barImage.addSlice(
            {'height': getbarheight(), 'width': nonFutureSliceWidth,
             'lowerSize': 1.0,
             'lowerColor': params['EVENTBAR.color%d' % colorNum],
             'dividerColor': params['EVENTBAR.color%d' % colorNum],
             'upperColor': params['EVENTBAR.color%d' % colorNum],
             'saturation': 1.0, 'brightness': 1.0})
             
    # add future slice, if necessary
    if futureStartXCoord is not None:
        barImage.addSlice({'height': getbarheight(),
                           'width': barWidth - futureStartXCoord,
                           'lowerSize': 1.0,
                           'lowerColor': params['EVENTBAR.futurecolor'],
                           'dividerColor': params['EVENTBAR.futurecolor'],
                           'upperColor': params['EVENTBAR.futurecolor'],
                           'saturation': 1.0,
                           'brightness': 1.0})
    
    if len(row['subitems']) > 0:
        writeSubItems(outfileObject, row, barImage)
    else:
        outfileObject.write(
            buildTimelineBar(row['nodeId'], row['startDate'], row['endDate'],
                             row['link'],
                             os.path.join(imageSubDir, row['nodeId'] + ".png"),
                             row['args']))

    if params.has_key('EVENTBAR.nowbarontop'):
        if params['EVENTBAR.nowbarontop']:
            barImage.drawFilledSlice(getNowBarStartXCoord() - startPixel,
                                     getnowbarwidth(),
                                     params['TIMELINE.nowbarcolor'])
            
    # write out the PNG
    barImage.generate(os.path.join(outputDir, imageSubDir,
                                   row['nodeId'] + ".png"))
    return


def writeTimelineFrame(rows, outputDir):
    """Write the HTML for the timeline frame."""
    
    timelineFile = open(os.path.join(outputDir, "timeline.html"), "wt")
    timelineFile.write(lvhtml.timelineTop % gettitle())
    writePopups(timelineFile, rows)
    writeDateTable(timelineFile, "ytabletop", "")
    timelineFile.write(lvhtml.timelinePastNowTable %
                       (getNowBarStartXCoord() + int(round(getnowbarwidth()/2))
                        - pastArrowImageWidth,
                       pastArrowImageWidth, futureArrowImageWidth))
    writeTimelineBars(timelineFile, rows, outputDir, "img-generated")
    writeDateTable(timelineFile, "ytablebottom", "b")
    timelineFile.write("\n\n<br /><br /><br /><br /><br /><br />\n\n")
    timelineFile.write('<div id="mysteriousfuture">\n\n\n</div>\n\n\n')
    writeLabels(timelineFile, rows)
    timelineFile.write(lvhtml.timelineBottom)
    timelineFile.close()
    return


def writeTimelineBackground(outputDir):
    """Write the background PNG for the timeline.

    outputDir -- output directory for the HTML.  The PNG will be written to
                 outputDir/img-generated/timeline-bg.html.
    """

    # width of the image is the starting pixel of the last month displayed,
    # plus enough pixels to represent that month itself
    endDate = timelineSections[len(timelineSections)-1]['endDate']
    width = getStartXCoordFromDate(endDate) + \
            int(round(getSectionFromDate(endDate)['pixelsPerMonth']
                  * int(params['TIMELINE.resolutioninmonths'])))

    bg = lvutils.Background(width, getbarheight() + 1, getNowBarStartXCoord())
    bg.nowColor = params['TIMELINE.nowbarcolor']
    if params.has_key('TIMELINE.backgroundstipplecolor'):
        bg.stippleColor = params['TIMELINE.backgroundstipplecolor']
    bg.dividerWidth = int(params['TIMELINE.minbarwidth'])
    bg.nowWidth = getnowbarwidth()
    bg.generate(os.path.join(outputDir, "img-generated", "timeline-bg.png"))

    return


def writeIndex(outputDir):
    """Write the index (main page) for the HTML frameset

    outputDir -- directory to write it into
    """
    
    indexFile = open(os.path.join(outputDir, "index.html"), "wt")
    indexFile.write(lvhtml.indexHtml % (gettitle(),
                                        params['TIMELINE.topframeheight'],
                                        getnowcellanchor()))
    indexFile.close()
    return


def writeHeaderFrame(outputDir):
    """Write the HTML page used in the header frame

    outputDir -- directory to write it into
    """
    
    headerFile = open(outputDir + "/header.html", "wt")
    headerFile.write(lvhtml.headerTop %
                     (gettitle(), params['TIMELINE.title'],
                      timelineSections[0]['startDate'].toString(),
                      timelineSections[len(timelineSections)-1]
                      ['endDate'].toString(),
                      timelineSections[0]['startDate'].toString()))

    # write out the navcells in the navbar
    cellcount = 1
    for navcell in navcells:
        if navcell['location'].lower() == 'bottom':
            anchorPrefix = 'b'
        else:
            anchorPrefix = ''

        if navcell['now']:
            onImage = "img-generated/nav-now-on.png"
            offImage = "img-generated/nav-now-off.png"
            cellName = "navnow"
        else:
            onImage = "img-static/nav-on.gif"
            offImage = "img-static/nav-off.gif"
            cellName = "nav" + str(cellcount)

        # since this is an anchor name, we need to use "_" instead of "/"
        dateString = navcell['date'].toString(monthSeparator="_")
        headerFile.write(
            lvhtml.buildnavcell(anchorPrefix, dateString, onImage, offImage,
                                cellName))
        cellcount += 1

    headerFile.write(lvhtml.headerBottom %
                     timelineSections[len(timelineSections)-1]
                     ['endDate'].toString())
    headerFile.close()
    return


def readDataFile(dataFile):

    rows = []
    reader = csv.reader(open(dataFile, "rt"))

    for row in reader:

        if row[0] != "":

            # check enddate to see if it's the special "?", which
            # represents now, but converts differently to a string
            if row[2] == "?":
                endDate = lvutils.LVDate(getnowdate())
                endDate.ongoing = True
            else:
                endDate = lvutils.LVDate(row[2])
            
            # a regular row
            rows.append({'nodeId': row[0], 'startDate': lvutils.LVDate(row[1]),
                         'endDate': endDate, 'link': row[3],
                         'title': row[4], 'args': row[5:], 'subitems': []})
        else:
            # a sub-item
            rows[-1]['subitems'].append({'date': lvutils.LVDate(row[1]),
                                         'link': row[2], 'args': row[3:]})

    return rows


def readInterestFile(interestFile):
    """Read a config file into the interestData global

    interestFile -- name of the file to read interest data from
    """

    global interestData
    global maxPosts

    reader = csv.reader(open(interestFile, "rt"))
    for row in reader:
        if not interestData.has_key(row[0]):
            interestData[row[0]] = {}
        interestData[row[0]][lvutils.LVDate(row[1])] = \
                                                     {'yesVotes': int(row[2]),
                                                      'noVotes': int(row[3])}
        # only add the discussion post info if it's there
        if len(row) == 5:
            interestData[row[0]][lvutils.LVDate(row[1])]['discussionPosts'] = \
                                                      int(row[4])
            # useful later for calculating relative discussion intensity
            if int(row[4]) > maxPosts:
                maxPosts = int(row[4])

    return

    
def readParamFile(paramFile):
    """Read a config file of parameters and return them as a dict"""

    global params
    nowCellSpecified = False

    reader = csv.reader(open(paramFile, "rt"))
    for row in reader:
        # a few things get special cases
        if row[0] == 'TIMELINE.section':

            interval = lvutils.LVDate(row[3])

            if row[2].lower() == "ongoing":
                endDate = getnowdate() + interval * 2
            else:
                endDate = lvutils.LVDate(row[2])

            timelineSections.append({'startDate': lvutils.LVDate(row[1]),
                                     'endDate': endDate,
                                     'interval': interval})
            
        elif row[0] == 'TIMELINE.navcell':
            if len(row) == 4 and row[3].lower() == 'now':
                if nowCellSpecified:
                    sys.stderr.write( 
                        "warning: more than one 'now' navcell was specified")
                now = True
                nowCellSpecified = True
            else:
                now = False

            navcells.append({'date': lvutils.LVDate(row[1]),
                             'location': row[2],
                             'now': now})
            global navCellsManuallySpecified
            navCellsManuallySpecified = True
            
        elif row[0] in ('EVENTBAR.color1', 'EVENTBAR.color2',
                        'EVENTBAR.futurecolor', 'EVENTBAR.nocolor',
                        'EVENTBAR.yescolor', 'EVENTBAR.nodatacolor',
                        'TIMELINE.backgroundstipplecolor',
                        'TIMELINE.nowbarcolor'):
                        
            # colors are assumed to be a hex rgb triple
            params[row[0]] = (int(row[1], 16), int(row[2], 16),
                                  int(row[3], 16))

        elif row[0] == 'TIMELINE.5digityears':
            lvutils.alwaysPrint5DigitYears = bool(eval(row[1]))
            params[row[0]] = bool(eval(row[1]))

        elif row[0] == 'EVENTBAR.nowbarontop':
            params[row[0]] = bool(eval(row[1]))

        elif row[0] == 'TIMELINE.labelresolution':
            if row[1] == "months":
                lvutils.dateResolutionDefaultsToYears = False
            params[row[0]] = row[1]

        elif row[0] == 'TIMELINE.hookfile':
            loadhooks(row[1])
            params[row[0]] = row[1]

        elif row[0] == 'TIMELINE.staticimage':
            extraStaticImages.append({'srcName': row[1], 'destName': row[2]})
            
        # everything else is stuffed directly into the params dict
        else:
            params[row[0]] = row[1]

    if navCellsManuallySpecified and not nowCellSpecified:
        sys.stderr.write("warning: no 'now' navcell was specified")


def doNotifications():
    """Send out any pending notifications.

    Reads the notifications CSV file, and sends out any pending notifications.
    """

    # notification is optional
    if not params.has_key('NOTIFY.datafile'):
        return
    
    # hooks for using a different class as the notifier
    if params.has_key('NOTIFY.hookfile'):
        lvnotify.init(params['NOTIFY.hookfile'])
        notifierClass = params['NOTIFY.notifierclass']
    else:
        notifierClass = lvnotify.DefaultNotifier
        
    # set up the default notifier
    notifier = notifierClass(params['NOTIFY.datafile'], params['NOTIFY.from'],
                             params['NOTIFY.smtpserver'],
                             params['TIMELINE.5digityears'])

    # override a few defaults, if requested
    if params.has_key('NOTIFY.notificationclass'):
        notifier.notificationClass = params['NOTIFY.notificationclass']
    if params.has_key('NOTIFY.subject'):
        notifier.subject = params['NOTIFY.subject']

    # iterate through the pending notifications
    for notification in notifier.getPendingNotifications():

        try:
            notifier.notify(notification)
        except Exception, ex:
            # something went wrong; write out a warning
            sys.stderr.write("%s: warning: failed to send notification: "
                             "'%s': %s\n" %
                             (sys.argv[0], notification.text, ex));

    # we're finished, write out the new version of the datafile
    notifier.updateDataFile()

    # add notification subitems HTML
    for notification in notifier.notifications:

        if notification.row is not None:

            # find the row that this notification belongs to
            rowNum = None
            for i in range(len(rows)):
                if rows[i]['nodeId'] == str(notification.row):
                    rowNum = i
                    break
            if rowNum is None:
                raise Exception, "Notification points to non-existent row"
            
            rows[rowNum]['subitems'].append(
                {'date': notification.date, 'link': '',
                 'isNotification': True,
                 'args': [rows[rowNum]['nodeId'], notification.text,
                          notification.status]})
    return


##############################################################################

# functions for use in generating the pages

def gettitle():
    """Return title string to be used in the timeline"""

    return "%s [ %s, %s - %s ]" % (
        params['TIMELINE.pretitle'], params['TIMELINE.title'],
        gettimelinestartdate().toString(),
        gettimelineenddate().toString())

def gettimelinestartdate():
    """Return the start date for this timeline"""
    return timelineSections[0]['startDate']

def gettimelineenddate():
    """Return the end date for this timeline"""
    return timelineSections[len(timelineSections)-1]['endDate']

def getbarheight():
    """Return height of timeline bars, in pixels

    Uses the 'EVENTBAR.height' value from the parameter file, if that
    exists.  Defaults to 13.
    """

    if params.has_key('EVENTBAR.height'):
        return int(params['EVENTBAR.height'])

    return 13


def getnowdate(resolutionOverride=None):
    """Return date to be used as the "now" item for a timeline

    Uses the 'TIMELINE.nowdate' value from the parameter file,
    and falls back to the current year if that doesn't exist.

    resolutionOverride -- force the given resolution in months to be used
    """

    if params.has_key('TIMELINE.nowdate'):
        return lvutils.LVDate(params['TIMELINE.nowdate'])

    today = datetime.date.today()

    if resolutionOverride is not None:
        resolution = resolutionOverride
    else:
        resolution = int(params['TIMELINE.resolutioninmonths'])

    currentMonth = today.year * 12 + today.month - 1

    closestMonth = int(round(currentMonth / resolution) * resolution)

    return lvutils.LVDate(closestMonth)


def getnowcellanchor():
    """Return the anchor name referred to by the now cell in the navbar.

    Currently this happens to be the year that begins the stretch of time
    that the nowcell represents."""


    nowcell = [navcell for navcell in navcells if navcell['now']]

    if nowcell[0]['location'].lower() == 'bottom':
        anchorPrefix = 'b'
    else:
        anchorPrefix = ''
    
    return nowcell[0]['date'].toString(monthSeparator="_") + anchorPrefix


def getnowbarvirtualwidth():
    """Return virtual width of now bar for use in calculations"""

    section = getSectionFromDate(getnowdate())

    return int(params['TIMELINE.resolutioninmonths']) \
           * section['pixelsPerMonth']


def getnowbarwidth():
    """Return the width of the "now" bar as rendered."""

    if params.has_key('TIMELINE.nowbarwidth'):
        return int(params['TIMELINE.nowbarwidth'])
    
    return max(int(params['TIMELINE.minbarwidth']),
               int(round(getnowbarvirtualwidth())))


###################################################################
# main program starts here

# just in case
def cleanup(): 
    if os.path.isdir(tempDir):
        shutil.rmtree(tempDir)
    return
sys.exitfunc = cleanup

# if we're running in the source directory, we want to use the local
# html prototypes and libraries
if sys.argv[0] == 'longview.py' or sys.argv[0] == './longview.py' and \
   os.path.isfile('./longview.py') and os.path.isdir('prototype-html'):

    print sys.argv[0] + " running in source tree; using local prototype-html"
    defaultProtoHtml = "./prototype-html"
else:
    defaultProtoHtml = os.path.join(sys.prefix, "longview", "prototype-html")

# parse the arguments
usage = "usage: %prog [options] parameter-file"
parser = OptionParser(usage=usage)
parser.add_option("-p", "--prototype-dir", type="string", dest="protoDir",
                  help="directory prototype files are copied from",
                  default=defaultProtoHtml)
parser.add_option("-o", "--output-dir", type="string", dest="outputDir",
                  help="directory to write output to",
                  default="html")
(options, args) = parser.parse_args()

# generate the new files in a temporary directory for HTTP if-mod-since
# purposes
tempDir = mkdtemp(dir=os.path.dirname(options.outputDir))

if len(args) != 1:
    parser.print_help()
    sys.exit(1)
    
# read the parameters for this page into a dictionary
try:
    readParamFile(sys.argv[1])
except IOError, ex:
    sys.stderr.write("%s: error reading parameter file %s: %s\n"
                     % (sys.argv[0], args[0], ex.args[1]))
    sys.exit(2)

# calculate the first pixel in each timeline section, as well as the
# number of pixels per month and store them in the timeline section
# dictionary for future reference

startPixel = int(params['TIMELINE.leftmargin'])
for section in timelineSections:
    section['startPixel'] = startPixel
    section['pixelsPerMonth'] = float(params['TIMELINE.intervalsize']) \
                               / float(section['interval'])
    startPixel += (section['endDate'] - section['startDate'] +
                   int(params['TIMELINE.resolutioninmonths'])) \
                   / section['interval'] * int(params['TIMELINE.intervalsize'])
totalWidth = startPixel - int(params['TIMELINE.leftmargin'])

# read all the data file items into a list
try:
    rows = readDataFile(params['TIMELINE.datafile'])
    
except IOError, ex:
    sys.stderr.write("%s: error reading datafile %s: %s\n"
                     % (sys.argv[0], params['TIMELINE.datafile'], ex.args[1]))
    sys.exit(2)

# execute all python template bits in the global namespace
lvhtml.init(params['TIMELINE.templatefile'])

# send off any notifications
doNotifications()

# read in the interest file, if there is one
if params.has_key('TIMELINE.interestfile'):
    try:
        readInterestFile(params['TIMELINE.interestfile'])

    except IOError, ex:
        sys.stderr.write("%s: error reading interestfile %s: %s\n"
                         % (sys.argv[0], params['TIMELINE.interestfile'],
                            ex.args[1]))
        sys.exit(2)
                                
# copy over the prototypes of all the non-generated files
try:
    shutil.rmtree(tempDir) # copytree doesn't like pre-existing dirs
    shutil.copytree(options.protoDir, tempDir)
except shutil.Error, ex:
    sys.stderr.write("%s: error copying from %s to %s: %s\n"
                     % (sys.argv[0], options.protoDir, tempDir,
                        ex.args[1]))
    sys.exit(1)

# copy any extra static images into the img-static subdir
for extraImage in extraStaticImages:
    shutil.copy(extraImage['srcName'],
                 os.path.join(tempDir, "img-static", extraImage['destName']))
        
# try and create the img-generated dir just in case it doesn't already exist
try:
    os.mkdir(os.path.join(tempDir, "img-generated"))
except os.error, ex:
    pass

# write out the background image
try:
    writeTimelineBackground(tempDir)
except IOError, ex:
    sys.stderr.write("%s: error writing %s/img-generated/timeline-bg.png: %s\n"
                     % (sys.argv[0], tempDir, ex.args[1]))
    sys.exit(1)

# write out the color swatches used for timeline bars and voting keys
try:
    if params.has_key('EVENTBAR.color1'):
        lvutils.writeColorSwatch(params['EVENTBAR.color1'],
                                 os.path.join(tempDir, "img-generated",
                                              "color1.png"))
    if params.has_key('EVENTBAR.color2'):
        lvutils.writeColorSwatch(params['EVENTBAR.color2'],
                                 os.path.join(tempDir, "img-generated",
                                              "color2.png"))

    if params.has_key('EVENTBAR.nocolor'):
        # write yes/no color key
        key1 = sliceMaker.SlicedImage(65,12)
        for i in range(1,13):
            key1.addSlice({'height': 12, 'width': 5, 'lowerSize': i / 12,
                           'lowerColor': params['EVENTBAR.nocolor'],
                           'dividerColor': params['EVENTBAR.nocolor'],
                           'upperColor': params['EVENTBAR.yescolor'],
                           'saturation': float(params['EVENTBAR.saturation']),
                           'brightness': .5})
        key1.generate(os.path.join(tempDir, "img-generated", "key1.png"))
        
        # write interest-data intensity key
        key2 = sliceMaker.SlicedImage(10,10)
        for i in range(1,6):
            key2.addSlice({'height': 10, 'width': 2, 'lowerSize': 0.6,
                           'lowerColor': params['EVENTBAR.nocolor'],
                           'dividerColor': params['EVENTBAR.nocolor'],
                           'upperColor': params['EVENTBAR.yescolor'],
                           'saturation': float(params['EVENTBAR.saturation']),
                           'brightness': 1.0 - 0.2 * i})
        key2.generate(os.path.join(tempDir, "img-generated", "key2.png"))
            
except IOError, ex:
    sys.stderr.write("%s: error writing color swatches and key images: %s\n"
                     % (sys.argv[0], ex.args[1]))
    sys.exit(1)

# generate the nav cell list and write out the now navcell PNGs
if not navCellsManuallySpecified:
    generateNavCellList()
try:
    writeNowNavCells(tempDir)
except IOError, ex:
    sys.stderr.write("%s: error writing now nav cells: %s\n"
                     % (sys.argv[0], tempDir, ex.args[1]))
    sys.exit(1)

# write the main HTML page (index.html)
try:
    writeIndex(tempDir)
except IOError, ex:
    sys.stderr.write("%s: error writing %s/index.html: %s\n"
                     % (sys.argv[0], tempDir, ex.args[1]))
    sys.exit(1)

# write the header frame
try:
    writeHeaderFrame(tempDir)
except IOError, ex:
    sys.stderr.write("%s: error writing %s/header.html: %s\n"
                     % (sys.argv[0], tempDir, ex.args[1]))
    sys.exit(1)

# write out the timeline frame
writeTimelineFrame(rows, tempDir)

# write out the stylesheets
try:
    cssFile = open(os.path.join(tempDir, "styles.css"), "wt")
    cssFile.write(lvhtml.stylesheets)
    cssFile.close()
except IOError, ex:
    sys.stderr.write("%s: error writing : %s\n"
                     % (sys.argv[0], os.path.join(tempDir, "styles.css"),
                        ex.args[1]))
    sys.exit(1)

# update the existing tree with any changed files; this way we don't blow out
# people's browser caches by unnecessarily changing file timestamps.
lvutils.updateTree(tempDir, options.outputDir)
shutil.rmtree(tempDir)

sys.exit(0)
