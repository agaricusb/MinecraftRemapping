#!/usr/bin/python

# Make srg MD and FD from output of jpdiff.py

for line in file("fields-with-signatures.csv").readlines():  # grep -v DEBUG|grep -v "("
    line = line.strip()
    if line == "": continue
    tokens = line.split("\t")
    if tokens[0] == "obf-class": continue

    obf_class, obf_field, obf_sig, cb_field, cb_sig = tokens

    print "FD: %s/%s %s" % (obf_class, obf_field, cb_field) 

for line in file("methods-with-signatures.csv").readlines(): # grep -v DEBUG|grep "("
    line = line.strip()
    if line == "": continue
    tokens = line.split("\t")
    if tokens[0] == "obf-class": continue

    obf_class, obf_method, obf_sig, cb_method, cb_sig = tokens

    if obf_class == obf_method: continue  # skip constructors


    print "MD: %s/%s %s %s %s" % (obf_class, obf_method, obf_sig, cb_method, cb_sig)


