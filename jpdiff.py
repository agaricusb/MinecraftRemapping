#!/usr/bin/python

# diff internally-renamed Java class files

JAVAP = "javap -s -private -c"
import os

a = os.popen(JAVAP + " mc-dev/net/minecraft/server/ChunkSection").readlines()
b = os.popen(JAVAP + " vanilla/zt").readlines()

assert len(a) == len(b), "Not equal length"

for i in range(len(a)):
    if a[i] != b[i]:
        print "-",a[i].strip()
        print "+",b[i].strip()
    else:
        print " ",a[i].strip()
