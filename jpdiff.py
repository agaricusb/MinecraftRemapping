#!/usr/bin/python

# javap-based diff of internally-renamed Java class files into a .srg

# Note: you probably want to use https://github.com/md-5/SpecialSource instead

# Requires:
#  classes.srg - from zip-class-diff.py
#  vanilla/ - extracted minecraft_server.jar
#  mc-dev/ - extracted minecraft-server-*.jar

# Example Usage:
# 0. Update classes.srg with comprehensive obfuscated->CB class map - see zip-class-diff.py
# 1. Extract minecraft_server.jar from Mojang into "vanilla"
# http://assets.minecraft.net/1_4_5/minecraft.jar 
# 2. Extract Bukkit's "mc-dev" minecraft-server into "mc-dev"
# http://repo.bukkit.org/content/repositories/releases/org/bukkit/minecraft-server/1.4.5/minecraft-server-1.4.5.jar
# 3. Run this script and save output to "obf2cb.srg"
# (To make cb2obf.srg, run ReverseSrg from SrgTools)

# TODO: use ASM instead of javap parsing
JAVAP = ["javap", "-s", "-private"]

import os
import subprocess
import sys

def debug(s):
    #print s
    pass

# Get provided map of obfuscated class names to CB names
def getClassMap(filename):
    obf2cb = {}
    i = 0
    for line in file(filename):
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
    cmd = JAVAP + [fn]
    debug("$ %s" % (" ".join(cmd),))
    f = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    while True:
        line = f.readline()
        assert len(line) != 0, "couldn't find class declaration in javap output for %s: %s" % (cmd, line)
        if "class" in line or "interface" in line:
            classDecl = line.strip()
            break
            
    members = []
   
    while True:
        decl = f.readline()
        if decl == "": break
        decl = decl.strip()
        debug(">"+decl)
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

def diffMembers(obfClass, cbClass, vanillaDir, mcdevDir):
    obfClassDecl, obfMembers = dumpMembers(os.path.join(vanillaDir, obfClass))
    cbClassDecl, cbMembers = dumpMembers(os.path.join(mcdevDir, cbClass))

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

def printPackage():
    print """PK: . net/minecraft/server
PK: net net
PK: net/minecraft net/minecraft
PK: net/minecraft/server net/minecraft/server"""

def main():
    if len(sys.argv) != 4:
        print "Usage: %s classes.srg vanilla/ mc-dev/" % (sys.argv[0],)
        raise SystemExit

    classesSrgFilename = sys.argv[1]
    vanillaDir = sys.argv[2]
    mcdevDir = sys.argv[3]

    printPackage()

    classes_obf2cb = getClassMap(classesSrgFilename)
    printClasses(classes_obf2cb)

    for obf in sorted(classes_obf2cb.keys()):
        cb = classes_obf2cb[obf]
        debug(" ".join(("***",obf,cb)))
        diffMembers(obf,cb,vanillaDir,mcdevDir)

if __name__ == "__main__":
    main()

