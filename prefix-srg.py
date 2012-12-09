#!/usr/bin/python

import sys

def applyPrefix(symbol, prefix):
    parts = symbol.split("/")
    return "/".join(parts[1:]) + "/" + prefix + parts[-1]

if len(sys.argv) < 3:
    print "Prepends a prefix to renamed symbols, to avoid collisions"
    print "Usage: %s file.srg prefix" % (sys.argv[0],)
    print "Example:"
    print "\t%s cb2mcp.srg cbtmp_" % (sys.argv[0],)
    raise SystemExit


filename = sys.argv[1]
prefix = sys.argv[2]

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
        print kind, inName, applyPrefix(outName, prefix)
    elif kind == "FD:": # field
        inName, outName = args
        print kind, inName, applyPrefix(outName, prefix)
    elif kind == "MD:": # method
        inName, inSig, outName, outSig = args
        print kind, inName, inSig, applyPrefix(outName, prefix), outSig
    else:
        print line

