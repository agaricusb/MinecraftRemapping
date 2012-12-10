#!/usr/bin/python

# Generate Perl script for quick-and-dirty textual rename of class names

import sys, os, re

def walk(_, dirname, fnames):
    for filename in fnames:
        if not filename.endswith(".java"): continue
        path = os.path.join(dirname, filename)
        print path

        data = file(path, "r").read()
        print len(data)


def process(filename):
    f = file(filename)
    patterns = []
    print "#!/usr/bin/perl -pi"
    for line in f.readlines():
        line = line.strip()
        tokens = line.strip().split()
        if tokens[0] != "CL:": continue
        args = tokens[1:]

        inFullName, outFullName = args

        inName = lastComponent(inFullName)
        outName = lastComponent(outFullName)

        print "s/(\W)%s(\W)/$1%s$2/g;" % (inName, outName)

def lastComponent(fullName):
    return fullName.split("/")[-1]

if len(sys.argv) != 2:
    print "Usage: %s mcp2cb-only-classes-prefixed.srg" % (sys.argv[0],)
    raise SystemExit

filename = sys.argv[1]

process(filename)

