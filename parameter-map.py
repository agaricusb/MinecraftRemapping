#!/usr/bin/python

# Extract parameter mappings from MCP into a "PA: " mapping for easier parsing by ApplySrg2Source

import re, os, csv, sys

MCP_CONF = "../MinecraftForge/mcp/conf"

# Read MCP's comma-separated-values files
def readCSV(path):
    d = {}
    header = True

    for row in csv.reader(file(path), delimiter=","):
        if header: 
            header = False
            continue
        d[row[0]] = row[1]

    return d

# Read name remap from srg, full old name + sig -> new name + sig
def readRemapSrg(path):
    methodMap = {}
    classMap = {}
    for row in csv.reader(file(path), delimiter=" "):
        if row[0] == "MD:":
            oldName, oldSig, newName, newSig = row[1:]
            methodMap[oldName + " " + oldSig] = (newName, newSig)
        elif row[0] == "CL:":
            oldName, newName = row[1:]
            classMap[oldName] = newName

    return methodMap, classMap
    
def main():
    if len(sys.argv) < 3:
        print "Usage: %s mcp-conf-dir exc-file.exc [method-name-remap.srg]" % (sys.argv[0],)
        print "Examples:"
        print "\t%s ../MinecraftForge/mcp/conf packaged.exc > 1.4.6/pkgmcp.methodparams" % (sys.argv[0],)
        print "\t%s ../MinecraftForge/mcp/conf packaged.exc 1.4.6/pkgmcp2cb.srg > 1.4.6/cb2mcp.methodparams" % (sys.argv[0],)
        print "\t%s ../MinecraftForge/mcp/conf joined.exc > 1.4.6/mcp.methodparams" % (sys.argv[0],)
        raise SystemExit

    mcpDir = sys.argv[1]
    excFilename = sys.argv[2]

    if len(sys.argv) > 3:
        methodNameRemap, classNameRemap = readRemapSrg(sys.argv[3])
    else:
        methodNameRemap = classNameRemap = None

    # Mapping from parameter number (p_####) to name in source (par#X..)
    paramNum2Name = readCSV(os.path.join(mcpDir, "params.csv"))

    # Method nmbers (func_####) to descriptive name in source
    methodNum2Name = readCSV(os.path.join(mcpDir, "methods.csv"))

    exc_re = re.compile(r"^([^.]+)\.([^(]+)(\([^=]+)=([^|]*)\|(.*)")
    
    ignoredClasses = set()

    for line in file(os.path.join(mcpDir, excFilename)).readlines():
        match = re.match(exc_re, line)
        className, methodNumber, methodSig, exceptionsString, paramNumbersString = match.groups()

        if methodNumber == "<init>":
            # constructor
            methodName = className.split("/")[-1]
        elif methodNum2Name.has_key(methodNumber):
            # descriptive name
            methodName = methodNum2Name[methodNumber]
        else:
            # no one named this method
            methodName = methodNumber

        fullMethodName = className + "/" + methodName

        # Second optional renaming pass, for translating MCP -> CB
        if classNameRemap is not None and methodNameRemap is not None:
            key = fullMethodName + " " + methodSig
            if methodNameRemap.has_key(key):
                fullMethodName, methodSig = methodNameRemap[key]
            else:
                if methodName == className.split("/")[-1]:
                    # Method name is class name.. this is a constructor
                    # Rename implied by CL: .srg entry instead of MD:
                    if not classNameRemap.has_key(className):
                        # No class mapping entry, probably a client-only class, included
                        # in joined mappings but we're remapping through CB, server-only
                        continue
                    newClassName = classNameRemap[className]
                    fullMethodName = newClassName + "/" + newClassName.split("/")[-1]
                else:
                    # This is probably a client-only method - ignore it, too
                    #print "COULD NOT REMAP METHOD:" + key
                    continue

        # List of classes thrown as exceptions
        exceptions = exceptionsString.split(",")
        if exceptions == ['']: exceptions = []

        # Parameters by number, p_XXXXX_X..
        paramNumbers = paramNumbersString.split(",")
        if paramNumbers == ['']: paramNumbers = []

        paramNames = [paramNum2Name[x] for x in paramNumbers]

        print " ".join(["PA:", fullMethodName, methodSig] + paramNames)

if __name__ == "__main__":
    main()
 
