#!/usr/bin/python

import os, pprint
import srglib

cbRoot = "../CraftBukkit"
mcpRoot = "../mcp725-pkgd"

"""Read javadoc into a dict keyed by line after the javadoc (without whitespace), to array of raw javadoc lines"""
def readJavadoc(mcpFilenamePath):
    readingJavadoc = False
    readingIdentifyingLine = False
    javadocLines = []
    javadoc = {}
    for mcpLine in file(mcpFilenamePath).readlines():
        if readingIdentifyingLine:
            # The line after the javadoc is what it refers to
            identifier = killWhitespace(mcpLine)
            assert len(identifier) != 0, "Nothing associated with javadoc '%s' in %s" % (javadocLines, mcpFilenamePath)
            assert not javadoc.has_key(identifier), "Duplicate javadoc for '%s' in %s: %s" % (identifier, mcpFilenamePath, javadocLines)
            javadoc[identifier] = javadocLines
            javadocLines = []
            readingIdentifyingLine = False
        if "/**" in mcpLine:
            readingJavadoc = True
        if readingJavadoc:
            # javadoc is enclosed in /** ... */
            javadocLines.append(mcpLine)
            if "*/" in mcpLine:
                print "Read javadoc: ",javadocLines
                readingJavadoc = False
                readingIdentifyingLine = True 

    assert not readingJavadoc, "Failed to find end of javadoc %s in %s" % (javadocLines, mcpFilenamePath)
    assert not readingIdentifyingLine, "Failed to find javadoc identifier for %s in %s" % (javadocLines, mcpFilenamePath)

    return javadoc

def process(cbFilenamePath, mcpFilenamePath, className):
    print ">>>",className

    javadoc = readJavadoc(mcpFilenamePath)
    pprint.pprint(javadoc)


"""Get a string with _all_ whitespace removed."""
def killWhitespace(s):
    return "".join(s.split())

def main():
    cbSrc = os.path.join(cbRoot, "src/main/java/net/minecraft/")
    mcpSrc = os.path.join(mcpRoot, "src/minecraft_server/net/minecraft/")

    for cbFilenamePath in srglib.getJavaSourceFiles(cbSrc):
        # Get corresponding MCP filename path
        commonPath = cbFilenamePath.replace(os.path.commonprefix((cbFilenamePath, cbSrc)), "") 
        className = os.path.splitext(commonPath)[0]  # class name including package path
        mcpFilenamePath = os.path.join(mcpSrc, commonPath)

        assert os.path.exists(cbFilenamePath), "CB source %s not found?" % (cbFilenamePath,)
        assert os.path.exists(mcpFilenamePath), "CB source %s has no corresponding MCP file at %s" % (cbFilenamePath, mcpFilenamePath)


        process(cbFilenamePath, mcpFilenamePath, className)

if __name__ == "__main__":
    main()

