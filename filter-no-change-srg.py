#!/usr/bin/python

import sys

def process(filename):
    f = file(filename)
    patterns = []
    for line in f.readlines():
        line = line.strip()
        tokens = line.strip().split()
        if tokens[0] != "CL:": continue
        args = tokens[1:]

        inFullName, outFullName = args

        inName = lastComponent(inFullName)
        outName = lastComponent(outFullName)

        if inName != outName.replace("cbtmp_", ""):
            print line

def lastComponent(fullName):
    return fullName.split("/")[-1]

if len(sys.argv) != 2:
    print "Usage: %s cb2mcp-only-classes-prefixed.srg" % (sys.argv[0],)
    raise SystemExit

filename = sys.argv[1]

process(filename)

