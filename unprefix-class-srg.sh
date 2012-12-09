#!/bin/sh
# Generate srg with classes removing cbtmp_ temporary prefix added by prefix-srg.py
# This is for applying after mcp2cb-only-classes-prefixed.srg to get the final class names

cat mcp2cb-only-classes-prefixed.srg|awk '{print $3}'|perl -pe'chomp;@a=split m(/);$_=$a[-1];($n=$_)=~s/cbtmp_//g;$_="CL: net/minecraft/src/$_ net/minecraft/src/$n\n"'

