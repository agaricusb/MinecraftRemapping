#!/usr/bin/python

# Generate "extras" file, showing MCP<->CB mappings, without obfuscated mappings

def process(filename):
    f = file(filename)
    classes_o2d = {}; classes_d2o = {}
    fields_o2d = {}; fields_d2o = {}
    methods_o2d = {}; methods_d2o = {}
    for line in f.readlines():
        line = line.strip()
        kind, argsString = line.split(": ")
        args = argsString.split(" ")
        if kind == "PK":  # package
            continue 
        elif kind == "CL": # class
            obfName, deobName = args
            classes_o2d[obfName] = deobName
            classes_d2o[deobName] = obfName
        elif kind == "FD": # field
            obfName, deobName = args
            fields_o2d[obfName] = deobName
            fields_d2o[deobName] = obfName
        elif kind == "MD": # method
            obfName, obfSig, deobName, deobSig = args

            obfKey = obfName + " " + obfSig
            deobKey = deobName + " " + deobSig
            methods_o2d[obfKey] = deobKey
            methods_d2o[deobKey] = obfKey
        else:
            assert "Unknown type " + kind

    return {"CLASS": classes_o2d, "FIELD": fields_o2d, "METHOD": methods_o2d}

def compare(filenameA, filenameB):
    allA = process(filenameA)
    allB = process(filenameB)

    for kind in ("CLASS", "FIELD", "METHOD"):
        mapA = allA[kind]
        mapB = allB[kind]

        assert len(mapA) == len(mapB), "incomplete maps"

        for obf in sorted(mapA.keys()):

            mapA[obf] = mapA[obf].replace("net/minecraft/src", "net/minecraft/server")  # CraftBukkit mappings, package

            print "\t".join((kind,mapA[obf],mapB[obf]))

compare("../mcp719-bukkitmappings/conf/server.srg", "../mcp719-clean/conf/server.srg")
