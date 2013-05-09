#!/usr/bin/python

# Remap an inheritance map through a mapping

import srglib

import pprint
import sys

srg = srglib.readSrg("1.5.1/pkgmcp2obf.srg")
classMap = srg[1]

for line in sys.stdin.readlines():
    line = line.replace("\n", "")
    clss = line.split(" ")
    outs = []

    for cls in clss:
        outs.append(classMap[cls])

    print " ".join(outs)

