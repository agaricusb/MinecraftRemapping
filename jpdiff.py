#!/usr/bin/python

# diff internally-renamed Java class files

JAVAP = "javap -s -private "

import os

def dumpMembers(fn):
    d = {}
    f = os.popen(JAVAP + fn)
    compiledFrom = f.readline().strip()
    assert compiledFrom == "Compiled from SourceFile"

    classDecl = f.readline().strip()
    print classDecl

    d["class"] = classDecl
    d["members"] = []
   
    while True:
        decl = f.readline()
        if decl == "": break
        decl = decl.strip()
        if decl == "}" or decl == "": continue
        assert decl[-1] == ";"
        decl = decl.replace(";","")

        sig = f.readline().strip()
        assert sig.startswith("Signature: ")
        sig = sig.replace("Signature: ", "")

        name = parseDeclName(decl)

        d["members"].append((name, sig))
        print name,sig

    return d["members"]

# Parse symbol name from declaration
def parseDeclName(decl):
    # strip arguments if a method
    if "(" in decl:
        before, args = decl.split("(")
    else:
        before = decl

    # last token
    tokens = before.split()
    name = tokens[-1]

    return name
    
a = dumpMembers("mc-dev/net/minecraft/server/ChunkSection")
b = dumpMembers("vanilla/zt")

for x,y in zip(a,b):
    print x,y

def difflines():
    a = os.popen(JAVAP + " mc-dev/net/minecraft/server/ChunkSection").readlines()
    b = os.popen(JAVAP + " vanilla/zt").readlines()

    assert len(a) == len(b), "Not equal length"

    for i in range(len(a)):
        if a[i] != b[i]:
            print "-",a[i].strip()
            print "+",b[i].strip()
        else:
            print " ",a[i].strip()
