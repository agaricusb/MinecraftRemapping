#!/usr/bin/python

# Process symbol range maps produced by ApplySrg2Source

import os


srcRoot = "../CraftBukkit"
rangeMap = "/tmp/nms4"

def loadSrg(filename):
    for line in file(filename).readlines():
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

for line in file(rangeMap).readlines():
    tokens = line.strip().split(",")
    if tokens[0] != "@": continue
    filename, startRangeStr, endRangeStr, kind = tokens[1:5]
    info = tokens[5:]
    startRange = int(startRangeStr.replace("(",""))
    endRange = int(endRangeStr.replace(")",""))

    data = file(os.path.join(srcRoot, filename)).read()
    oldName = data[startRange:endRange]

    print filename,[startRange,endRange],kind,info
