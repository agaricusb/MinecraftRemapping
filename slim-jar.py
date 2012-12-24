#!/usr/bin/python

# Generate minecraft-server.jar (internally-renamed server jar)
# without any of the NMS classes included in the CB project

# This can help avoid PSI errors
# To use: 
# 1. edit CraftBukkit/pom.xml , change:
#      <artifactId>minecraft-server</artifactId>
#  to:
#      <artifactId>slim-minecraft-server</artifactId>
# 2. run:
# mvn install:install-file -Dfile=../slim-minecraft-server-1.4.6.jar -DgroupId=org.bukkit -DartifactId=slim-minecraft-server -Dversion=1.4.6 -Dpackaging=jar
# Project should build as normal

import zipfile, os, sys

srcDir = "../CraftBukkit/src/main/java/net/minecraft/server"
inFile = "../minecraft-server-1.4.6.jar"
outFile = "../slim-minecraft-server-slim-1.4.6.jar"

skipFiles = ["net/minecraft/server/" + x.replace(".java", ".class") for x in os.listdir(srcDir)]
z = zipfile.ZipFile(inFile)
z2 = zipfile.ZipFile(outFile, "w")
for zi in z.infolist():
    if zi.filename not in skipFiles:
        z2.writestr(zi, z.read(zi.filename))

z2.close()

