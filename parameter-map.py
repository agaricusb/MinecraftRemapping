#!/usr/bin/python

import re, os

MCP_CONF = "../MinecraftForge/mcp/conf"

# Get mapping from parameter number (p_####) to name in source (par#X..)
def getParamNames():
    paramNum2Name = {}
    filename = os.path.join(MCP_CONF, "params.csv")

    for line in file(filename):
        tokens = line.split(",")
        if tokens[0] == "param": continue

        number, name, side = tokens

        paramNum2Name[number] = name

    return paramNum2Name

def readExc():
    paramNum2Name = getParamNames()

    exc_re = re.compile(r"^([^.]+)\.([^(]+)(\([^=]+)=([^|]*)\|(.*)")

    excFilename = os.path.join(MCP_CONF, "packaged.exc")
    for line in file(excFilename).readlines():
        match = re.match(exc_re, line)
        className, methodNumber, methodSig, exceptionsString, paramNumbersString = match.groups()

        # List of classes thrown as exceptions
        exceptions = exceptionsString.split(",")
        if exceptions == ['']: exceptions = []

        # Parameters by number, p_XXXXX_X..
        paramNumbers = paramNumbersString.split(",")
        if paramNumbers == ['']: paramNumbers = []

        paramNames = [paramNum2Name[x] for x in paramNumbers]

        print [className, methodNumber, methodSig, exceptions, paramNames]

def main():
    readExc()

if __name__ == "__main__":
    main()

