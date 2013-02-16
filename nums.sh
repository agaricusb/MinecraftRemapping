#!/bin/sh
# Generate obf<->num (mcp "srg" numeric names)
for mcpdir in ../mcps/*
do
    version=`basename $mcpdir`
    py chain.py $mcpdir/conf/server.srg - | sort > $version/obf2num.srg
    py reverse-srg.py < $version/obf2num.srg | sort > $version/num2obf.srg
done

