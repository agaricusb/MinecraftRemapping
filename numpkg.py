#!/usr/bin/python

# Repackage cb2num.srg mappings to cb2numpkg.srg, with FML's repackaging to match runtime deobf

import sys, re

import srglib

def repackage(s, packageMap):
    for name, new in packageMap.iteritems():
        s = s.replace("net/minecraft/src/"+name, new+"/"+name)  # inefficient, yeah
    return s

def main():
    packageMap = srglib.readClassPackageMap("../MinecraftForge/fml/conf")

    for line in sys.stdin.readlines():
        line = line.strip()
        tokens = line.split(" ")
        kind = tokens[0]
        args = tokens[1:]
        if kind == "PK:":  # package
            print line
        elif kind == "CL:": # class
            inName, outName = args
            print kind, inName, repackage(outName, packageMap)
        elif kind == "FD:": # field
            inName, outName = args
            print kind, inName, repackage(outName, packageMap)
        elif kind == "MD:": # method
            inName, inSig, outName, outSig = args
            print kind, inName, inSig, repackage(outName, packageMap), repackage(outSig, packageMap)
        else:
            print line

if __name__ == "__main__":
    main()
   
