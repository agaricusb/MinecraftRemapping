#!/usr/bin/python

import sys

# Add version to package, like CB's maven-shade-plugin relocation

if len(sys.argv) < 2:
    print "usage: %s inVersion outVersion" % (sys.argv[0],)
    raise SystemExit

inVersion = sys.argv[1] # "v1_4_5"
outVersion = sys.argv[2] # "v1_4_6"

def addVersion(path, version):
    if version == "-":
        return path

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

def addSigVersion(sig, version):
    # TODO: parse more intelligently
    sig = sig.replace("net/minecraft/server/", "net/minecraft/server/" + version + "/")
    sig = sig.replace("org/bouncycastle/", "net/minecraft/" + version + "/org/bouncycastle/")
    return sig

noverMode = inVersion == "nover"   # for making unversioned 1.4.5 -> versioned (with v1_4_5 package) - ignores output

for line in sys.stdin.readlines():
    line = line.strip()
    tokens = line.split(" ")
    kind = tokens[0]
    args = tokens[1:]
    if kind == "PK:":  # package
        print line
    elif kind == "CL:": # class
        inName, outName = args
        if noverMode: 
            print kind, inName, addVersion(inName, outVersion)
        else:
            print kind, addVersion(inName, inVersion), addVersion(outName, outVersion)
    elif kind == "FD:": # field
        inName, outName = args
        if noverMode:
            print kind, inName, addVersion(inName, outVersion)
        else:
            print kind, addVersion(inName, inVersion), addVersion(outName, outVersion)
    elif kind == "MD:": # method
        inName, inSig, outName, outSig = args
        if noverMode:
            print kind, inName, inVersion, inSig, addVersion(inName, outVersion), addSigVersion(outSig, outVersion)
        else:
            print kind, addVersion(inName, inVersion), inSig, addVersion(outName, outVersion), addSigVersion(outSig, outVersion)
    else:
        print line

