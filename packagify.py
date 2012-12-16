#!/usr/bin/python

# Prepend new MCP package names to classes from stdin to stdout

import sys

mcpdir = "../MinecraftForge/mcp/"

def getPackages():
    cls2pkg = {}
    fn = mcpdir + "conf/packages.csv"
    for line in file(fn).readlines():
        cls, pkg = line.strip().split(",")
        if cls == "class" or pkg == "package": continue
        cls2pkg[cls] = pkg

    return cls2pkg

if __name__ == "__main__":
    cls2pkg = getPackages()

    while True:
        line = sys.stdin.readline()
        if len(line) == 0: break

        inClass = line.strip()
        if not cls2pkg.has_key(inClass):
            print "No such class: "+inClass
            continue

        print cls2pkg[inClass] + "/" + inClass


