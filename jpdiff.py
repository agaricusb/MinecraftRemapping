#!/usr/bin/python

# diff internally-renamed Java class files

JAVAP = "javap -s -private -c "

import os

def disasm(fn):
    f = os.popen(JAVAP + fn)
    compiledFrom = f.readline().strip()
    assert compiledFrom == "Compiled from SourceFile"

    classDecl = f.readline().strip()
    print classDecl
   
    while True:
        memberDecl = f.readline()
        if memberDecl == "": break
        memberDecl = memberDecl.strip()
        assert memberDecl[-1] == ";"
        memberDecl = memberDecl.replace(";","")

        print memberDecl

        sig = f.readline().strip()
        assert sig.startswith("Signature: ")
        sig = sig.replace("Signature: ", "")
        print sig

        line = f.readline().strip()
        if line == "": continue
        print line
        assert line == "Code:"

        while True:
            codeLine = f.readline().strip()
            if codeLine == "": break
            print codeLine
        print "---"

disasm("mc-dev/net/minecraft/server/ChunkSection")

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
