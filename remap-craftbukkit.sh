#!/bin/sh -x

# Root of checked out CraftBukkit repository
CB_ROOT=../CraftBukkit

# MCP decompiled with FML repackaging, but not joined. See https://gist.github.com/4366333
MCP_PKGD_ROOT=../mcp725-pkgd

DIFF_OUT=/tmp/diff

# TODO: extract CB range map with Srg2Source, on slim
# TODO: and MCP

# TODO: apply prerenamefixes, minecraft-server-pkgmcp

# TODO: parameters
python rangeapply.py

# TODO: apply javadoc

# Reformat source style in NMS (only; not OBC) to more closely resemble MCP
# This assumes you have astyle installed and ~/.astylerc copied from conf/astyle.cfg
find $CB_ROOT/src/main/java/net/minecraft -name '*.java' -exec astyle --suffix=none {} \;

# Measure differences to get a sense of progress
diff -ur $MCP_PKGD_ROOT/src/minecraft_server/net/minecraft/ $CB_ROOT/src/main/java/net/minecraft/ > $DIFF_OUT

wc -l $DIFF_OUT


