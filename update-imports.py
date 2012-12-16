#!/usr/bin

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

def getClassUsage(data, clslist):
    foundClasses = []
    for cls in clslist:
        if re.search(r"\b" + re.escape(cls) + r"\b", data):
            foundClasses.append(cls)
    return foundClasses


cls2pkg = packagify.getPackages()

for filename in getJavaSource(srcdir):
    data = file(filename, "r").read()
    if "COPIED MCP SOURCE" in data: continue

    print filename, getClassUsage(data, cls2pkg.keys())

