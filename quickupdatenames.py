#!/usr/bin/python

# Quick textual rename for updating newly-added csvnames
# Similar to MCP updatenames script
# Only for *new* csvnames (previously srgnamed) - for *changed*
# csvnames use srg2source or another symbolic rename refactoring tool

import sys, os, re

import srglib

mcpConfDir = "../FML/mcp/conf/"
targetDir = "../15mcpc-plus/src"

methodNames = srglib.readDescriptiveMethodNames(mcpConfDir)
fieldNames = srglib.readDescriptiveFieldNames(mcpConfDir)

print methodNames, fieldNames

FUNC_PATTERN = re.compile(r"(func_\d+_\w+)")
FIELD_PATTERN = re.compile(r"(field_\d+_\w+)")

for root, dirs, files in os.walk(targetDir):
    for fn in files:
        path = os.path.join(root, fn)
        if not path.endswith(".java"): continue

        print path
        data = file(path).read()

        def renameMethod(match):
            name = match.group(0)
            return methodNames.get(name, name)

        def renameField(match):
            name = match.group(0)
            return fieldNames.get(name, name)

        data = re.sub(FUNC_PATTERN, renameMethod, data)
        data = re.sub(FIELD_PATTERN, renameField, data)

        file(path, "w").write(data)

