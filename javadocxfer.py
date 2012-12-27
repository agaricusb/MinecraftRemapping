#!/usr/bin/python

import os
import srglib

cbRoot = "../CraftBukkit"
mcpRoot = "../mcp725-pkgd"

def process(cbFilenamePath, mcpFilenamePath, className):
    print className
    # TODO

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

