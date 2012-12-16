#!/usr/bin/python

import sys

if len(sys.argv) < 2:
    print "Translate symbols on stdin to stdout through srg"
    print "\t%s srg < in > out"% (sys.argv[0],)
    raise SystemExit

classes = {}
filename = sys.argv[1]

f = file(filename)
for line in f.readlines():
    line = line.strip()
    tokens = line.split(" ")
    kind = tokens[0]
    args = tokens[1:]
    if kind == "PK:":  # package
        # TODO
        pass
    elif kind == "CL:": # class
        inName, outName = args
        classes[inName] = outName
    elif kind == "FD:": # field
        inName, outName = args
        # TODO
    elif kind == "MD:": # method
        # TODO
        pass
    else:
        pass

while True:
    line = sys.stdin.readline()
    if len(line) == 0: break
    inName = line.strip()

    print classes.get(inName, "Not found: "+inName)
