#!/usr/bin/python -tt

# make a distribution of longview
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

import sys
import glob
import os

from distutils.core import setup

# walk the prototype-html tree and generate the set of all relevant files
protoFiles = []
for dirpath, dirnames, filenames in os.walk("prototype-html"):
    # don't want to install CVS goop
    if dirpath.endswith("CVS"):
        continue
    # generate the set of files in this directory
    fileSet = []
    for name in filenames:
        fileSet.append((os.path.join(dirpath, name)))
    # 
    protoFiles.append((os.path.join("longview", dirpath), fileSet))

setup(name="longview",
      version="1.0",
      author="The Long Now Foundation",
      author_email="timeline@list.longnow.org",
      url="http://www.longnow.org/",
      py_modules=["lvhtml", "lvutils", "lvnotify", "sliceMaker"],
      scripts=["longview.py"],
      data_files=[("longview/examples",
                   glob.glob("biotech-*") + glob.glob("bets-*"))] + protoFiles)



# just notes to myself, mostly
#
if "sdist" in sys.argv:
    
    print "\nBe sure you did all these things before creating the tarball:\n"
    print " 1. update version number in longview.py and setup.py"
    print " 2. update ChangeLog using cvs2cl.pl"
    print " 3. update NEWS"
    
