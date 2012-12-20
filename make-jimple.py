#!/usr/bin/python
# Run soot on CraftBukkit

# See http://www.sable.mcgill.ca/soot/

import os, subprocess

def runSoot(outdir, jar, cls):
    subprocess.call(("java", "-jar", "../soot/soot-2.5.0.jar", "-f", "jimple", "-d", outdir,
        "-v", "-debug",
        "-cp", classpath + ":" + jar,
        "--allow-phantom-refs",  # TODO: remove after finding all symbols
        cls))

# The CraftBukkit jar to analyze - notes:
# 1. If you get warnings about net.minecraft.sever.foo phantom classes:
# build with maven-shade-plugin 2.0 to remove the outdated symbols in the constant pool
# see https://bukkit.atlassian.net/browse/BUKKIT-3213 and https://github.com/agaricusb/CraftBukkit/tree/shade2.0
# 2. If you get an error "Exception in thread "main" soot.AbstractSootFieldRef$FieldResolutionFailedException: Class net.minecraft.server.v1_4_5.MinecraftServer doesn't have field worldServer"
# build with worldserverref fixes from https://github.com/agaricusb/CraftBukkit/tree/worldserverref
cb_jar = "../CraftBukkit/target/craftbukkit-1.4.5-R1.1-SNAPSHOT.jar"

# Internally-renamed "mc-dev" Minecraft server jar from
# http://repo.bukkit.org/content/groups/public/org/bukkit/minecraft-server/1.4.5/minecraft-server-1.4.5.jar
# This is based on the vanilla minecraft_server.jar but partially deobfuscated to mc-dev mappings
mcdev_jar = "../jars/minecraft-server-1.4.5.jar"

# soot requires its own classpath, and -pp doesn't detect the standard classpath on OS X
# TODO: more complete classpath
classpath = "/Library/Java/JavaVirtualMachines/1.7.0.jdk/Contents/Home/jre/lib/rt.jar:/Library/Java/JavaVirtualMachines/1.7.0.jdk/Contents/Home/jre/lib/jce.jar"
classpath += ":".join(os.getenv("CLASSPATH", ""))

nms_classes = filter(lambda x: x.startswith("net"), [x.strip().replace("/", ".") for x in file("class-lists/classes-all-mcdev").readlines()])

for cls in nms_classes:
    # CraftBukkit
    relocClass = cls.replace("net.minecraft.server.", "net.minecraft.server.v1_4_5.")

    runSoot("jimple/cb-reloc", cb_jar, relocClass)

    # Remove the version number from the package (due to maven shade relocation), for comparison with mc-dev
    unrelocData = file("jimple/cb-reloc/" + relocClass + ".jimple").read().replace("v1_4_5.", "").replace("v1_4_5/", "")
    file("jimple/cb/" + cls + ".jimple", "w").write(unrelocData)

    # mc-dev
    runSoot("jimple/mcdev", mcdev_jar, cls)
