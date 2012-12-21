#!/usr/bin/python

# Filter srg removing names that didn't change

import sys

for line in sys.stdin.readlines():
    line = line.strip()
    tokens = line.split(" ")
    kind = tokens[0]
    args = tokens[1:]
    if kind == "PK:":  # package
        print line
    elif kind == "CL:": # class
        inName, outName = args
        if inName != outName:
            print kind, inName, outName
    elif kind == "FD:": # field
        inName, outName = args
        if inName != outName:
            print kind, inName, outName
    elif kind == "MD:": # method
        inName, inSig, outName, outSig = args
        if inName != outName:
            print kind, inName, inSig, outName, outSig
    else:
        print line

