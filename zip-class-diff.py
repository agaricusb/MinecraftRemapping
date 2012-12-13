#!/usr/bin/python

# Generate class mapping difference between two identical but internally-renamed jars

import zipfile
import sys
import os

def getClassList(filename):
    return filter(lambda fn: fn.endswith(".class"), zipfile.ZipFile(filename).namelist())

def removeExt(filename):
    return os.path.splitext(filename)[0]

if len(sys.argv) != 3:
    print "Map class names from vanilla to mc-dev"
    print "Example usage: %s minecraft_server.jar minecraft-server-1.4.5.jar | sort > classes.srg" % (sys.argv[0],)
    print "vanilla: http://assets.minecraft.net/1_4_5/minecraft_server.jar"
    print "mc-dev: http://repo.bukkit.org/content/repositories/releases/org/bukkit/minecraft-server/1.4.5/minecraft-server-1.4.5.jar"
    raise SystemExit

# classes are in same order in the archives, so "zip" the list up in pairs and dump it
for a, b in zip(getClassList(sys.argv[1]), getClassList(sys.argv[2])):
    print "CL:", removeExt(a), removeExt(b)

