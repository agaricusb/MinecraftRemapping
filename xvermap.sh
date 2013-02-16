#!/bin/sh
# Chain mappings across Minecraft versions

# Uses MCP's numeric names ("srg") as reference point
# Shows hit rate for each version to latest

for mcpdir in ../mcps/*
do
    version=`basename $mcpdir`
    ver=`echo $version | tr -d '.'`
    xver=$version/obf$ver-to-obf147.srg
    py chain.py 1.4.7/num2obf.srg $version/num2obf.srg | sort > $xver
    hits=`wc -l < $xver`
    echo $version = $hits

    #py chain $version/
done

