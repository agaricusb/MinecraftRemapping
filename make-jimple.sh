#!/bin/sh -x
# Run soot on CraftBukkit
# Notes:
# 1. If you get warnings about net.minecraft.sever.foo phantom classes:
# build with maven-shade-plugin 2.0 to remove the outdated symbols in the constant pool
# see https://bukkit.atlassian.net/browse/BUKKIT-3213 and https://github.com/agaricusb/CraftBukkit/tree/shade2.0
# 2. If you get an error "Exception in thread "main" soot.AbstractSootFieldRef$FieldResolutionFailedException: Class net.minecraft.server.v1_4_5.MinecraftServer doesn't have field worldServer"
# build with worldserverref fixes from https://github.com/agaricusb/CraftBukkit/tree/worldserverref
CB_JAR=../CraftBukkit/target/craftbukkit-1.4.5-R1.1-SNAPSHOT.jar
export CLASSPATH=/Library/Java/JavaVirtualMachines/1.7.0.jdk/Contents/Home/jre/lib/rt.jar:/Library/Java/JavaVirtualMachines/1.7.0.jdk/Contents/Home/jre/lib/jce.jar
java -jar ../soot/soot-2.5.0.jar -f jimple -d cb2544+s2 \
    -v -debug \
    -cp $CLASSPATH:$CB_JAR \
    --allow-phantom-refs -process-dir $CB_JAR
# TODO: investigate Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: -32768 at soot.coffi.cp_info.getTypeDescr(cp_info.java:239) - https://gist.github.com/4343179
