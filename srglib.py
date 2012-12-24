#!/usr/bin/python

# srglib: routines for manipulating MCP's .srg, .csv, and .exc files

# Not all of the tools use this library yet

import re, os, csv, sys

EXC_RE = re.compile(r"^([^.]+)\.([^(]+)(\([^=]+)=([^|]*)\|(.*)")

# Read .exc and get mapping from descriptive method names to descriptive parameter names
def readExc(excFilename, methodNum2Name, paramNum2Name):
    d = {}
    for line in file(excFilename).readlines():
        match = re.match(EXC_RE, line)
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

        # List of classes thrown as exceptions
        exceptions = exceptionsString.split(",")
        if exceptions == ['']: exceptions = []
        # not actually used

        # Parameters by number, p_XXXXX_X..
        paramNumbers = paramNumbersString.split(",")
        if paramNumbers == ['']: paramNumbers = []

        paramNames = [paramNum2Name[x] for x in paramNumbers]

        d[fullMethodName + " " + methodSig] = paramNames

    return d


# Mapping from parameter number (p_####) to name in source (par#X..)
def readDescriptiveParamNames(mcpDir):
    return readCSV(os.path.join(mcpDir, "params.csv"))

# Method nmbers (func_####) to descriptive name in source
def readDescriptiveMethodNames(mcpDir):
    methodNum2Name = readCSV(os.path.join(mcpDir, "methods.csv"))

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

# Read MCP's .srg mappings
def readSrg(filename):
    packageMap = {}
    classMap = {}
    fieldMap = {}
    methodMap = {}
    for line in file(filename).readlines():
        line = line.strip()
        kind, argsString = line.split(": ")
        args = argsString.split(" ")
        if kind == "PK":
            inName, outName = args
            packageMap[inName] = outName
        elif kind == "CL":
            inName, outName = args
            classMap[inName] = outName
        elif kind == "FD": 
            inName, outName = args
            fieldMap[inName] = outName
        elif kind == "MD": 
            inName, inSig, outName, outSig = args

            methodMap[inName + " " + outName] = (outName, outSig)
        else:
            assert "Unknown type " + kind

    return packageMap, classMap, methodMap, classMap

# Remap method signatures through a class map
def remapSig(sig, classMap):
    for k, v in classMap.iteritems():
        # yeah..
        sig = sig.replace("L" + k + ";", "L" + v + ";")

    return sig
    
