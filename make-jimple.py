#!/usr/bin/python
# Run soot on CraftBukkit

# See http://www.sable.mcgill.ca/soot/

import os, subprocess

# The CraftBukkit jar to analyze - notes:
# 1. If you get warnings about net.minecraft.sever.foo phantom classes:
# build with maven-shade-plugin 2.0 to remove the outdated symbols in the constant pool
# see https://bukkit.atlassian.net/browse/BUKKIT-3213 and https://github.com/agaricusb/CraftBukkit/tree/shade2.0
# 2. If you get an error "Exception in thread "main" soot.AbstractSootFieldRef$FieldResolutionFailedException: Class net.minecraft.server.v1_4_5.MinecraftServer doesn't have field worldServer"
# build with worldserverref fixes from https://github.com/agaricusb/CraftBukkit/tree/worldserverref
cb_jar = "../CraftBukkit/target/craftbukkit-1.4.5-R1.1-SNAPSHOT.jar"

# soot requires its own classpath, and -pp doesn't detect the standard classpath on OS X
# TODO: more complete classpath
classpath = "/Library/Java/JavaVirtualMachines/1.7.0.jdk/Contents/Home/jre/lib/rt.jar:/Library/Java/JavaVirtualMachines/1.7.0.jdk/Contents/Home/jre/lib/jce.jar"
classpath += ":".join(os.getenv("CLASSPATH", ""))

nms_classes = filter(lambda x: x.startswith("net"), [x.strip().replace("/", ".") for x in file("class-lists/classes-all-mcdev").readlines()])

for cls in nms_classes:
    relocClass = cls.replace("net.minecraft.server.", "net.minecraft.server.v1_4_5.")

    subprocess.call(("java", "-jar", "../soot/soot-2.5.0.jar", "-f", "jimple", "-d", "jimple/cb-reloc",
        "-v", "-debug",
        "-cp", classpath + ":" + cb_jar,
        "--allow-phantom-refs",  # TODO: remove after finding all symbols
        relocClass))

    # Remove the version number from the package (due to maven shade relocation), for comparison with mc-dev
    unrelocData = file("jimple/cb-reloc/" + relocClass + ".jimple").read().replace("v1_4_5.", "")
    file("jimple/cb/" + cls + ".jimple").write(unrelocData)

# TODO: mc-dev, too
