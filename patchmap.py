#!/usr/bin/python
import subprocess

cmd = ("git", "format-patch", "pkgmcp", "--stdout", "-N")

f = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
while True:
    line = f.readline()
    if len(line) == 0: break
    # Stop reading at automated rename patch
    # TODO: find out how to specify 'only diff the last commit'.. even though git-format-patch
    # has a -1 flag, it generates a diff for the automated rename instead... and revision ranges
    # like pkgmcp^! pkgmcp similarly do not output only the changes we're interested in.
    # So instead, cut out the excess ourselves
    if line.startswith("From 2b58f7320d0b0e45d94ee86a0accf4947cfe1bb1"): break
    print line,

