#!/usr/bin/python

# List string literals which would be replaced to support
# reflection for a hypothetical constant pool remapper
# see https://github.com/MinecraftPortCentral/MCPC-Plus/issues/13

import srglib
import sys

if len(sys.argv) < 2:
    print "Filename required"
    raise SystemExit


def main():
    packageMap, classMap, fieldMap, methodMap, methodSigMap = srglib.readSrg(sys.argv[1])
    
    oldNames = {}

    for oldFull, newFull in fieldMap.iteritems():
        oldName = srglib.splitBaseName(oldFull)
        newName = srglib.splitBaseName(newFull)

        if oldName == newName: continue  # skip un-renamed

        #print oldName,newName,oldFull,newFull

        if not oldNames.has_key(oldName):
            oldNames[oldName] = []
        alreadyHave = False
        for otherNewName, otherOldFull, otherNewFull in oldNames[oldName]:
            if otherNewName == newName:
                # different symbol luckily maps to same obf
                # example: 2 log [[('a', 'net/minecraft/server/MinecraftServer/log', 'net/minecraft/server/MinecraftServer/a'), ('a', 'net/minecraft/server/WorldNBTStorage/log', 'ahv/a')]]
                # ignore these since they aren't collisions
                alreadyHave = True
                break
        if alreadyHave: continue

        oldNames[oldName].append((newName,oldFull,newFull))

    print
    for oldName, newNames in oldNames.iteritems():
        print len(newNames),oldName,[newNames]

    # TODO: method map

if __name__ == "__main__":
    main()

