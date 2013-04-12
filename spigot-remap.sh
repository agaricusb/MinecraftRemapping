#!/bin/sh -x

set -e

pushd ../CraftBukkit
git reset --hard HEAD || true
git checkout master
git branch -D spigot || true
git fetch spigot
git checkout spigot/master -b spigot
perl -i.bak -pe's(<parent)(<!--$&); s(</parent>)($&-->);' pom.xml
popd

pushd ../Srg2Source/python
python remap-craftbukkit.py --cb-dir=../../CraftBukkit --fml-dir=fml --out-dir /tmp/out --skip-output-archive --skip-finish-cleanup --skip-compile
popd

python expandmcpb.py Spigot

