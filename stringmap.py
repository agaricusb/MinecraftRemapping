#!/usr/bin/python

# List string literals which would be replaced to support
# reflection for a hypothetical constant pool remapper
# see https://github.com/MinecraftPortCentral/MCPC-Plus/issues/13

import srglib
import sys

if len(sys.argv) < 2:
    print "Filename required"
    raise SystemExit

def uniq(xs):
    return [list(x) for x in set(tuple(x) for x in xs)]

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
        oldNames[oldName].append((newName,oldFull,newFull))

    print
    for oldName, newNames in oldNames.iteritems():
        obfNames = uniq([x for x,y,z in newNames])
        print len(obfNames),oldName,[newNames]

    # TODO: method map

if __name__ == "__main__":
    main()

