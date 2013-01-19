#!/usr/bin/python

import subprocess, os

srcRoot = "../CraftBukkit"
scriptDir = "../jars"  # relative to srcRoot
startCommit = "d92dbbef5418f133f521097002c2ba9c9e145b8a"
outDir = "cbpatches/"
cbmcpBranch = "pkgmcp"

def runRemap():
    print "Starting remap script..."
    pushd = os.getcwd()
    os.chdir(scriptDir)
    run("./remap-craftbukkit.sh")
    os.chdir(pushd)
    print "Remap script finished"

def run(cmd):
    print ">",cmd
    raw_input()
    assert os.system(cmd) == 0, "Failed to run "+cmd

def runOutput(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()


def remap(commit):
    run("git checkout "+commit)


    # Get the header from the original commit
    header = runOutput(("git", "show", commit, 
        "--format=email",       # email format is for git-format-diff/git-am
        "--stat"))              # omit the actual diff (since it isn't remapped), only show stats
    print header

    # Compare against rename of previous commit
    cmd = ("git", "diff", "pkgmcp")
    diff = runOutput(cmd)
    print diff

def main():
    if os.path.basename(os.getcwd()) != os.path.basename(srcRoot): os.chdir(srcRoot)

    # Get all the latest changes
    run("git checkout master")
    run("git pull origin master")

    # Start from here, creating an initial remap on a branch for the basis of comparison
    run("git checkout "+startCommit)
    run("git branch -D "+cbmcpBranch)
    run("git checkout -b "+cbmcpBranch)
    runRemap()
    run("git commit -m 'Automated file rename'")  # separate commit for diff visibility
    run("git commit -am 'Automated symbol rename'")

    # TODO: remap commits and compare

if __name__ == "__main__":
    main()

