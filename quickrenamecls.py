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
    print "Save to Perl script /tmp/a, and run: find src -name '*.java' -exec perl -i /tmp/a {} \;"
    print "#!/usr/bin/perl -pi"
    ren = []
    for line in f.readlines():
        line = line.strip()
        tokens = line.strip().split()
        if tokens[0] != "CL:": continue
        args = tokens[1:]

        inFullName, outFullName = args

        inName = lastComponent(inFullName)
        outName = lastComponent(outFullName)

        inName = inName.replace("$", "\$1"); outName = outName.replace("$", "\$1") # TODO: real escaping

        print "s/(\W)%s(\W)/$1%s$2/g;" % (inName, outName)

        ren.append("git mv '%s.java' '%s.java'" % (inName, outName.replace("cbtmp_", "")))

    print
    print "Then run: find . -type perl -pe's/cbtmp_//g' -i {} \;"
    print "And then run renames commands:"
    print "\n".join(ren)



def lastComponent(fullName):
    return fullName.split("/")[-1]

if len(sys.argv) != 2:
    print "Usage: %s cb2mcp-only-classes-prefixed.srg" % (sys.argv[0],)
    raise SystemExit

filename = sys.argv[1]

process(filename)

