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


def main():
    if len(sys.argv) < 3:
        print "Usage: %s mcp-conf-dir exc-file.exc" % (sys.argv[0],)
        print "Examples:"
        print "\t%s ../MinecraftForge/mcp/conf packaged.exc" % (sys.argv[0],)
        print "\t%s ../MinecraftForge/mcp/conf joined.exc" % (sys.argv[0],)
        raise SystemExit

    mcpDir = sys.argv[1]
    excFilename = sys.argv[2]

    # Mapping from parameter number (p_####) to name in source (par#X..)
    paramNum2Name = readCSV(os.path.join(mcpDir, "params.csv"))

    # Method nmbers (func_####) to descriptive name in source
    methodNum2Name = readCSV(os.path.join(mcpDir, "methods.csv"))

    exc_re = re.compile(r"^([^.]+)\.([^(]+)(\([^=]+)=([^|]*)\|(.*)")

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

        # List of classes thrown as exceptions
        exceptions = exceptionsString.split(",")
        if exceptions == ['']: exceptions = []

        # Parameters by number, p_XXXXX_X..
        paramNumbers = paramNumbersString.split(",")
        if paramNumbers == ['']: paramNumbers = []

        paramNames = [paramNum2Name[x] for x in paramNumbers]

        #print [className, methodName, methodSig, exceptions, paramNames]

        print " ".join(["PA:", className + "/" + methodName, methodSig] + paramNames)

if __name__ == "__main__":
    main()

