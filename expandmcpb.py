#!/usr/bin/python

import shutil, difflib, os, sys

outDir = "/tmp/out"
fmlDir = "../Srg2Source/python/fml"
mcpDir = os.path.join(fmlDir, "mcp")
vanillaSrc = os.path.join(mcpDir, "src/minecraft_server") # decompiled server with srgnames
cbPatches = "../MCPBukkit/patches"

print "Copying vanilla source"
if os.path.exists(outDir):
    shutil.rmtree(outDir)
shutil.copytree(vanillaSrc, outDir)

# TODO
#print "Applying CraftBukkit patches"
#sys.path.append(os.path.join(fmlDir, "install"))
#import fml
#print fml.apply_patches

sys.path.append(mcpDir)
import runtime.commands
pushd = os.getcwd()
os.chdir(mcpDir)
commands = runtime.commands.Commands()

commands.srcserver = outDir
print "Adding javadoc"
commands.process_javadoc(runtime.commands.SERVER)
print "Renaming srg->csv"
commands.process_rename(runtime.commands.SERVER)

os.chdir(pushd)

