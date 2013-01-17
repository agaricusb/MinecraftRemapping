#!/bin/sh -x

# original obfuscated jar from Mojang
# http://assets.minecraft.net/1_4_7/minecraft_server.jar
VANILLA=minecraft_server-147.jar
VANILLA_DIR=vanilla147

# internally renamed jar from Bukkit
# http://repo.bukkit.org/content/repositories/releases/org/bukkit/minecraft-server/1.4.5/minecraft-server-1.4.5.jar
MCDEV=minecraft-server-1.4.7.jar
MCDEV_DIR=mcdev147

# MCP deobfuscation mappings from Ocean Labs
MCPCONF=../mcp726-clean/conf/

# Repackaged FML/MCP - created as described on 
# https://github.com/agaricusb/CraftBukkit/wiki/How-to-decompile-Minecraft-using-MCP-with-FML-repackaged-class-names,-without-FML's-other-changes
PKGMCPCONF=../mcp726-pkgd/conf/

# Location to store generated mappings (must already exist)
OUT_DIR=1.4.7/

set -e

# obfuscated -> CB

# Class mappings (CL:)
python zip-class-diff.py $VANILLA $MCDEV | sort > $OUT_DIR/classes.srg

# Method and field (MD: and FD:)
rm -rf $VANILLA_DIR/
rm -rf $MCDEV_DIR/
unzip $VANILLA -d $VANILLA_DIR/
unzip $MCDEV -d $MCDEV_DIR/
python -u jpdiff.py $OUT_DIR/classes.srg $VANILLA_DIR $MCDEV_DIR | tee $OUT_DIR/obf2cb.srg

# CB -> MCP
python chain.py $MCPCONF $OUT_DIR/obf2cb.srg | sort > $OUT_DIR/cb2mcp.srg
python chain.py $PKGMCPCONF $OUT_DIR/obf2cb.srg | sort > $OUT_DIR/cb2pkgmcp.srg


# Reversed
python reverse-srg.py $OUT_DIR/obf2cb.srg | sort > $OUT_DIR/cb2obf.srg
python reverse-srg.py $OUT_DIR/cb2mcp.srg | sort > $OUT_DIR/mcp2cb.srg
python reverse-srg.py $OUT_DIR/cb2pkgmcp.srg | sort > $OUT_DIR/pkgmcp2cb.srg

# obf <-> MCP - this is like what MCP ships, except with merged descriptive symbol names
python chain.py $OUT_DIR/cb2mcp.srg $OUT_DIR/cb2obf.srg | sort > $OUT_DIR/obf2mcp.srg # TODO: include client
# special case chaining to '-' extracts complete obfuscated->mcp names without remapping
python chain.py $PKGMCPCONF - | sort > $OUT_DIR/obf2pkgmcp.srg
python reverse-srg.py $OUT_DIR/obf2mcp.srg | sort > $OUT_DIR/mcp2obf.srg
python reverse-srg.py $OUT_DIR/obf2pkgmcp.srg | cat > $OUT_DIR/pkgmcp2obf.srg # TODO: sort

