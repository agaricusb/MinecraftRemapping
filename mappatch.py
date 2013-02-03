#!/usr/bin/python
# Remap patches from git history

# For updating MCPC+ to latest upstream CB

import subprocess, os

srcRoot = "../CraftBukkit"
scriptDir = "../Srg2Source/python"  # relative to srcRoot
outDir = "../jars/upstream-patches/craftbukkit" # relative to srcRoot
startCommit = "eea7fc2067d7d7fc08c72414b662d0a065495264" # Remove erroneous break.. before update to 1.4.7-R1.0
#startCommit = "6b4ae3cdc7da8c8a886c0d2e1e57363cfd151f46" # Spigot - Add Custom Timings to various points
#startCommit = "eea7fc2067d7d7fc08c72414b662d0a065495264" # before spigot - Remove erroneous break statement in scheduler. Fixes BUKKIT-3395
#startCommit = "deda98a3b2562660ce2e359e099deb5f59fe7f80" # Update Fireballs to account for ExplosionPower
#startCommit = "ed63bd525b36780e57d1576842e3d45f4bf5d55d" # Refactor processBlockPlace logic
#startCommit = "a05357ee65e95d2eadb6e2f6036c0c6f25243702" # commit in Spigot before filename too long - shade 2.0
#startCommit = "ed63bd525b36780e57d1576842e3d45f4bf5d55d" # commit before Spigot #425, Refactor processBlockPlace logic. Fixes BUKKIT-3406 and BUKKIT-3454
#startCommit = "4e8a841fa9b368b55d2b60511a8c0655eb52e29e" # 2nd commit in 1.4.7-R.02, Place beds with the correct data. Fixes BUKKIT-3447
#startCommit = "0104a4078da87d65abbe7f94aa58c5e136dfdab8" # last commit of 1.4.6 before 1.4.7
#startCommit = "d92dbbef5418f133f521097002c2ba9c9e145b8a"  # first dev build of 1.4.6-R0.4 - initial MCPC+ fork
cbmcpBranch = "pkgmcp"
masterBranch = "master"

shouldPullLatestChanges = True
shouldCheckoutMaster = True
shouldRemapInitial = True
shouldRemapPatches = True
shouldRewritePaths = True

def runRemap():
    print "Starting remap script..."
    pushd = os.getcwd()
    os.chdir(scriptDir)
    run("./remap-craftbukkit.py")
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
    cmd = ("git", "diff", cbmcpBranch)
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
        run("git checkout "+masterBranch)

    if shouldPullLatestChanges:
        # Get all the latest changes 
        run("git pull origin "+masterBranch)

    if shouldCheckoutMaster:
        run("git checkout "+masterBranch)

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
            safeMessage = "".join(x if x.isalnum() else "_" for x in message)
            filename = "%s/%.4d-%s-%s" % (outDir, n, commit, safeMessage)
            filename = filename[0:200]
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
            if not os.path.isfile(path): continue
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

