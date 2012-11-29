#!/usr/bin/python

# diff internally-renamed Java class files

JAVAP = "javap -s -private "

import os

def disasm(fn):
    f = os.popen(JAVAP + fn)
    compiledFrom = f.readline().strip()
    assert compiledFrom == "Compiled from SourceFile"

    classDecl = f.readline().strip()
    print classDecl
   
    while True:
        name = f.readline()
        if name == "": break
        name = name.strip()
        if name == "}" or name == "": continue
        assert name[-1] == ";"
        name = name.replace(";","")


        sig = f.readline().strip()
        assert sig.startswith("Signature: ")
        sig = sig.replace("Signature: ", "")

        print name,sig

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
