#!/usr/bin/env python

import os
import siteUtils
import shutil
import glob
import sys

jobDir = siteUtils.getJobDir()

#shutil.copy("%s/getrebdetails.py" % jobDir ,os.getcwd())



for i in range(2) :
     print "RETEST (N/y)?"
sys.stdout.flush()
answer = raw_input("RETEST (N/y)?")
if "y" in answer.lower() :
     raise Exception("PURPOSELY crashing to allow a retest via retrying the e-Traveler step")

answer = raw_input("Please paste copy of executed command - ")
print "command = ",answer

#os.system("./rebalive_plots.sh 2>&1 logplt &")

results = []

any_fp_files = glob.glob("*.txt")
any_fp_files = any_fp_files + glob.glob("*summary*")
any_fp_files = any_fp_files + glob.glob("*png")
any_fp_files = any_fp_files + glob.glob("*log*")

data_products = [lcatr.schema.fileref.make(item) for item in any_fp_files]
results.extend(data_products)



