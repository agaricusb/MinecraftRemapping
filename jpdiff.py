#!/usr/bin/python

# diff internally-renamed Java class files into a .srg

# Example Usage:
# 0. Update classes.srg with comprehensive obfuscated->CB class map
# 1. Extract minecraft_server.jar from Mojang into "vanilla"
# http://assets.minecraft.net/1_4_5/minecraft.jar 
# 2. Extract Bukkit's "mc-dev" minecraft-server into "mc-dev"
# http://repo.bukkit.org/content/repositories/releases/org/bukkit/minecraft-server/1.4.5/minecraft-server-1.4.5.jar
# 3. Run this script and save output to "obf2cb.srg"
# (To make cb2obf.srg, run ReverseSrg from SrgTools)

JAVAP = ["javap", "-s", "-private"]

import os
import subprocess

def debug(s):
    pass

# Get provided map of obfuscated class names to CB names
def getClassMap():
    obf2cb = {}
    i = 0
    for line in file("classes.srg"):
        i += 1
        line = line.strip()
        assert line.startswith("CL: ")
        line = line.replace("CL: ","")
        obf, cb = line.split(" ")

        obf2cb[obf] = cb

    return obf2cb

def printClasses(obf2cb):
    for obf in sorted(obf2cb.keys()):
        print "CL: %s %s" % (obf, obf2cb[obf])

def dumpMembers(fn):
    d = {}
    f = subprocess.Popen(JAVAP + [fn], stdout=subprocess.PIPE).stdout
    compiledFrom = f.readline().strip()
    if compiledFrom == "Compiled from SourceFile":
        classDecl = f.readline().strip()
    else:
        classDecl = compiledFrom  # bouncycastle

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

def diffMembers(obfClass, cbClass):
    obfClassDecl, obfMembers = dumpMembers("vanilla/"+obfClass)
    cbClassDecl, cbMembers = dumpMembers("mc-dev/"+cbClass)

    debug(obfClassDecl)
    debug(cbClassDecl)

    # This means either the wrong class, or missing class
    assert len(obfMembers) == len(cbMembers), "Mismatched number of members: %d != %d, %s != %s" % (len(obfMembers), len(cbMembers), obfMembers, cbMembers)

    for a,b in zip(obfMembers,cbMembers):
        obfName, obfSig = a
        cbName, cbSig = b
        debug("\t".join((obfClass, obfName,obfSig, cbName,cbSig)))

        if obfName == "{}": continue  # skip static initializer bodies

        if "(" in obfSig:  # method
            #if cbName == cbClass: continue # skip constructors
            #if obfName == obfClass: continue # skip constructors
            print "MD: %s/%s %s %s/%s %s" % (obfClass, obfName, obfSig, cbClass, cbName, cbSig)
        else:  # field
            print "FD: %s/%s %s/%s" % (obfClass, obfName, cbClass, cbName)

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

def printPackage():
    print """PK: . net/minecraft/server
PK: net net
PK: net/minecraft net/minecraft
PK: net/minecraft/server net/minecraft/server"""

def main():
    printPackage()

    classes_obf2cb = getClassMap()
    printClasses(classes_obf2cb)

    for obf in sorted(classes_obf2cb.keys()):
        cb = classes_obf2cb[obf]
        debug(" ".join(("***",obf,cb)))
        diffMembers(obf,cb)

if __name__ == "__main__":
    main()

