#!/usr/bin/python

# Textually rename 

import sys, os, re, subprocess

def filenameRenames(renames, srcdir):
    pushd = os.getcwd()
    os.chdir(srcdir)  # have to be in root for git 
    os.mkdir("main/java/net/minecraft/src/")
    for before, after in renames.iteritems():
        # Change package too
        # TODO: fix org bouncycastle renames, have to do manually
        beforePath = os.path.join("main/java/net/minecraft/server/", before) + ".java"
        afterPath = os.path.join("main/java/net/minecraft/src/", after) + ".java"

        cmd = ("git", "mv", beforePath, afterPath)
        print " ".join(cmd)
        subprocess.call(cmd)
    os.chdir(pushd)


# Rename classes in files, by text
def textualRename(renames, filenames):
    for filename in filenames:
        print filename
        data = file(filename, "r").read()

        for before, after in renames.iteritems():
            data = re.sub(r"\b" + re.escape(before) + r"\b", after, data)

        file(filename, "w").write(data)

def getJavaSource(srcdir):
    paths = []
    for root, dirs, files in os.walk(srcdir):
        for fn in files:
            if not fn.endswith(".java"): continue

            path = os.path.join(root, fn)
            paths.append(path)
    return paths


# Get class renames map
def getRenames(filename):
    renames = {}
    f = file(filename)
    ren = []
    for line in f.readlines():
        line = line.strip()
        tokens = line.strip().split()
        if tokens[0] != "CL:": continue
        args = tokens[1:]

        inFullName, outFullName = args

        inName = lastComponent(inFullName)
        outName = lastComponent(outFullName)

        renames[inName] = outName

    renames["net.minecraft.server"] = "net.minecraft.src"  #  package name

    return renames


def lastComponent(fullName):
    return fullName.split("/")[-1]

def main():
    if len(sys.argv) != 3:
        print "Usage: %s cb2mcp-only-classes.srg ../CraftBukkit/src/" % (sys.argv[0],)
        raise SystemExit

    renames = getRenames(sys.argv[1])
    filenames = getJavaSource(sys.argv[2])

    print "Renaming class references..."
    textualRename(renames, filenames)
    print "Commit to git now, then press enter once committed to continue"
    raw_input()
    print "Renaming files"
    filenameRenames(renames, sys.argv[2])
    print "Rename complete! Commit to git, then fix any errors (org.bukkit.Potion vs net.minecraft.src.Potion, etc.)"
    print "Note, you must now use git-log --follow to view history of any of the renames files"

if __name__ == "__main__":
    main()

