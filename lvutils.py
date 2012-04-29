#!/usr/bin/python -tt
"""Utility classes for implementing Long View functionality."""

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

__author__ = "Dan Mosedale <timeline@list.longnow.org>"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2004 The Long Now Foundation"
__license__ = "BSD-style"

# in pre 3.0 versions of python, without this import, 9/2=4, not 4.5.
from __future__ import division

import os
import re
import shutil
from filecmp import dircmp

import gd


class NowCellPNG:
    """A class to build PNGs for the "now" nav cell"""

    def __init__(self, filename, onCell, nowXCoord):
        """Initialize a NowCellPNG object

        filename -- filename to write cell to
        onCell -- is this the "on" version of the cell?
        nowXCoord -- the X coordinate of the now
        """

        self.filename = filename
        self.onCell = onCell
        self.nowXCoord = nowXCoord

        self.width = 25
        """Width of the entire navcell"""
        
        self.height = 20
        """Height of the entire navcell"""

        self.backgroundColor = (0xff, 0xff, 0xff)
        
        self.stippleColor = (0x99, 0x99, 0x99)

        self.borderColor = (0x00, 0x33, 0x66)

        self.nowBoxColor = (0x66, 0x66, 0x66)

        self.nowBoxWidth = 4
        
        return

    def generate(self):
        """Build and write the PNG file"""

        img = gd.image((self.width, self.height))

        # allocate the background as "white", but set it to be transparent
        bgColorIndex = img.colorAllocate(self.backgroundColor)
        stippleColorIndex = img.colorAllocate(self.stippleColor)
        img.colorTransparent(bgColorIndex)

        # set up the stipple pattern
        stipple = gd.image((2,2))
        stippleBgColorIndex = stipple.colorAllocate(self.backgroundColor)
        stippleFgColorIndex = stipple.colorAllocate(self.stippleColor)
        stipple.colorTransparent(stippleBgColorIndex)
        stipple.setPixel((0,0), stippleFgColorIndex)
        stipple.setPixel((1,1), stippleFgColorIndex)

        # draw the stippled background
        img.setTile(stipple)
        img.filledRectangle((1,1), (self.width-2, self.height-2), gd.gdTiled)

        # draw the now box
        nowBoxColorIndex = img.colorAllocate(self.nowBoxColor)
        img.rectangle(
            (self.nowXCoord, 1),
            (self.nowXCoord + self.nowBoxWidth, self.height - 2),
            nowBoxColorIndex)
        img.fillToBorder((self.nowXCoord+1, 2), nowBoxColorIndex, bgColorIndex)
                         
        # draw the border if the cell is "on"
        if self.onCell:
            borderColorIndex = img.colorAllocate(self.borderColor)
            img.rectangle((1,0), (self.width-1, self.height-1),
                          borderColorIndex)
        
        # write out the file
        outputFile = open(self.filename, "w")
        img.writePng(outputFile)
        outputFile.close()

        return

    
def updateTree(srcdir, destdir):
    """Update destdir with any changes made to srcdir"""

    if not os.path.isdir(destdir):
        os.mkdir(destdir, 0755)
        
    comparison = dircmp(srcdir, destdir)

    # copy over any files that differ
    for file in comparison.diff_files:
        shutil.copyfile(os.path.join(srcdir, file),
                        os.path.join(destdir, file))

    # recurse on any common directories
    for directory in comparison.common_dirs:
        if directory == "CVS":
            continue
        updateTree(os.path.join(srcdir, directory),
                   os.path.join(destdir, directory))

    # copy over anything that's in the src directory only
    for entry in comparison.left_only:
        if os.path.isdir(os.path.join(srcdir, entry)):
            shutil.copytree(os.path.join(srcdir, entry),
                            os.path.join(destdir, entry))
        else:
            shutil.copyfile(os.path.join(srcdir, entry),
                            os.path.join(destdir, entry))

    # get rid of anything that's no longer in the src tree
    for entry in comparison.right_only:
        if os.path.isdir(os.path.join(destdir, entry)):
            shutil.rmtree(os.path.join(destdir, entry))
        else:
            os.remove(os.path.join(destdir, entry))
    return


def writeColorSwatch(color, filename):
    """Write a 1x1 png of the given color.

    color -- an RGB tuple
    filename -- name of the PNG file
    """

    image = gd.image((1,1))

    # all we have to do is allocate the background color; no need to draw
    # anything in the foreground
    image.colorAllocate(color)

    # write the file
    file = open(filename, "w")
    image.writePng(file)
    file.close()

    return


alwaysPrint5DigitYears = True
"""Always zero pad years to be five digits long?"""

dateResolutionDefaultsToYears = True
"""Assume that dates are to be displayed in years?"""

