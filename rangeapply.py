#!/usr/bin/python

# Process symbol range maps produced by ApplySrg2Source

import os
import srglib

srcRoot = "../CraftBukkit"
rangeMapFile = "/tmp/nms"
mcpDir = "../mcp725-pkgd/conf"
srgFile = "1.4.6/cb2pkgmcp.srg"
rewriteFiles = True
renameFiles = True

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
            #key = "package "+packageName # ignore old name (unique identifier is filename)
            key = "package "+filename
        elif kind == "class":
            className, = info
            key = "class "+srglib.sourceName2Internal(className)
        elif kind == "field":
            className, fieldName = info
            key = "field "+srglib.sourceName2Internal(className)+"/"+fieldName
        elif kind == "method":
            className, methodName, methodSignature = info
            key = "method "+srglib.sourceName2Internal(className)+"/"+methodName+" "+methodSignature
        elif kind == "param":
            className, methodName, methodSignature, parameterName, parameterIndex = info
            key = "param "+srglib.sourceName2Internal(className)+"/"+methodName+" "+methodSignature+" "+str(parameterIndex)  # ignore old name (positional)
        elif kind == "localvar":
            className, methodName, methodSignature, variableName, variableIndex = info
            key = "localvar "+srglib.sourceName2Internal(className)+"/"+methodName+" "+methodSignature+" "+str(variableIndex) # ignore old name (positional)
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
    importMaps = {}

    # CB -> packaged MCP class/field/method
    _notReallyThePackageMap, classMap, fieldMap, methodMap, methodSigMap = srglib.readSrg(srgFile)
    for old,new in classMap.iteritems():
        maps["class "+old]=srglib.splitBaseName(new) 
        importMaps["class "+old]=srglib.internalName2Source(new)  # when renaming class, need to import it, too
    for old,new in fieldMap.iteritems():
        maps["field "+old]=srglib.splitBaseName(new)
    for old,new in methodMap.iteritems():
        maps["method "+old]=srglib.splitBaseName(new)

    # CB source file -> package
    for cbClass, mcpClass in classMap.iteritems():
        cbFile = "src/main/java/"+cbClass+".java"
        mcpPackage = srglib.splitPackageName(mcpClass)
        maps["package "+cbFile] = srglib.internalName2Source(mcpPackage)

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

    return maps, importMaps

# Sort range map by starting offset
# Needed since symbol range output is not always guaranteed to be in source file order
def sortRangeMap(rangeMap):
    sortedRangeMap = []

    print "---"
    starts = {}
    for key,r in rangeMap.iteritems():
        start,end = r
        assert not starts.has_key(start), "Range map invalid: multiple symbols starting at "+start
        starts[start] = end,key
    prevEnd = 0
    for start in sorted(starts.keys()):
        end,key = starts[start]
        sortedRangeMap.append((key, start, end))

        # sanity check
        assert start > prevEnd, "Range map invalid: overlapping symbols at "+start
        prevEnd = end
        #print start,end

    return sortedRangeMap

# Add new import statements to source
def addImports(data, newImports):
    lines = data.split("\n")
    lastNativeImport = None
    existingImports = []
    # Parse the existing imports and find out where to add ours
    # This doesn't use Psi.. but the syntax is easy enough to parse here
    for i, line in enumerate(lines):
        if line.startswith("import net.minecraft"):
            lastNativeImport = i
            existingImports.append(line)

    if  lastNativeImport is None:
        insertionPoint = 3
    else:
        insertionPoint = lastNativeImport

    importsToAdd = []
    for imp in newImports:
        if imp in existingImports: continue
        importsToAdd.append("import %s;" % (imp,))
    print "Adding %s imports" % (len(newImports,))

    splice = lines[0:insertionPoint] + importsToAdd + lines[insertionPoint:]
    return "\n".join(splice)



# Rename symbols in source code
def processJavaSourceFile(filename, rangeMap, renameMap, importMap):
    path = os.path.join(srcRoot, filename)
    data = file(path).read()

    importsToAdd = []

    shift = 0

    sortedRangeMap = sortRangeMap(rangeMap)

    firstClassNewName = None

    for key,start,end in sortedRangeMap:
        oldName = data[start+shift:end+shift]

        if key.startswith("localvar"):
            # Temporary hack to rename local variables without a mapping
            # This is not accurate.. variables are not always monotonic nor sequential
            # TODO: extract local variable map from MCP source with same tool, range map -> local var
            newName = "var%s" % ((int(key.split(" ")[-1]) + 1),)
        else:
            if not renameMap.has_key(key):
                print "No rename for "+key
                continue
            newName = renameMap[key]

        print "Rename",key,[start+shift,end+shift],"::",oldName,"->",newName

        if importMap.has_key(key):
            # this rename requires adding an import
            importsToAdd.append(importMap[key])
        if firstClassNewName is None and key.startswith("class "):
            # remember first class declared in this file, for renaming the file
            firstClassNewName = renameMap[key]

        # Rename algorithm: 
        # 1. textually replace text at specified range with new text
        # 2. shift future ranges by difference in text length
        data = data[0:start+shift] + newName + data[end+shift:]
        shift += len(newName) - len(oldName)

    # Lastly, update imports
    data = addImports(data, importsToAdd)

    newPackage = srglib.sourceName2Internal(renameMap["package "+filename])
    newFilename = os.path.join(srcRoot, "src/main/java/", newPackage, firstClassNewName + ".java")
    newPath = os.path.join(srcRoot, newFilename)

    if rewriteFiles:
        print "Writing",filename
        file(path,"w").write(data)
    if renameFiles:
        print "Rename file",filename,"->",newFilename
        srglib.rename_path(path, newPath)

def main():
    renameMap, importMap = getRenameMaps(srgFile, mcpDir)
    rangeMapByFile = readRangeMap(rangeMapFile)

    for filename in sorted(rangeMapByFile.keys()):
        processJavaSourceFile(filename, rangeMapByFile[filename], renameMap, importMap)

if __name__ == "__main__":
    main()

