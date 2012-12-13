#!/usr/bin/python

import sys

if len(sys.argv) < 2:
    print "Reverse srg mapping"
    print "Usage: %s file.srg" % (sys.argv[0],)
    raise SystemExit


filename = sys.argv[1]

f = file(filename)
for line in f.readlines():
    line = line.strip()
    tokens = line.split(" ")
    kind = tokens[0]
    args = tokens[1:]
    if kind == "PK:":  # package
        print line
    elif kind == "CL:": # class
        inName, outName = args
        print kind, outName, inName
    elif kind == "FD:": # field
        inName, outName = args
        print kind, outName, inName
    elif kind == "MD:": # method
        inName, inSig, outName, outSig = args
        print kind, outName, outSig, inName, inSig
    else:
        print line

