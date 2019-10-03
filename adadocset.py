#!/usr/bin/env python3
# Copyright (c) 2019 Bartek thindil Jasicki <thindil@laeran.pl>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Build Ada 2012 specification docset from the HTML version of it."""

import re
import sqlite3

CONN = sqlite3.connect('Ada.docset/Contents/Resources/docSet.dsidx')
CUR = CONN.cursor()
CUR.execute('DROP TABLE searchIndex;')
CUR.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')

# Packages, Types, Subprograms, Objects
FILENAMES = ["RM-Q-1.html", "RM-Q-2.html", "RM-Q-3.html", "RM-Q-4.html", "RM-Q-5.html"]
TYPES = ["Package", "Type", "Function", "Exception", "Object"]
for j in range(len(FILENAMES)):
    with open("Ada.docset/Contents/Resources/Documents/" + FILENAMES[j]) as fn:
        content = fn.readlines()
    i = 0
    while i < len(content):
        line = content[i].strip()
        if line.startswith("<div class=\"Index\">"):
            line = line[19: ]
            result = re.search("^\w+", line)
            name = line[ :result.span()[1]]
            while line.find("<A HREF=") == -1:
                i += 1
                line = content[i].strip()
            line = line[line.find("<A HREF=") + 9:]
            path = line[:line.find("\"")]
            CUR.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)',
                        (name, TYPES[j], path))
        i += 1

#Pragmas
with open("Ada.docset/Contents/Resources/Documents/RM-L.html") as fn:
    CONTENT = fn.readlines()
i = 0
while i < len(CONTENT):
    LINE = CONTENT[i].strip()
    if LINE.find("<B>pragma</B>") > 0:
        while CONTENT[i].find("</div>") == -1:
            LINE += CONTENT[i].strip()
            i += 1
        LINE += CONTENT[i].strip()
        RESULT = re.search(">\w+(\[|\(|;)", LINE)
        NAME = LINE[RESULT.span()[0] + 1 : RESULT.span()[1] - 1]
        LINE = LINE[LINE.find("See <A HREF=") + 13:]
        PATH = LINE[:LINE.find("\"")]
        CUR.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)',
                    (NAME, "Directive", PATH))
    i += 1

#Aspects and Attributes
FILENAMES = ["RM-K-1.html", "RM-K-2.html"]
TYPES = ["Property", "Attribute"]
for j in range(len(FILENAMES)):
    with open("Ada.docset/Contents/Resources/Documents/" + FILENAMES[j]) as fn:
        content = fn.readlines()
    i = 0
    while i < len(content):
        line = content[i].strip()
        if line.startswith("<div class=\"WideHanging-Term\">") > 0:
            line = line[30:]
            result = re.search("[A-Z]+.+</", line)
            name = line[result.span()[0] : result.span()[1] - 2]
            while content[i].find("See <A HREF=") == -1:
                i += 1
            line = content[i].strip()
            line = line[line.find("See <A HREF=") + 13:]
            path = line[:line.find("\"")]
            CUR.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)',
                        (name, TYPES[j], path))
        i += 1

# Chapters
with open("Ada.docset/Contents/Resources/Documents/RM-TOC.html") as fn:
    CONTENT = fn.readlines()
i = 0
START = False
while i < len(CONTENT):
    LINE = CONTENT[i].strip()
    if LINE == "<HR>":
        START = not START
    if START and LINE.find("<A HREF=") > -1:
        LINE = LINE[LINE.find("<A HREF=") + 9:]
        PATH = LINE[:LINE.find("\"")]
        NAME = LINE[LINE.find("\"") + 2:LINE.find("</A>")]
        CUR.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)',
                    (NAME, "Section", PATH))
    i += 1

CONN.commit()
CONN.close()
