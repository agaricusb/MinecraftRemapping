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
#renameFiles = False

dumpRenameMap = True

# Read ApplySrg2Source symbol range map into a dictionary
# Keyed by filename -> list of (range start, end, expectedOldText, key)
def readRangeMap(filename):
    rangeMap = {}
    for line in file(filename).readlines():
        tokens = line.strip().split("|")
        if tokens[0] != "@": continue
        filename, startRangeStr, endRangeStr, expectedOldText, kind = tokens[1:6]
        startRange = int(startRangeStr)
        endRange = int(endRangeStr)
        info = tokens[6:]

        # Build unique identifier for symbol
        if kind == "package":
            packageName, forClass = info

            #key = "package "+packageName # ignore old name (unique identifier is filename)
            if forClass == "(file)":
                forClass = getTopLevelClassForFilename(filename)
            else:
                forClass = srglib.sourceName2Internal(forClass)  # . -> / 
   

            # 'forClass' is the class that is in this package; when the class is
            # remapped to a different package, this range should be updated
            key = "package "+forClass
            
        elif kind == "class":
            className, = info
            key = "class "+srglib.sourceName2Internal(className)
        elif kind == "field":
            className, fieldName = info
            key = "field "+srglib.sourceName2Internal(className)+"/"+fieldName
        elif kind == "method":
            if expectedOldText in ("super", "this"): continue # hack: avoid erroneously replacing super/this calls
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
            rangeMap[filename] = []

        # Map to range
        rangeMap[filename].append((startRange, endRange, expectedOldText, key))

    # Sort and check
    for filename in sorted(rangeMap.keys()):
        sortRangeList(rangeMap[filename], filename)

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

    # CB class -> MCP package name
    for cbClass, mcpClass in classMap.iteritems():
        cbFile = "src/main/java/"+cbClass+".java"
        mcpPackage = srglib.splitPackageName(mcpClass)
        maps["package "+cbClass] = srglib.internalName2Source(mcpPackage)

    # Read parameter map.. it comes from MCP with MCP namings, so have to remap to CB 
    mcpParamMap = srglib.readParameterMap(mcpDir)
    invMethodMap, invMethodSigMap = srglib.invertMethodMap(methodMap, methodSigMap)
    invClassMap = srglib.invertDict(classMap)
    cbParamMap, removedParamMap = srglib.remapParameterMap(mcpParamMap, invMethodMap, invMethodSigMap, invClassMap)
    # removedParamMap = methods in FML/MCP repackaged+joined but not CB = client-only methods

    for old,new in cbParamMap.iteritems():
        for i in range(0,len(new)):
            maps["param %s %s" % (old, i)] = new[i]
    # TODO: local variable map

    if dumpRenameMap:
        for key in sorted(maps.keys()):
            newName = maps[key]
            print "RENAME MAP: %s -> %s" % (key, newName)

    return maps, importMaps

# Add new import statements to source
def updateImports(data, newImports, importMap):
    lines = data.split("\n")
    # Parse the existing imports and find out where to add ours
    # This doesn't use Psi.. but the syntax is easy enough to parse here
    newLines = []
    addedNewImports = False

    newImportLines = []
    for imp in sorted(list(newImports)):
        newImportLines.append("import %s;" % (imp,))

    for i, line in enumerate(lines):
        if line.startswith("import net.minecraft"):
            # Add our new imports first, before existing NMS imports
            if not addedNewImports:
                print "Adding %s imports" % (len(newImportLines,))
                newLines.extend(newImportLines)

                addedNewImports = True

            # Rewrite NMS imports
            oldClass = line.replace("import ", "").replace(";", "");
            print oldClass
            if oldClass == "net.minecraft.server.*":
                newClass = "net.minecraft.*" # TODO
            else:
                newClass = importMap["class "+srglib.sourceName2Internal(oldClass)]
            newLine = "import %s;" % (newClass,)
            if newLine not in newImportLines:  # if not already added
                newLines.append(newLine)
        else:
            newLines.append(line)

    if not addedNewImports:
        newLines = newLines[0:2] + newImportLines + newLines[2:]

    return "\n".join(newLines)


