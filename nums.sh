#!/bin/sh
# Generate obf<->num (mcp "srg" numeric names)
for mcpdir in ../mcps/*
do
    version=`basename $mcpdir`
    py chain.py $mcpdir/conf/server.srg - | sort > $version/obf2num.srg
    py reverse-srg.py < $version/obf2num.srg | sort > $version/num2obf.srg
done

# chain across versions to show hit rate
for mcpdir in ../mcps/*
do
    version=`basename $mcpdir`
    echo $version
    py chain.py $version/num2obf.srg 1.4.7/num2obf.srg|wc -l
done

