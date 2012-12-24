#!/usr/bin/python

# srglib: routines for manipulating MCP's .srg, .csv, and .exc files

# Not all of the tools use this library yet

import re, os, csv, sys

EXC_RE = re.compile(r"^([^.]+)\.([^(]+)(\([^=]+)=([^|]*)\|(.*)")


# Get map from full descriptive method name + signature -> list of descriptive parameter names
def readParameterMap(mcpConfDir):
    excFilename = os.path.join(mcpConfDir, "packaged.exc")  # TODO: what about joined.exc?
    methodNum2Name = readDescriptiveMethodNames(mcpConfDir)
    paramNum2Name = readDescriptiveParameterNames(mcpConfDir)

    paramMap = {}

    rows = readExc(excFilename)
    for row in rows:
        className, methodNumber, methodSig, exceptions, paramNumbers = row
         
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

        # Parameters by number, p_XXXXX_X.. to par1. descriptions
        paramNames = [paramNum2Name[x] for x in paramNumbers]

        paramMap[fullMethodName + " " + methodSig] = paramNames

    return paramMap

# Read .exc file, returning list of tuples per line,
# tuples of class name, method number, signature, list of exceptions through, and list of parameter numbers
def readExc(filename):
    exc = []
    for line in file(filename).readlines():
        match = re.match(EXC_RE, line)
        className, methodNumber, methodSig, exceptionsString, paramNumbersString = match.groups()

        # List of classes thrown as exceptions
        exceptions = exceptionsString.split(",")
        if exceptions == ['']: exceptions = []

        # Parameters by number, p_XXXXX_X..
        paramNumbers = paramNumbersString.split(",")
        if paramNumbers == ['']: paramNumbers = []

        exc.append((className, methodNumber, methodSig, exceptions, paramNumbers))

    return exc




# Mapping from parameter number (p_####) to name in source (par#X..)
def readDescriptiveParameterNames(mcpConfDir):
    return readCSV(os.path.join(mcpConfDir, "params.csv"))

# Method nmbers (func_####) to descriptive name in source
def readDescriptiveMethodNames(mcpConfDir):
    return readCSV(os.path.join(mcpConfDir, "methods.csv"))

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
    
