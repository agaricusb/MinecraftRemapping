#!/usr/bin/python

import sys, os, pprint
import srglib

rewriteFiles = True

# Get dict of unique lines (ignoring all whitespace), mapped to line number
def getUniqueLines(filename):
    seenLines = {}
    for i, originalLine in enumerate(file(filename).readlines()):
        key = srglib.killWhitespace(originalLine)
        if not seenLines.has_key(key):
            seenLines[key] = []
        seenLines[key].append((i, originalLine))

    uniqueLines = {}
    for key, seenAt in seenLines.iteritems():
        if len(seenAt) == 1:
            uniqueLines[key] = seenAt[0]

    return uniqueLines

def neutralizeWhitespace(cbFilenamePath, mcpFilenamePath, className):
    cbUniqueLines = getUniqueLines(cbFilenamePath)
    mcpUniqueLines = getUniqueLines(mcpFilenamePath)

    lineChanges = {}

    # Find whitespace-only differences in unique lines
    for key, (cbLineNo, cbOriginalLine) in cbUniqueLines.iteritems():
        if not mcpUniqueLines.has_key(key): continue

        mcpLineNo, mcpOriginalLine = mcpUniqueLines[key]

        if cbOriginalLine != mcpOriginalLine:
            # Lines are identical except for whitespace
            # For example in (casts), CB often has a byte after the closing paren, while MCP
            # doesn't.. and there's a space after array initializers { ...}. CB prefers more 
            # space. Unfortunately, astyle doesn't fix this. CB seems to be using the jacobe
            # tool for reformatting (see Bukkit-MinecraftServer GitHub project), not astyle.
            #print "CB:",cbOriginalLine
            #print "MC:",mcpOriginalLine

            # MCP is right
            lineChanges[cbLineNo] = mcpOriginalLine

    # Change those lines
    newLines = []
    count = 0
    for i, line in enumerate(file(cbFilenamePath).readlines()):
        if lineChanges.has_key(i):
            newLines.append(lineChanges[i])
            count += 1
        else:
            newLines.append(line)

    if rewriteFiles:
        file(cbFilenamePath, "w").write("".join(newLines))

    if count != 0:
        print "Neutralized %s whitespace line differences in %s" % (count, className)

def main():
    if len(sys.argv) != 3:
        print "usage: %s cbRoot mcpRoot" % (sys.argv[0],)
        raise SystemExit
    
    cbRoot = sys.argv[1]#"../CraftBukkit"
    mcpRoot = sys.argv[2]#"../mcp725-pkgd"

    cbSrc = os.path.join(cbRoot, "src/main/java/net/minecraft/")
    mcpSrc = os.path.join(mcpRoot, "src/minecraft_server/net/minecraft/")

    for cbFilenamePath in srglib.getJavaSourceFiles(cbSrc):
        # Get corresponding MCP filename path
        commonPath = cbFilenamePath.replace(os.path.commonprefix((cbFilenamePath, cbSrc)), "") 
        className = os.path.splitext(commonPath)[0]  # class name including package path
        mcpFilenamePath = os.path.join(mcpSrc, commonPath)

        assert os.path.exists(cbFilenamePath), "CB source %s not found?" % (cbFilenamePath,)
        assert os.path.exists(mcpFilenamePath), "CB source %s has no corresponding MCP file at %s" % (cbFilenamePath, mcpFilenamePath)


        neutralizeWhitespace(cbFilenamePath, mcpFilenamePath, className)

if __name__ == "__main__":
    main()

