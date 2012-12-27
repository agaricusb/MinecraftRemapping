#!/usr/bin

# Add missing imports to NMS after MCP package class rename

# XXX: This is obsolete - used in the older 1.4.5 rename. 1.4.6+ in rangeapply.py

import os, re

import packagify

srcdir = "../CraftBukkit/src/main/java/net/minecraft"

def getJavaSource(srcdir):
    paths = []
    for root, dirs, files in os.walk(srcdir):
        for fn in files:
            if not fn.endswith(".java"): continue

            path = os.path.join(root, fn)
            paths.append(path)
        for d in dirs:
            paths.extend(getJavaSource(os.path.join(root, d)))
        return paths

# Get (heurstically estimated) classes referenced by another class
def getClassUsage(data, clslist):
    foundClasses = []
    for cls in clslist:
        if re.search(r"\b" + re.escape(cls) + r"\b", data):
            foundClasses.append(cls)
    return foundClasses

def addImports(data, newImports):
    lines = data.split("\n")
    lastNativeImport = None
    existingImports = []
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
        importsToAdd.append(imp)

    splice = lines[0:insertionPoint] + importsToAdd + lines[insertionPoint:]
    return "\n".join(splice)

def getThisPackage(data):
    match = re.match(r"package ([^;]+);", data)
    if not match:
        print data
        print "!!! Unable to parse package in file" 
        raise SystemExit
    return match.group(1)

cls2pkg = packagify.getPackages()

for filename in getJavaSource(srcdir):
    data = file(filename, "r").read()
    if "COPIED MCP SOURCE" in data: continue

    usedClasses = getClassUsage(data, cls2pkg.keys())
    thisPackage = getThisPackage(data)
    newImports = []
    for cls in usedClasses: 
        pkg = cls2pkg[cls].replace("/",".")
        if pkg == thisPackage: continue # unnecessary import
        newImports.append("import %s.%s;" % (pkg, cls))
   
    newImports.sort()

    print filename
    #print "BEFORE"
    #print data
    data = addImports(data, newImports)
    #print "AFTER"
    #print data
    print len(newImports)

    file(filename, "w").write(data)

