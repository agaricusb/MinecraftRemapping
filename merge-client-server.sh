#!/bin/sh -x

# MCP created using instructions on https://github.com/agaricusb/CraftBukkit/wiki/How-to-decompile-Minecraft-using-MCP-with-FML-repackaged-class-names,-without-FML's-other-changes
# "with client/server joined"
MCP_JOINED=../mcp726-joined/

# Where to copy $MCP_JOINED for patching
MCP_CBJOINED=../mcp726-cbjoined/

# MCP/CB diff created using remap-craftbukkit.sh
PATCH_FILE=/tmp/diff

rm -rf $MCP_CBJOINED
cp -r $MCP_JOINED $MCP_CBJOINED

# Try to merge patch into joined client/server
patch --reject-file /tmp/rej -d $MCP_CBJOINED/mcp/src_work/minecraft --dry-run -p4 < $PATCH_FILE
# TODO: fix patch failures due to new import statements

