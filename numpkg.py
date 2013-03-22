#!/usr/bin/python

# Repackage cb2num.srg mappings to cb2numpkg.srg, with FML's repackaging to match runtime deobf

import sys, re

import srglib

def repackage(s, packageMap):
    def getNewName(match):
        className = match.group(1)
        if not packageMap.has_key(className):
            # from a time before packaging..
            return "net/minecraft/src/"+className
        else:
            return packageMap[className] + "/" + className

    return re.sub(r"net\/minecraft\/src/(\w+)", getNewName, s)

def main():
    packageMap = srglib.readCSVMap("allpackages.csv")

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
   
