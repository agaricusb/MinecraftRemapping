#!/usr/bin/python

# Process symbol range maps produced by ApplySrg2Source

import os
import srglib

srcRoot = "../CraftBukkit"
rangeMapFile = "/tmp/nms"
mcpDir = "../mcp725-pkgd/conf"
srgFile = "1.4.6/cb2pkgmcp.srg"

# Read ApplySrg2Source symbol range map into a dictionary
# keyed by filename, with a dict for each symbol type
def readRangeMap(filename):
    rangeMap = {}
    for line in file(filename).readlines():
        tokens = line.strip().split("|")
        if tokens[0] != "@": continue
        filename, startRangeStr, endRangeStr, kind = tokens[1:5]
        startRange = int(startRangeStr)
        endRange = int(endRangeStr)
        info = tokens[5:]

        k = {"start":startRange, "end":endRange}
        if kind == "package":
            k["packageName"] = info
        elif kind == "class":
            k["className"] = info
        elif kind == "field":
            k["className"], k["fieldName"] = info
        elif kind == "method":
            k["className"], k["methodName"], k["methodSignature"] = info
        elif kind == "param":
            k["className"], k["methodName"], k["methodSignature"], k["parameterName"], k["parameterIndex"] = info
        elif kind == "localvar":
            k["className"], k["methodName"], k["methodSignature"], k["variableName"], k["variableIndex"] = info
        else:
            assert False, "Unknown kind: "+kind

        if not rangeMap.has_key(filename):
            rangeMap[filename] = {"package":[], "class":[], "field":[], "method":[], "param":[], "localvar":[]}

        rangeMap[filename][kind] = k

        #data = file(os.path.join(srcRoot, filename)).read()
        #oldName = data[startRange:endRange]
        #print filename,[startRange,endRange],kind,info

    return rangeMap

def main():
    paramMap = srglib.readParameterMap(mcpDir)
    packageMap, classMap, fieldMap, methodMap = srglib.readSrg(srgFile)
    rangeMapByFile = readRangeMap(rangeMapFile)

    for filename, rangeMap in rangeMapByFile.iteritems():
        print filename,rangeMap

if __name__ == "__main__":
    main()

