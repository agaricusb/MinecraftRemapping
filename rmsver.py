#!/usr/bin/python

# Temporary hack to remove incorrectly versioned net/minecraft/server/MinecraftServer
# from vcb2obf mappings (as it isn't reobfuscated in vanilla, but it is shaded in CB)

import sys

def transform(symbol):
    symbol = symbol.replace("v1_4_6/MinecraftServer", "MinecraftServer")
    symbol = symbol.replace("v1_4_R1/MinecraftServer", "MinecraftServer")
    return symbol

for line in sys.stdin.readlines():
    line = line.strip()
    tokens = line.split(" ")
    kind = tokens[0]
    args = tokens[1:]
    if kind == "PK:":  # package
        print line
    elif kind == "CL:": # class
        inName, outName = args
        print kind, inName, transform(outName)
    elif kind == "FD:": # field
        inName, outName = args
        print kind, inName, transform(outName)
    elif kind == "MD:": # method
        inName, inSig, outName, outSig = args
        print kind, inName, inSig, transform(outName), transform(outSig)
    else:
        print line

