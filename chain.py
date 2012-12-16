#!/usr/bin/python

# Given obf<->MCP and obf<->CB mappings, generate MCP<->CB mappings

import sys, os

global verbose

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
        tokens = line.split(",",3)
        if tokens[0] == "searge": continue
        searge,name,side,desc = tokens
        if side != "1": continue # 1=server-side, mappings don't always match 0=client-side
        d[searge] = name
    return d

def chain(mcpdir, cbsrg):
    if mcpdir.endswith(".srg"):
        # only chain srgs
        mcpsrg = mcpdir
        fields_fn = methods_fn = None
    elif mcpdir.endswith("/"):
        # also translate descriptive names through MCP's fields/methods.csv
        mcpsrg = mcpdir + "server.srg"  # old MCP
        if not os.path.exists(mcpsrg):
            mcpsrg = mcpdir + "packaged.srg"    # Forge uses multi-level packages (not joined.srg)
        if not os.path.exists(mcpsrg):
            print "no .srg found in %s" % (mcpdir,)
            raise SystemExit

        fields_fn = mcpdir + "fields.csv"
        methods_fn = mcpdir + "methods.csv"
    else:
        print "argument must be srg or mcp dir with .srg, fields.csv, and methods.csv"
        raise SystemExit

    mcp = process(mcpsrg)
    cb = process(cbsrg)

    # Map MCP indexed names to descriptive names
    if fields_fn and methods_fn:
        descriptiveFieldNames = loadDescriptiveNamesCSV(fields_fn)
        descriptiveMethodNames = loadDescriptiveNamesCSV(methods_fn)
    else:
        descriptiveFieldNames = descriptiveMethodNames = {}

    def descriptiveName(mcpIndexedNameSig):
        # methods are name, space, signature
        if " " in mcpIndexedNameSig:
            mcpIndexedName, sig = mcpIndexedNameSig.split(" ")
            sig = " " + sig
        else:
            mcpIndexedName = mcpIndexedNameSig
            sig = ""

        # translate name, preserving package
        tokens = mcpIndexedName.split("/")
        firstName = tokens[:-1]
        lastName = tokens[-1]
        if lastName.startswith("field_"):
            newName = descriptiveFieldNames.get(lastName, lastName)
        elif lastName.startswith("func_"):
            newName = descriptiveMethodNames.get(lastName, lastName)
        else:
            newName = lastName

        return "/".join(firstName + [newName]) + sig

    for kind in ("CL", "FD", "MD"):
        mapMCP = mcp[kind]
        mapCB = cb[kind]

        missing = set(mapMCP.keys()) - set(mapCB.keys())
        if len(missing) != 0 and verbose:
            print "CB mappings missing from MCP mappings: %s" % (missing,)
            import pprint
            print "=== mapMCP ==="
            pprint.pprint(mapMCP)
            print "=== mapCB ==="
            pprint.pprint(mapCB)
            print "== missing ==="
            pprint.pprint(missing)

        surplus = set(mapCB.keys()) - set(mapMCP.keys())
        if len(surplus) != 0:
           #print "CB mappings has extra mappings not in MCP: %s" % (surplus,) # no problem, probably just constructors (no rename)
           pass

        for obf in sorted(mapMCP.keys()):
            if not mapCB.has_key(obf) or not mapMCP.has_key(obf): continue

            print "%s: %s %s" % (kind, mapCB[obf], descriptiveName(mapMCP[obf]))

def main():
    global verbose

    verbose = False

    if len(sys.argv) < 3:
        print "chain srg given obf<->MCP and obf<->CB to CB<->MCP"
        print "Usage: %s clean-mcpdir/conf cb-server.srg [-v]" % (sys.argv[0],)
        print "Examples:"
        print "Translate through .srg and descriptive fields.csv/methods.csv:"
        print "\t%s ../mcp723-clean/conf/ obf2cb.srg > cb2mcp.srg" % (sys.argv[0],)
        print "Translate only through .srg, leaving indexed func_XXX/field_XXX names:"
        print "\t%s ../mcp723-clean/conf/server.srg obf2cb.srg" % (sys.argv[0],)
        raise SystemExit

    mcpdir = sys.argv[1]
    cbsrg = sys.argv[2]

    verbose = "-v" in sys.argv

    chain(mcpdir, cbsrg)

if __name__ == "__main__":
    main()
