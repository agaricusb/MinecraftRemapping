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

    for oldFull, newFull in fieldMap.iteritems():
        oldName = srglib.splitBaseName(oldFull)
        newName = srglib.splitBaseName(newFull)

        if oldName == newName: continue  # skip un-renamed

        print oldName,newName,oldFull,newFull

    # TODO: method map

if __name__ == "__main__":
    main()

