#!/usr/bin/python

# Process symbol range maps produced by ApplySrg2Source

rangeMap = "/tmp/nms3"
for line in file(rangeMap).readlines():
    tokens = line.strip().split(",")
    if tokens[0] != "@": continue
    filename, startRangeStr, endRangeStr, kind = tokens[1:5]
    info = tokens[5:]
    startRange = int(startRangeStr.replace("(",""))
    endRange = int(endRangeStr.replace(")",""))

    print filename,[startRange,endRange],kind,info