# Check whether a unique identifier method key is a constructor, if so return full class name for remapping, else None
def getConstructor(key):
    tokens = key.split(" ", 2)  # TODO: switch to non-conflicting separator..types can have spaces :(
    if tokens[0] != "method": return None
    print tokens
    kind, fullMethodName, methodSig = tokens
    if methodSig[-1] != "V": return None # constructors marked with 'V' return type signature in ApplySrg2Source and MCP
    fullClassName = srglib.splitPackageName(fullMethodName)
    methodName = srglib.splitBaseName(fullMethodName)

    packageName = srglib.splitPackageName(fullClassName)
    className = srglib.splitBaseName(fullClassName)

    if className == methodName: # constructor has same name as class
        return fullClassName
    else:
        return None

def getNewName(key, oldName, renameMap):
    if key.startswith("localvar"):
        # Temporary hack to rename local variables without a mapping
        # This is not accurate.. variables are not always monotonic nor sequential
        # TODO: extract local variable map from MCP source with same tool, range map -> local var
        newName = "var%s" % ((int(key.split(" ")[-1]) + 1),)
    else:
        if not renameMap.has_key(key):
            constructorClassName = getConstructor(key)
            if constructorClassName is not None:
                # Constructors are not in the method map (from .srg, and can't be derived
                # exclusively from the class map since we don't know all the parameters).. so we
                # have to synthesize a rename from the class map here. Ugh..but, it works.
                print "FOUND CONSTR",key,constructorClassName
                if renameMap.has_key("class "+constructorClassName):
                    # Rename constructor to new class name
                    newName = srglib.splitBaseName(renameMap["class "+constructorClassName])
                else:
                    return None
            else:
                # Not renaming this
                return None
        else:
            newName = renameMap[key]

    return newName+"/*was:"+oldName+"*/"

# Sort range list by starting offset
# Needed since symbol range output is not always guaranteed to be in source file order
# Also runs a sanity checks, removes duplicates, verifies non-overlapping
# Modifies list in-place
def sortRangeList(rangeList, filename):
    rangeList.sort()  # sorts by keys, tuple, first element is start

    starts = {}
    prevEnd = 0
    newRangeList = []
    for start,end,expectedOldText,key in rangeList:
        if starts.has_key(start):
            # If duplicate, must be identical symbol
            otherStart, otherEnd, otherExpectedOldText, otherKey = starts[start]
            if not (otherStart == start and otherEnd == end and otherExpectedOldText == expectedOldText and otherKey == key):
                print "WARNING: Range map for %s has multiple symbols starting at [%s,%s] '%s' = %s & [%s,%s] '%s' = %s" % (
                    filename,
                    start, end, expectedOldText, key,
                    otherStart, otherEnd, otherExpectedOldText, otherKey)
            continue  # ignore duplicate 

        starts[start] = start,end,expectedOldText,key

        # sanity check
        assert start > prevEnd, "Range map invalid: overlapping symbols, failed check %s > %s: with '%s' = %s" % (start, prevEnd, expectedOldText, key)
        prevEnd = end

        assert len(expectedOldText)==end-start, "Range map invalid: expected old text '%s' length %s != %s (%s - %s)" % (
            expectedOldText, len(expectedOldText), end-start, end, start)

        newRangeList.append((start,end,expectedOldText,key))

    rangeList[:] = []
    rangeList.extend(newRangeList)

# Get the top-level class required to be declared in a file by its given name, if in the main tree
# This is an internal name, including slashes for packages components
def getTopLevelClassForFilename(filename):
    withoutExt, ext = os.path.splitext(filename)
    parts = withoutExt.split(os.path.sep)
    # expect project-relative pathname, standard Maven structure
    assert parts[0] == "src", "unexpected filename '%s', not in src" % (filename,)
    assert parts[1] in ("main", "test"), "unexpected filename '%s', not in src/{test,main}" % (filename,)
    assert parts[2] == "java", "unexpected filename '%s', not in src/{test,main}/java" % (filename,)

    return "/".join(parts[3:])  # "internal" fully-qualified class name, separated by /

