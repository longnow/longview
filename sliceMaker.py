#!/usr/bin/env python

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

__author__ = "John Tangney and Dan Mosedale <timeline@list.longnow.org>"
__version__ = "1.0"
__copyright__ = "Copyright (c) The 2004 Long Now Foundation"
__license__ = "BSD-style"

# in pre 3.0 versions of python, without this import, 9/2=4, not 4.5.
from __future__ import division

import sys
import string
import math
import csv

import gd


class SlicedImage:

    def __init__(self, width, height):
        self.__image = gd.image((width, height))
        self.__xOffset = 0
        self.__height = height
        
        self.diamondWidth = 7
        """Width of any diamonds rendered."""

        self.diamondLeftMargin = 2
        """Width of horizontal margin on the left side a diamond"""

        self.diamondVerticalMargin = 0
        """Height of vertical margin above and below a diamond"""
        
        self.diamondColor = (0xff, 0xff, 0xff)
        """Color used to render diamonds."""

        return

    def addSlice(self, fields):
        """Add a slice to this image"""
        
        # Returns a tuple of adjusted r, g, b integers given tuple of integers.
        def computeRgbValues(rgb, saturation, brightness):
            return map((lambda x:
                        adjustColorComponent(x, saturation, brightness)), rgb)

        # Returns an integer value for the given component, adjusted for
        # brightness and saturation.
        def adjustColorComponent(component, saturation, brightness):
            answer = component * saturation + brightness * 255.0 * \
                     (1 - saturation)
            return int(round(answer))

        width = fields["width"]
        height = fields["height"]

        saturation = fields["saturation"]
        brightness = fields["brightness"]

        upperHeight = int(round(height - (height * fields["lowerSize"])))

        tl = (self.__xOffset, upperHeight + 1)
        br = (self.__xOffset + width, height)
        lowerColor = self.__image.colorAllocate(
            computeRgbValues(fields["lowerColor"],  saturation, brightness))
        self.__image.filledRectangle(tl, br, lowerColor)

        tl = (self.__xOffset, upperHeight)
        br = (self.__xOffset + width, upperHeight + 1)
        dividerColor = self.__image.colorAllocate(
            computeRgbValues(fields["dividerColor"], saturation, brightness))
        self.__image.filledRectangle(tl, br, dividerColor)

        tl = (self.__xOffset, 0)
        br = (self.__xOffset + width, upperHeight)
        upperColor = self.__image.colorAllocate(
            computeRgbValues(fields["upperColor"],  saturation, brightness))
        self.__image.filledRectangle(tl, br, upperColor)

        self.__xOffset += width
        
        return

    def drawDiamond(self, startX):
        """Draw a diamond whose leftmost point is at startX."""

        # allocate diamond color, if we haven't already
        if not hasattr(self, '__diamondColorIndex'):
            self.__diamondColorIndex = self.__image.colorAllocate(
                self.diamondColor)

        # calculate the points
        bottomPoint = (startX + int(math.ceil(self.diamondWidth/2)),
                       self.__height-1 - self.diamondVerticalMargin)
        rightPoint = (startX + self.diamondWidth-1, int((self.__height-1)/2))
        topPoint = (startX + int(math.ceil(self.diamondWidth/2)),
                    self.diamondVerticalMargin)
        leftPoint = (startX + self.diamondLeftMargin, int(self.__height/2))

        # draw the diamond
        diamond = (bottomPoint, rightPoint, topPoint, leftPoint)
        self.__image.filledPolygon(diamond, self.__diamondColorIndex)

        return


    def drawFilledSlice(self, startX, width, color):
        """Draw a filled slice

        startX -- X coordinate where slice should start
        width -- width in pixels
        color -- color tuple
        """

        colorIndex = self.__image.colorAllocate(color)
        self.__image.filledRectangle( (startX, 0),
                                      (startX + width - 1, self.__height),
                                      colorIndex )
        return

    
    def generate(self, filename):
        """Write out a PNG file for this image"""

        # write out the file
        file = open(filename, "w")
        self.__image.writePng(file)
        file.close()

        return
        

# Returns a tuple of red, green, and blue integer values, given a hex string
def parseHexColor(hex):
    justHex = hex.split('#')[-1]
    return map((lambda x: string.atoi(x, 16)), (justHex[0:2], justHex[2:4], justHex[4:6]))

    
def calculateTotalSize(inputFileName):
    width = 0
    height = 0
    reader = csv.reader(file(inputFileName))
    for row in reader:
        fields = mapInputFields(row)
        width += fields["width"]
        if fields["height"] > height:
            height = fields["height"]
    return int(width), int(height)

            
# Given a list of input values, return a dictionary of same. This allows us to
# deal with column positions in one place only.
def mapInputFields(row):
    fields = ["height", "width", "lowerSize", "lowerColor", "dividerColor", "upperColor", "saturation", "brightness"]
    numericFieldNos = [0, 1, 2, 6, 7]
    percentFieldNos = [2, 6, 7]
    hexFieldNos = [3, 4, 5]
    i = 0
    answer = {}
    for field in fields:
        value = row[i]
        if i in numericFieldNos:
            value = string.atof(value)
            if i in percentFieldNos:
                value = value / 100.0
        else:
            if i in hexFieldNos:
                value = parseHexColor(value)
        answer[field] = value
        i = i + 1
    return answer


def makeSlices(width, height, inputFileName, outputFileName):

    slices = SlicedImage(width, height);

    reader = csv.reader(file(inputFileName))
    for row in reader:
        fields = mapInputFields(row)
        slices.addSlice(fields)

    slices.generate(outputFileName)
    return


# We write an image per csv file.    
def generateImage(inFile, outFile):
    print "Reading from %s and writing to %s" % (inFile, outFile)
    width, height = calculateTotalSize(inFile)
    
    slices = makeSlices(width, height, inFile, outFile)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "Usage: %s csvfile [pngfile]" % sys.argv[0]
        print "  If pngfile is not specified, its name is derived from csvfile"
    else:
        inFile = sys.argv[1]
        if len(sys.argv) == 2:
            outFile = inFile.split(".")[0] + ".png"
        else:
            outFile = sys.argv[2]
            
        generateImage(inFile, outFile)

