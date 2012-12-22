#!/usr/bin/python

import re, os, csv

MCP_CONF = "../MinecraftForge/mcp/conf"

# Read MCP's comma-separated-values files
def readCSV(filename):
    path = os.path.join(MCP_CONF, filename)
    d = {}
    header = True

    for row in csv.reader(file(path), delimiter=","):
        if header: 
            header = False
            continue
        d[row[0]] = row[1]

    return d


def readExc():
    # Mapping from parameter number (p_####) to name in source (par#X..)
    paramNum2Name = readCSV("params.csv")

    # Method nmbers (func_####) to descriptive name in source
    methodNum2Name = readCSV("methods.csv")

    exc_re = re.compile(r"^([^.]+)\.([^(]+)(\([^=]+)=([^|]*)\|(.*)")

    excFilename = os.path.join(MCP_CONF, "packaged.exc")
    for line in file(excFilename).readlines():
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

        print [className, methodName, methodSig, exceptions, paramNames]

def main():
    readExc()

if __name__ == "__main__":
    main()

