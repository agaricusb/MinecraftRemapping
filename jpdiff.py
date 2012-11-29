#!/usr/bin/python

# diff internally-renamed Java class files

JAVAP = "javap -s -private "

import os

# Get provided map of obfuscated class names to CB names
def getClassMap():
    obf2cb = {}
    for line in file("knownclasses.txt"):
        line = line.strip()
        assert line.startswith("CL: ")
        line = line.replace("CL: ","")
        obf, cb = line.split(" ")
        obf2cb[obf] = cb

    return obf2cb

def dumpMembers(fn):
    d = {}
    f = os.popen(JAVAP + fn)
    compiledFrom = f.readline().strip()
    assert compiledFrom == "Compiled from SourceFile"

    classDecl = f.readline().strip()

    members = []
   
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

        members.append((name, sig))
        #print name,sig

    return classDecl, members

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

def diffMembers(fn1, fn2):
    class1, m1 = dumpMembers(fn1)
    class2, m2 = dumpMembers(fn2)

    print class1
    print class2

    assert len(m1) == len(m2), "Mismatched number of members"

    for a,b in zip(m1,m2):
        na, sa = a
        nb, sb = b
        print na,nb,sa,sb

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

def main():
    classes_obf2cb = getClassMap()
    classes_cb2obf = {v:k for k,v in classes_obf2cb.iteritems()}

    print classes_cb2obf

    diffMembers("vanilla/zt", "mc-dev/net/minecraft/server/ChunkSection")

if __name__ == "__main__":
    main()