# Rename symbols in source code
def processJavaSourceFile(filename, rangeList, renameMap, importMap):
    path = os.path.join(srcRoot, filename)
    data = file(path).read()

    if "\r" in data:
        # BlockJukebox is the only file with CRLF line endings in NMS.. and.. IntelliJ IDEA treats offsets 
        # as line endings being one character, whether LF or CR+LF. So remove the extraneous character or
        # offsets will be all off :.
        print "Warning: %s has CRLF line endings; consider switching to LF" % (filename,)
        data = data.replace("\r", "")

    importsToAdd = set()

    shift = 0

    # Existing package/class name (with package, internal) derived from filename
    oldTopLevelClassFullName = getTopLevelClassForFilename(filename)
    oldTopLevelClassPackage = srglib.splitPackageName(oldTopLevelClassFullName)
    oldTopLevelClassName = srglib.splitBaseName(oldTopLevelClassFullName)

    # New package/class name through mapping
    newTopLevelClassPackage = srglib.sourceName2Internal(renameMap.get("package "+oldTopLevelClassFullName))
    newTopLevelClassName = renameMap.get("class "+oldTopLevelClassFullName)
    if newTopLevelClassPackage is not None and newTopLevelClassName is None:
        assert False, "filename %s found package %s->%s but no class map for %s" % (filename, oldTopLevelClassPackage, newTopLevelClassPackage, newTopLevelClassName)
    if newTopLevelClassPackage is None and newTopLevelClassName is not None:
        assert False, "filename %s found class map %s->%s but no package map for %s" % (filename, oldTopLevelClassName, newTopLevelClassName, oldTopLevelClassPackage)

    for start,end,expectedOldText,key in rangeList:
        oldName = data[start+shift:end+shift]

        if oldName != expectedOldText:
            print "Rename sanity check failed: expected '%s' at [%s,%s] (shifted %s to [%s,%s]) in %s, but found '%s'" % (
                expectedOldText, start, end, shift, start+shift, end+shift, filename, oldName)
            print "Regenerate symbol map on latest sources or start with fresh source and try again"
            #file("/tmp/a","w").write(data)
            raise SystemExit

        newName = getNewName(key, oldName, renameMap)
        if newName is None:
            print "No rename for "+key
            continue

        print "Rename",key,[start+shift,end+shift],"::",oldName,"->",newName

        if importMap.has_key(key):
            # this rename requires adding an import
            importsToAdd.add(importMap[key])

        # Rename algorithm: 
        # 1. textually replace text at specified range with new text
        # 2. shift future ranges by difference in text length
        data = data[0:start+shift] + newName + data[end+shift:]
        shift += len(newName) - len(oldName)

    # Lastly, update imports - this is separate from symbol range manipulation above
    data = updateImports(data, importsToAdd, importMap)

    if rewriteFiles:
        print "Writing",filename
        file(path,"w").write(data)

    if renameFiles:
        if newTopLevelClassPackage is not None: # rename if package changed
            newFilename = os.path.join(srcRoot, "src/main/java/", newTopLevelClassPackage, newTopLevelClassName + ".java")
            newPath = os.path.join(srcRoot, newFilename)

            print "Rename file",filename,"->",newFilename
            srglib.rename_path(path, newPath)

def main():
    renameMap, importMap = getRenameMaps(srgFile, mcpDir)
    rangeMapByFile = readRangeMap(rangeMapFile)

    for filename in sorted(rangeMapByFile.keys()):
        processJavaSourceFile(filename, rangeMapByFile[filename], renameMap, importMap)

if __name__ == "__main__":
    main()

