#!/bin/sh -x

# original obfuscated jar from Mojang
# http://assets.minecraft.net/1_4_5/minecraft.jar
VANILLA=minecraft_server.jar

# internally renamed jar from Bukkit
# http://repo.bukkit.org/content/repositories/releases/org/bukkit/minecraft-server/1.4.5/minecraft-server-1.4.5.jar
MCDEV=minecraft-server-1.4.5.jar

# MCP deobfuscation mappings from Ocean Labs
MCPCONF=../mcp723-clean/conf/


# obfuscated -> CB

# Class mappings (CL:)
python zip-class-diff.py $VANILLA $MCDEV | sort > classes.srg

# Method and field (MD: and FD:)
rm -rf vanilla/
rm -rf mc-dev/
unzip $VANILLA -d vanilla/
unzip $MCDEV -d mc-dev/
python -u jpdiff.py | tee obf2cb.srg

# CB -> MCP
python chain.py $MCPCONF obf2cb.srg > cb2mcp.srg

# Reversed
python reverse-srg.py obf2cb.srg > cb2obf.srg
python reverse-srg.py cb2mcp.srg > mcp2cb.srg

# Split by type for easier processing
grep FD: cb2mcp.srg > cb2mcp-only-fields.srg
grep MD: cb2mcp.srg > cb2mcp-only-methods.srg
grep CL: cb2mcp.srg > cb2mcp-only-classes.srg
grep FD: mcp2cb.srg > mcp2cb-only-fields.srg
grep MD: mcp2cb.srg > mcp2cb-only-methods.srg
grep CL: mcp2cb.srg > mcp2cb-only-classes.srg

# Temporary prefixes for atomic remapping
python prefix-srg.py cb2mcp-only-methods.srg cbtmp_ > cb2mcp-only-methods-prefixed.srg
python prefix-srg.py cb2mcp-only-fields.srg cbtmp_ > cb2mcp-only-fields-prefixed.srg
python prefix-srg.py cb2mcp-only-classes.srg cbtmp_ > cb2mcp-only-classes-prefixed.srg
python prefix-srg.py mcp2cb-only-methods.srg cbtmp_ > mcp2cb-only-methods-prefixed.srg
python prefix-srg.py mcp2cb-only-fields.srg cbtmp_ > mcp2cb-only-fields-prefixed.srg
python prefix-srg.py mcp2cb-only-classes.srg cbtmp_ > mcp2cb-only-classes-prefixed.srg

