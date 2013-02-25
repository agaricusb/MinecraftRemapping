#!/usr/bin/python
# Create MCP patches between releases of Forge from git history

import subprocess, os

srcRoot = "../MinecraftForge"
outDir = "../jars/upstream-patches/forge" # relative to srcRoot
startCommit = "feca047114562c2ec2ec6be42e3ffd7c09a9a94d" # build 528, Update FML to 556..
#startCommit = "6673844c54b8de0ebe4cba601b6505ec0e3dda3f" # build 524, Fix ServerBrand retriever..
#startCommit = "0f3bd780e17baf3fcccc8f594337556e2368fe35" # build 518, Merge branch 'master' into TESRculling.. 2013-02-29
#startCommit = "fb87773c3ab77522a27651dcf20066277bb5e88d" # Added input getters for..
#startCommit = "f06e0be5e59723808305f4c4aeb89c9108c79230" # We try and log a message.. - last commit of Forge 516
#startCommit = "f20ea649c6fbf4e49ccb857e6ea9d3333cf6d6a9" # Attempt to fix a possible NPE in the...
#startCommit = "3a9c7b4532240b70dac5f72082cbcedc0dd41335" # build 497, released 2013-01-01
patchBranch = "mcppatch"
masterBranch = "master"

shouldPullLatestChanges = True
shouldCheckoutMaster = True
shouldBuildInitial = True
shouldBuildPatches = True
shouldRewritePaths = True

def build():
    print "Starting build..."
    print "Rerun setup first?"
    if True or raw_input().startswith("y"):
        print "Rerunning setup..."  # TODO: automatic, if commit changes FML.. or always?
        run("py setup.py") # installs MCP, decompiles
        print "Continue?"
        #raw_input()

    run("py release.py")  # patches MCP source
    # TODO: pass --force to mcp cleanup to avoid confirmation prompt
    print "Complete"

def run(cmd):
    print ">",cmd
    #raw_input()
    status = os.system(cmd)
    assert status == 0, "Failed to run %s: status %s" % (cmd, status)

def runOutput(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()


def buildMCPPatch(commit):
    # Get the header from the original commit
    header = runOutput(("git", "show", commit, 
        "--format=email",       # email format is for git-format-diff/git-am
        "--stat"))              # omit the actual diff (since it isn't remapped), only show stats
    print header

    run("git add -f mcp/src")  # the meat
    # Compare against rename of previous commit
    cmd = ("git", "diff", patchBranch)
    diff = runOutput(cmd)

    #print "Waiting"
    #raw_input()

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
        assert not (message.startswith("Automated") and message.endswith("build")), "Unclean starting point - already has automated commits! Reset and retry."
        commits.append((commit, message))
    commits.reverse()
    return commits

def saveBranch():
    # Save our remapped changes to the branch for comparison reference
    try:
        run("git branch -D "+patchBranch)
    except:
        pass
    run("git checkout -b "+patchBranch)
    run("git add -f mcp/src")  # the meat
    run("git commit mcp/src -m 'Automated build'")

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

    if shouldBuildInitial:
        # Start from here, creating an initial remap on a branch for the basis of comparison
        run("git checkout "+startCommit)
        build()
        saveBranch()


    if shouldBuildPatches:
        # Build Forge, generating patches from MCP source per commit
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
            # TODO: remove extraneous files (patches of patches)..but requires more
            # intelligent diff parsing :(

            file(path, "w").write("".join(lines))

if __name__ == "__main__":
    main()

