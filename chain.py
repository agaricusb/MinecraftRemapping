#!/usr/bin/python

# Given obf<->MCP and obf<->CB mappings, generate MCP<->CB mappings

import sys

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

    return {"CL": classes_o2d, "FD": fields_o2d, "MD": methods_o2d}

def compare(filenameA, filenameB):
    allA = process(filenameA)
    allB = process(filenameB)

    for kind in ("CL", "FD", "MD"):
        mapA = allA[kind]
        mapB = allB[kind]

        missing = set(mapA.keys()) - set(mapB.keys())
        if len(missing) != 0:
            print "Second mappings missing fields from first mappings: %s" % (missing,)

        surplus = set(mapB.keys()) - set(mapA.keys())
        if len(surplus) != 0:
            #print "Second mappings has extra mappings not in first: %s" % (surplus,) # no problem, probably just constructors (no rename)
            pass

        #assert len(mapA) == len(mapB), "non-one-to-one map: %s != %s, +%s, -%s" % (len(mapA), len(mapB), set(mapA.keys()) - set(mapB.keys()), set(mapB.keys()) - set(mapA.keys()))

        for obf in sorted(mapA.keys()):
            print "%s: %s %s" % (kind, mapB[obf], mapA[obf])

if len(sys.argv) != 3:
    print "chain srg given obf<->MCP and obf<->CB to CB<->MCP"
    print "Usage: %s ../mcp723-clean/conf/server.srg bukkit/conf/server.srg" % (sys.argv[0],)
    raise SystemExit

compare(sys.argv[1], sys.argv[2])

