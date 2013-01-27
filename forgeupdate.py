#!/usr/bin/python
# Create MCP patches between releases of Forge from git history

import subprocess, os

srcRoot = "../MinecraftForge"
outDir = "../jars/forgepatches" # relative to srcRoot
startCommit = "3a9c7b4532240b70dac5f72082cbcedc0dd41335" # build 497, released 2013-01-01
patchBranch = "mcppatch"
masterBranch = "master"

shouldPullLatestChanges = True
shouldCheckoutMaster = True
shouldRemapPatches = False
shouldRewritePaths = True

def build():
    print "Starting build..."
    run("py setup.py")
    run("py release.py")  # patches MCP source
    print "Complete"

def run(cmd):
    print ">",cmd
    raw_input()
    assert os.system(cmd) == 0, "Failed to run "+cmd

def runOutput(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()


def buildMCPPatch(commit):
    # Get the header from the original commit
    header = runOutput(("git", "show", commit, 
        "--format=email",       # email format is for git-format-diff/git-am
        "--stat"))              # omit the actual diff (since it isn't remapped), only show stats
    print header

    # Compare against rename of previous commit
    cmd = ("git", "diff", patchBranch)
    diff = runOutput(cmd)

    return header + "\n" + diff

def clean():
    # Clean out even non-repository or moved files
    pass
    # TODO: needed?

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
    run("git branch -D "+patchBranch)
    run("git checkout -b "+patchBranch)
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
            build()
            
            patch = buildMCPPatch(commit)
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

            # Fix paths, Forge to MCPC+
            for i, line in enumerate(lines):
                lines[i] = line.replace("mcp/src/minecraft", "src/minecraft")

            file(path, "w").write("".join(lines))

if __name__ == "__main__":
    main()

