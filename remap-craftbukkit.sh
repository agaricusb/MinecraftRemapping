#!/bin/sh -x

# Root of checked out CraftBukkit repository
CB_ROOT=../CraftBukkit

# MCP decompiled with FML repackaging, but not joined. See https://gist.github.com/4366333
MCP_ROOT=../mcp725-pkgd

# CB/MCP patch output
DIFF_OUT=/tmp/diff

# Python 2.7+ installation 
PYTHON=/usr/bin/python2.7

# Abort on any command failure
set -e

# TODO: extract CB range map with Srg2Source, on slim
# TODO: and MCP

CB_RANGEMAP=1.4.6/cb2577.rangemap
MCP_RANGEMAP=1.4.6/pkgmcp.rangemap

SRG_CB2MCP=1.4.6/cb2pkgmcp.srg
SRG_CB2MCP_FIXES=1.4.6/uncollide-cb2pkgmcp.srg

# TODO: apply prerenamefixes, minecraft-server-pkgmcp

# Apply the renames
$PYTHON rangeapply.py --srcRoot $CB_ROOT --cbRangeMap $CB_RANGEMAP --mcpRangeMap $MCP_RANGEMAP --mcpConfDir $MCP_ROOT/conf --srgFiles $SRG_CB2MCP $SRG_CB2MCP_FIXES

# TODO: apply javadoc

# Reformat source style in NMS (only; not OBC) to more closely resemble MCP
# This assumes you have astyle installed and ~/.astylerc copied from conf/astyle.cfg
find $CB_ROOT/src/main/java/net/minecraft -name '*.java' -exec astyle --suffix=none {} \;

$PYTHON javadocxfer.py $CB_ROOT $MCP_ROOT

$PYTHON whitespaceneutralizer.py $CB_ROOT $MCP_ROOT

# Measure differences to get a sense of progress
(diff -ur $MCP_ROOT/src/minecraft_server/net/minecraft/ $CB_ROOT/src/main/java/net/minecraft/ > $DIFF_OUT) || true

wc -l $DIFF_OUT


