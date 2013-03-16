#!/usr/bin/python

# Find symbols not deobfuscated in MCP, yet deobfuscated in CB

# py nonobf.py < 1.5/cb2pkgmcp.srg

import sys
import srglib

def isUnmappedMCP(s):
    return "func_" in s or "field_" in s

def isUnmappedCB(s):
    return len(srglib.splitBaseName(s)) < 3

for line in sys.stdin.readlines():
    line = line.strip()
    tokens = line.split(" ")
    kind = tokens[0]
    args = tokens[1:]
    if kind == "PK:":  # package
        pass
    elif kind == "CL:": # class
        inName, outName = args
        pass
    elif kind == "FD:": # field
        inName, outName = args
        if not isUnmappedCB(inName) and isUnmappedMCP(outName):
            print kind, inName, outName
    elif kind == "MD:": # method
        inName, inSig, outName, outSig = args
        if not isUnmappedCB(inName) and isUnmappedMCP(outName):
            print kind, inName, inSig, outName, outSig
    else:
        pass

