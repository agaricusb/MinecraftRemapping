#!/bin/sh -x

# original obfuscated jar from Mojang
# http://assets.minecraft.net/1_4_5/minecraft.jar
VANILLA=minecraft_server-146.jar
VANILLA_DIR=vanilla146

# internally renamed jar from Bukkit
# http://repo.bukkit.org/content/repositories/releases/org/bukkit/minecraft-server/1.4.5/minecraft-server-1.4.5.jar
MCDEV=minecraft-server-1.4.6.jar
MCDEV_DIR=mcdev146

# MCP deobfuscation mappings from Ocean Labs
MCPCONF=../mcp725-clean/conf/

# Location to store generated mappings (must already exist)
OUT_DIR=1.4.6/

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
python chain.py $MCPCONF $OUT_DIR/obf2cb.srg > $OUT_DIR/cb2mcp.srg


# Reversed
python reverse-srg.py $OUT_DIR/obf2cb.srg > $OUT_DIR/cb2obf.srg
python reverse-srg.py $OUT_DIR/cb2mcp.srg > $OUT_DIR/mcp2cb.srg

# obf <-> MCP - this is like what MCP ships, except with merged descriptive symbol names
python chain.py $OUT_DIR/cb2mcp.srg $OUT_DIR/cb2obf.srg > $OUT_DIR/obf2mcp.srg
python reverse-srg.py $OUT_DIR/obf2mcp.srg > $OUT_DIR/mcp2obf.srg

# Split by type for easier processing
grep FD: $OUT_DIR/cb2mcp.srg > $OUT_DIR/cb2mcp-only-fields.srg
grep MD: $OUT_DIR/cb2mcp.srg > $OUT_DIR/cb2mcp-only-methods.srg
grep CL: $OUT_DIR/cb2mcp.srg > $OUT_DIR/cb2mcp-only-classes.srg
grep FD: $OUT_DIR/mcp2cb.srg > $OUT_DIR/mcp2cb-only-fields.srg
grep MD: $OUT_DIR/mcp2cb.srg > $OUT_DIR/mcp2cb-only-methods.srg
grep CL: $OUT_DIR/mcp2cb.srg > $OUT_DIR/mcp2cb-only-classes.srg

# Temporary prefixes for atomic remapping
python prefix-srg.py $OUT_DIR/cb2mcp-only-methods.srg cbtmp_ > $OUT_DIR/cb2mcp-only-methods-prefixed.srg
python prefix-srg.py $OUT_DIR/cb2mcp-only-fields.srg cbtmp_ > $OUT_DIR/cb2mcp-only-fields-prefixed.srg
python prefix-srg.py $OUT_DIR/cb2mcp-only-classes.srg cbtmp_ > $OUT_DIR/cb2mcp-only-classes-prefixed.srg
python prefix-srg.py $OUT_DIR/mcp2cb-only-methods.srg cbtmp_ > $OUT_DIR/mcp2cb-only-methods-prefixed.srg
python prefix-srg.py $OUT_DIR/mcp2cb-only-fields.srg cbtmp_ > $OUT_DIR/mcp2cb-only-fields-prefixed.srg
python prefix-srg.py $OUT_DIR/mcp2cb-only-classes.srg cbtmp_ > $OUT_DIR/mcp2cb-only-classes-prefixed.srg


