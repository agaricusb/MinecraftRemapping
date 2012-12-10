#!/usr/bin/python

# Quick-and-dirty textual rename of class names

import sys, os

def process(filename, target):
    f = file(filename)
    for line in f.readlines():
        line = line.strip()
        tokens = line.strip().split()
        if tokens[0] != "CL:": continue
        args = tokens[1:]

        inFullName, outFullName = args

        inName = lastComponent(inFullName)
        outName = lastComponent(outFullName)

        print "Rename: %s -> %s" % (inName, outName)

        cmd = "find '%s' -type f -name '*.java' -exec perl -pe's/(\W)%s(\W)/$1%s$2/g' -i {} \;" % (target, inName, outName)
        print cmd
        #os.system(cmd)

def lastComponent(fullName):
    return fullName.split("/")[-1]

if len(sys.argv) != 3:
    print "Usage: %s mcp2cb-only-classes-prefixed.srg target-dir/" % (sys.argv[0],)
    raise SystemExit

filename = sys.argv[1]
target = sys.argv[2]

process(filename, target)

