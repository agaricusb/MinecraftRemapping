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

# Load fields/methods.csv mapping "searge" name (func_XXX/field_XXX) to descriptive MCP name
def loadDescriptiveNamesCSV(fn):
    f = file(fn)
    d = {}
    for line in f.readlines():
        tokens = line.split(",")
        if tokens[0] == "searge": continue
        searge,name,side,desc = tokens
        d[searge] = name
    return d

def loadDescriptiveNames(ffn, mfn):
    d = loadDescriptiveNamesCSV(ffn)
    d.extend(loadDescriptiveNamesCSV(mfn))
    return d
    
def chain(mcpdir, cbsrg):

    mcpsrg = mcpdir + "server.srg"
    mcp = process(mcpsrg)
    cb = process(cbsrg)

    for kind in ("CL", "FD", "MD"):
        mapMCP = mcp[kind]
        mapCB = cb[kind]

        missing = set(mapMCP.keys()) - set(mapCB.keys())
        if len(missing) != 0:
            print "CB mappings missing fields from MCP mappings: %s" % (missing,)

        surplus = set(mapCB.keys()) - set(mapMCP.keys())
        if len(surplus) != 0:
            #print "CB mappings has extra mappings not in MCP: %s" % (surplus,) # no problem, probably just constructors (no rename)
            pass

        for obf in sorted(mapMCP.keys()):
            print "%s: %s %s" % (kind, mapCB[obf], mapMCP[obf])

if len(sys.argv) != 3:
    print "chain srg given obf<->MCP and obf<->CB to CB<->MCP"
    print "Usage: %s clean-mcpdir cb-server.srg" % (sys.argv[0],)
    print "Example: %s ../mcp723-clean/conf/ server.srg" % (sys.argv[0],)
    raise SystemExit

mcpdir = sys.argv[1]
cbsrg = sys.argv[2]

chain(mcpdir, cbsrg)

