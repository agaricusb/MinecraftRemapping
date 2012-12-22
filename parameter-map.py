#!/usr/bin/python

import re

excFilename = "../MinecraftForge/mcp/conf/packaged.exc"

EXC_RE = re.compile(r"^([^.]+)\.([^(]+)(\([^=]+)=([^|]*)\|(.*)")

for line in file(excFilename).readlines():
    if len(line) == 0: break

    match = re.match(EXC_RE, line)
    className, methodNumber, methodSig, exceptionsString, paramNumbersString = match.groups()

    # List of classes thrown as exceptions
    exceptions = exceptionsString.split(",")
    if exceptions == ['']: exceptions = []

    # Parameters by number, p_XXXXX_X..
    paramNumbers = paramNumbersString.split(",")
    if paramNumbers == ['']: paramNumbers = []

    print [className, methodNumber, methodSig, exceptions, paramNumbers]

