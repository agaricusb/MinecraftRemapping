#!/usr/bin/python
import subprocess

cmd = ("git", "diff", "pkgmcp")

diff = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()
print diff
