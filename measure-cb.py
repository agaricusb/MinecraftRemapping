#!/usr/bin/python
# Measure how many lines are surrounded by "// CraftBukkit"

import os

def getClasses():
    return [x.strip() for x in file("class-lists/classes-patched-both-mcp").readlines()]

def getFilenames():
    return ["../CraftBukkit/src/main/java/" + c + ".java" for c in getClasses()]

def measure(fn):
    inside = False
    x = 0 
    for line in file(fn).readlines():
        if "// CraftBukkit start" in line:
            inside = True
        elif "// CraftBukkit end" in line:
            inside = False
        elif "// CraftBukkit" in line:
            x += 1

        if inside:
            x += 1

    return x

for fn in getFilenames():
    print measure(fn), os.path.splitext(os.path.basename(fn))[0]

