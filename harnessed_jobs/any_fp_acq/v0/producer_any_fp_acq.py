#!/usr/bin/env python
import os
import sys

for i in range(2) :
     print("From lsst-dc06, execute the acquisition command like\n./comcam-data.py --symlink %s examples/flat.cfg\nThen return here and press enter to proceed with archiving the data products\n" % os.getcwd())
sys.stdout.flush()

answer = input("From lsst-dc06, execute the acquisition command like\n./comcam-data.py --symlink %s examples/flat.cfg\nThen return here and press enter to proceed with archiving the data products\n" % os.getcwd())