class LVDate(int):
    """A date (at month resolution) on a timeline"""

    # __new__ is used instead of __init__ because we are overriding a builtin
    # type.  http://www.python.org/2.2.1/descrintro.html#__new__ has details.
    #
    def __new__(className, date):

        # construct from a raw integer or another lvdate
        if issubclass(date.__class__, int):
            return int.__new__(LVDate, date)

        # assume we've got a string, and parse it into a single integer
        # representing either an absolute date or a duration in months
        parseRE = re.compile(
            """(?P<year>\d+)?                # year (years if a duration)
            (/(?P<month>\d+))?               # month (months if a duration)
            (?P<isBCE>\s?B\.?C\.?E?\.?)?     # is this BCE?
            """, re.I | re.X)
        parseMatch = parseRE.match(date)

        months = 0
        if parseMatch.group('year'):
            months = int(parseMatch.group('year')) * 12

        if parseMatch.group('month'):
            months += int(parseMatch.group('month')) - 1

        if parseMatch.group('isBCE'):
            months *= -1
            
        return int.__new__(LVDate, months)

    # workaround for python 2.3.3 bug/feature (apparently guido says this
    # is not a bug).  without this hack, <class LVDate> + <class LVDate>
    # returns <int>.  I suspect that if we start using more / other operators
    # on LVDate operands in the code, we may need to add more similar
    # overrides.
    def __add__(self, other):
        return LVDate(int.__add__(self, other))

    def __sub__(self, other):
        return LVDate(int.__sub__(self, other))

    def toString(self, spaceBeforeBC=False, periods=False,
                 resolutionInYears=None,
                 monthSeparator="/"):
        """Return a human-readable string representation of this date.

        spaceBeforeBC -- should there be a space between the number and the BC?
           defaults to False
        periods -- should BC have periods after the letters?
           defaults to False
        resolutionInYears -- should we print this as years only?
           defaults to the value of dateResolutionDefaultsToYears
        monthSeperator -- string to use to separate years from months
           defaults to "/"
        """

        yearNum = self/12

        # if the ongoing attribute ongoing is set to True, print this as ?
        if hasattr(self, "ongoing") and self.ongoing:
            return "?"
        
        if abs(yearNum) == yearNum:
            bc = ""
            space = ""
        else:
            if periods:
                bc = "B.C."
            else:
                bc = "BC"

            if spaceBeforeBC:
                space = " "
            else:
                space = ""

        if alwaysPrint5DigitYears:
            yearString = "%05d" % abs(yearNum)
        else:
            yearString = str(abs(yearNum))

        if (resolutionInYears is None and dateResolutionDefaultsToYears) \
               or resolutionInYears is True:
            return yearString + space + bc
        else:
            return yearString + monthSeparator + str(self % 12 + 1) \
                   + space + bc


class Background:
    """Class representing the background image for a timeline."""

    def __init__(self, width, height, nowStartXCoord):
        """Initialize a background object.

        width -- width of the background
        height -- height of the background
        nowStartXCoord --- starting X coordinate of the 'now' bar
        """
        
        self.width = width
        self.height = height
        self.nowStartXCoord = nowStartXCoord
        
        self.dividerWidth = 8
        """Number of pixels between left and right vertical divider lines"""
        
        self.intervalSize = 100
        """Number of pixels representing a single interval"""
        
        self.nowColor = (0x99, 0x99, 0xcc)
        """Color of the 'now' bar"""

        self.nowWidth = 10
        """Number of pixels wide to make the 'now' bar"""
        
        self.stippleColor = (0x99, 0x99, 0x99)
        """Color to use in the stippling pattern for the 'future' section"""
        
        self.backgroundColor = (0xff, 0xff, 0xff)
        """(R,G,B) tuple of background color."""
        
        self.darkDividerColor = (0xaa, 0xaa, 0xaa)
        """(R,G,B) tuple of dark divider color."""
        
        self.lightDividerColor = (0xdd, 0xdd, 0xdd)
        """(R,G,B) tuple of light divider color."""
        
        self.__img = gd.image((width, height))
        return
        
    def generate(self, filename):
        """Generate a background image suitable for a longview timeline."""

        # draw vertical dividers
        def drawDividers(startPoint, colorTuple):
            """Draw vertical timeline dividers once per self.intervalSize."""

            brush = gd.image((self.dividerWidth, 1))

            # set up the colors
            backgroundColorIndex = brush.colorAllocate(self.backgroundColor)
            colorIndex = brush.colorAllocate(colorTuple)
            brush.colorTransparent(backgroundColorIndex)

            # set up the pattern
            brush.setPixel((0,0), colorIndex)
            brush.setPixel((self.dividerWidth-1,0), colorIndex)
            self.__img.setBrush(brush)

            # draw the lines
            i = startPoint
            while i <= self.width:
                self.__img.line( (i,0), (i, self.height-1), gd.gdBrushed)
                i = i + self.intervalSize

        # setup
        backgroundColorIndex = self.__img.colorAllocate(self.backgroundColor)
        self.__img.colorTransparent(backgroundColorIndex)
        lightDividerColorIndex = self.__img.colorAllocate(
            self.lightDividerColor)
        darkDividerColorIndex = self.__img.colorAllocate(self.darkDividerColor)

        # draw the bottom line, dash-style
        self.__img.setStyle((backgroundColorIndex, lightDividerColorIndex))
        self.__img.line((0,self.height-1), (self.width,self.height-1),
                        gd.gdStyled)

        # draw the vertical dividers
        drawDividers(int(self.dividerWidth/2), self.lightDividerColor)
        drawDividers(int(self.intervalSize/2 + self.dividerWidth/2),
                     self.darkDividerColor)

        # add now box
        nowColorIndex = self.__img.colorAllocate(self.nowColor)
        self.__img.filledRectangle( (self.nowStartXCoord, 0),
                                    (self.nowStartXCoord + self.nowWidth-1, \
                                     self.height-1), nowColorIndex )

        # draw the future stippling
        stipple = gd.image((2,2))
        stippleBgColorIndex = stipple.colorAllocate(self.backgroundColor)
        stippleColorIndex = stipple.colorAllocate(self.stippleColor)
        stipple.colorTransparent(stippleBgColorIndex)
        stipple.setPixel((1,0), stippleColorIndex)

        self.__img.setTile(stipple)
        self.__img.filledRectangle((self.nowStartXCoord + self.nowWidth, 0),
                                   (self.width-1, self.height-1), gd.gdTiled)

        # write out the file
        file = open(filename, "w")
        self.__img.writePng(file)
        file.close()

        return
