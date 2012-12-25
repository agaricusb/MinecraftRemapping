#!/usr/bin/python

# Process symbol range maps produced by ApplySrg2Source

import os
import srglib

srcRoot = "../CraftBukkit"
rangeMapFile = "/tmp/nms"
mcpDir = "../mcp725-pkgd/conf"
srgFile = "1.4.6/cb2pkgmcp.srg"

# Read ApplySrg2Source symbol range map into a dictionary
# Keyed by filename -> dict of unique identifiers -> range
def readRangeMap(filename):
    rangeMap = {}
    for line in file(filename).readlines():
        tokens = line.strip().split("|")
        if tokens[0] != "@": continue
        filename, startRangeStr, endRangeStr, kind = tokens[1:5]
        startRange = int(startRangeStr)
        endRange = int(endRangeStr)
        info = tokens[5:]

        # Build unique identifier for symbol
        if kind == "package":
            packageName, = info
            key = "package "+packageName
        elif kind == "class":
            className, = info
            key = "class "+className
        elif kind == "field":
            className, fieldName = info
            key = "field "+className.replace(".","/")+"/"+fieldName
        elif kind == "method":
            className, methodName, methodSignature = info
            key = "method "+className.replace(".","/")+"/"+methodName+" "+methodSignature
        elif kind == "param":
            className, methodName, methodSignature, parameterName, parameterIndex = info
            key = "param "+className.replace(".","/")+"/"+methodName+" "+methodSignature+" "+str(parameterIndex)  # ignore old name (positional)
        elif kind == "localvar":
            className, methodName, methodSignature, variableName, variableIndex = info
            key = "localvar "+className.replace(".","/")+"/"+methodName+" "+methodSignature+" "+str(variableIndex) # ignore old name (positional)
        else:
            assert False, "Unknown kind: "+kind


        if not rangeMap.has_key(filename):
            rangeMap[filename] = {}

        # Map to range
        rangeMap[filename][key] = (startRange, endRange)

    return rangeMap

# Get all rename maps, keyed by globally unique symbol identifier, values are new names
def getRenameMaps(srgFile, mcpDir):
    maps = {}

    packageMap, classMap, fieldMap, methodMap, methodSigMap = srglib.readSrg(srgFile)
    for old,new in packageMap.iteritems():
        maps["package "+old]=new
    for old,new in classMap.iteritems():
        maps["class "+old]=new
    for old,new in fieldMap.iteritems():
        maps["field "+old]=new
    for old,new in methodMap.iteritems():
        maps["method "+old]=new

    # Read parameter map.. it comes from MCP with MCP namings, so have to remap to CB 
    mcpParamMap = srglib.readParameterMap(mcpDir)
    invMethodMap, invMethodSigMap = srglib.invertMethodMap(methodMap, methodSigMap)
    cbParamMap, removedParamMap = srglib.remapParameterMap(mcpParamMap, invMethodMap, invMethodSigMap)
    # removedParamMap = methods in FML/MCP repackaged+joined but not CB = client-only methods

    for old,new in cbParamMap.iteritems():
        for i in range(0,len(new)):
            #print "RENPARAM","param %s %s" % (old, i),"->",new[i]
            maps["param %s %s" % (old, i)] = new[i]
    # TODO: local variable map

    return maps


def main():
    renameMap = getRenameMaps(srgFile, mcpDir)
    rangeMapByFile = readRangeMap(rangeMapFile)

    for filename, rangeMap in rangeMapByFile.iteritems():
        data = file(os.path.join(srcRoot, filename)).read()

        for key,r in rangeMap.iteritems():
            start, end = r
            oldName = data[start:end]
            if not renameMap.has_key(key):
                print "No rename for "+key
                continue
            newName = renameMap[key]
            print oldName,"->",newName

if __name__ == "__main__":
    main()

