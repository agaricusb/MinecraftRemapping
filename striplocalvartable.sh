#!/bin/sh
cp -r mcp-craftbukkit-1.4.5-R0.2 mcp-stripped-craftbukkit-1.4.5-R0.2
find mcp-stripped-craftbukkit-1.4.5-R0.2 -name '*.class' -exec perl -pe's/LocalVariableTable/XocalVariableTable/g' -i {} \;
