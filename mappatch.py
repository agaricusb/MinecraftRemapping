#!/usr/bin/python
# Remap patches from git history

# For updating MCPC+ to latest upstream CB

import subprocess, os

srcRoot = "../CraftBukkit"
scriptDir = "../jars"  # relative to srcRoot
outDir = "../jars/cbpatches/" # relative to srcRoot
startCommit = "d92dbbef5418f133f521097002c2ba9c9e145b8a"
cbmcpBranch = "pkgmcp"

shouldPullLatestChanges = False
shouldCheckoutMaster = False#True
shouldRemapInitial = False#True
shouldRemapPatches = False#True
shouldRewritePaths = True#False

def runRemap():
    print "Starting remap script..."
    pushd = os.getcwd()
    os.chdir(scriptDir)
    run("./remap-craftbukkit.sh")
    os.chdir(pushd)
    print "Remap script finished"

def run(cmd):
    print ">",cmd
    #raw_input()
    assert os.system(cmd) == 0, "Failed to run "+cmd

def runOutput(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()


def buildRemappedPatch(commit):
    # Get the header from the original commit
    header = runOutput(("git", "show", commit, 
        "--format=email",       # email format is for git-format-diff/git-am
        "--stat"))              # omit the actual diff (since it isn't remapped), only show stats
    print header

    # Compare against rename of previous commit
    cmd = ("git", "diff", "pkgmcp")
    diff = runOutput(cmd)

    return header + "\n" + diff

def clean():
    # Clean out even non-repository or moved files
    run("rm -rf src")
    run("git reset --hard HEAD")

def readCommitLog():
    # Get commit IDs and messages after the starting commit, in reverse chronological order
    commits = []
    for line in runOutput(("git", "log", "--format=oneline")).split("\n"):
        assert len(line) != 0, "Reached end of commit log without finding starting commit "+startCommit
        commit, message = line.split(" ", 1)
        if commit == startCommit: break
        print commit, message
        assert not (message.startswith("Automated") and message.endswith("rename")), "Unclean starting point - already has automated commits! Reset and retry."
        commits.append((commit, message))
    commits.reverse()
    return commits

def saveBranch():
    # Save our remapped changes to the branch for comparison reference
    run("git branch -D "+cbmcpBranch)
    run("git checkout -b "+cbmcpBranch)
    run("git commit -m 'Automated file rename'")  # separate commit for diff visibility
    run("git commit -am 'Automated symbol rename'")

def main():
    if os.path.basename(os.getcwd()) != os.path.basename(srcRoot): os.chdir(srcRoot)

    if shouldCheckoutMaster:
        clean()
        run("git checkout master")

    if shouldPullLatestChanges:
        # Get all the latest changes 
        run("git pull origin master")

    if shouldCheckoutMaster:
        run("git checkout master")

    commits = readCommitLog()

    if shouldRemapInitial:
        # Start from here, creating an initial remap on a branch for the basis of comparison
        run("git checkout "+startCommit)
        runRemap()
        saveBranch()

    if shouldRemapPatches:
        # Remap commits, translating patches
        n = 0
        for commitInfo in commits:
            commit, message = commitInfo
            n += 1
            filename = "%s/%.4d-%s-%s" % (outDir, n, commit, message.replace(" ", "_"))
            print "\n\n*** %s %s" % (commit, message)
            clean()
            run("git checkout "+commit)
            runRemap()
            
            patch = buildRemappedPatch(commit)
            file(filename, "w").write(patch)

            # Save for comparison to next commit
            saveBranch()

    if shouldRewritePaths:
        for filename in sorted(os.listdir(outDir)):
            if filename[0] == ".": continue
            print filename
            path = os.path.join(outDir, filename)
            lines = file(path).readlines()
            # Clean up patch, removing stat output
            # TODO: find out how to stop git show from outputting it in the first place
            statLine = None
            for i, line in enumerate(lines):
                if "files changed, " in line:
                    statLine = i
                    break
            if statLine is None:
                print "Skipping",path  # probably already processed
                continue
            i = statLine - 1
            while True:
                assert i > 0, "Could not find patch description in %s" % (path,)
                if len(lines[i].strip()) == 0: break  # blank line separator
                i -= 1
            lines = lines[:i] + lines[statLine + 1:]

            # Fix paths, CBMCP to MCPC+
            for i, line in enumerate(lines):
                lines[i] = line.replace("src/main/java", "src/minecraft")

            file(path, "w").write("".join(lines))

if __name__ == "__main__":
    main()

