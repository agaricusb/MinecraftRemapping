#!/usr/bin/python

import sys

# Add version to package, like CB's maven-shade-plugin relocation

inVersion = "v1_4_5"
outVersion = "v1_4_6"

def addVersion(path, version):
    components = path.split("/")

    if path.startswith("net/minecraft/server/"):
        #                <relocation>
        #                    <pattern>net.minecraft.server</pattern>
        #                    <shadedPattern>net.minecraft.server.v${minecraft_version}</shadedPattern>
        #                </relocation>
        #
        components = components[:-1] + [version, components[-1]]
    elif path.startswith("org/bouncycastle/"):
        #                <relocation>
        #                  <pattern>org.bouncycastle</pattern>
        #                  <shadedPattern>net.minecraft.v${minecraft_version}.org.bouncycastle</shadedPattern>
        #                </relocation>
        components = ["net", "minecraft", version] + components

    return "/".join(components)

for line in sys.stdin.readlines():
    line = line.strip()
    tokens = line.split(" ")
    kind = tokens[0]
    args = tokens[1:]
    if kind == "PK:":  # package
        print line
    elif kind == "CL:": # class
        inName, outName = args
        print kind, addVersion(inName, inVersion), addVersion(outName, outVersion)
    elif kind == "FD:": # field
        inName, outName = args
        print kind, addVersion(inName, inVersion), addVersion(outName, outVersion)
    elif kind == "MD:": # method
        inName, inSig, outName, outSig = args
        print kind, addVersion(inName, inVersion), inSig, addVersion(outName, outVersion), outSig
    else:
        print line

