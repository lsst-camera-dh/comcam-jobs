"""
BOT PD module
"""
from __future__ import print_function
import os
import sys
import glob
import time
from java.time import Duration
from collections import namedtuple
import logging
import re
try:
    import java.lang
except ImportError:
    print("could not import java.lang")
from ccs_scripting_tools import CcsSubsystems, CCS
#from ts8_utils import set_ccd_info, write_REB_info

bbsub = CCS.attachProxy("ts8-bench/Monitor")
#pdsub = CCS.attachProxy("bot-bench PhotoDiode")

__all__ = ["PhotodiodeReadout","logger"]

CCS.setThrowExceptions(True)

logging.basicConfig(format="%(message)s",
                    level=logging.INFO,
                    stream=sys.stdout)
logger = logging.getLogger()
nreads = 0
nplc = 0

class PhotodiodeReadout(object):
    """
    Class to handle monitoring photodiode readout.
    """
    def __init__(self, exposure, max_reads=2048):
        print(" **************************** ")
        print(" PD readout exposure time requested = ",exposure)
        exptime = 1.0 * exposure
        """
        Parameters
        ----------
        exptime : float
            Exposure time in seconds for the frame to be taken.
        eo_acq_object : EOAcquisition object
            An instance of a subclass of EOAcquisition.
        max_reads : int, optional
            Maximum number of reads of monitoring photodiode.  Default: 2048.
        """

        buffertime = 8.0


        # for exposures over 0.5 sec, nominal PD readout at 60Hz,
        # otherwise 240Hz


        if exptime > 0.5:
            self.nplc = 1.
        else:
            self.nplc = 0.25

        # add a buffer to duration of PD readout
        total_time = exptime + buffertime
        self.nreads = min(total_time*60./self.nplc, max_reads)
        print("self.nreads = ",self.nreads)
        self.nreads = int(self.nreads)

        # adjust PD readout when max_reads is reached
        # (needs to be between 0.001 and 60 - add code to check)
        self.nplc = (exptime + buffertime)*60./self.nreads
        pd_result = None
        self.start_time = None

    def start_accumulation(self):
        """
        Start the asynchronous accumulation of photodiode current readings.
        """

        # get Keithley picoAmmeters ready by resetting and clearing buffer
#        sub.pd.synchCommand(60, "reset")
#        bbsub.synchCommand(60, "resetPD")
#        bbsub.synchCommand(60, "clearPDbuff")
#        bbsub.sendSynchCommand("resetPD")
#        bbsub.sendSynchCommand("Photodiode/setCurrentRange 0.0000002")
        bbsub.sendSynchCommand("clearPDbuff")

        # start accummulating current readings
        logger.info("accumPDBuffer being called with self.nreads = %d and self.nplc = %f",self.nreads,self.nplc)
#        pd_result = bbsub.asynchCommand("accumPDBuffer", self.nreads,
#                                                    self.nplc, True)
        pd_result = bbsub.sendAsynchCommand("accumPDBuffer", self.nreads,
                                                    self.nplc)
        self.start_time = time.time()
        logger.info("Photodiode readout accumulation started at %f",
                         self.start_time)

        running = False
        while not running:
            time.sleep(0.25)
            try:
#                running = bbsub.synchCommand(20, "isPDAccumInProgress").getResult()
                running = bbsub.sendSynchCommand( "isPDAccumInProgress")
#.getResult()
            except StandardError as eobj:
                logger.info("PhotodiodeReadout.start_accumulation:")
                logger.info(str(eobj))
            except :
                logger.info("isPDAccumInProgress command rejected")

            logger.info("Photodiode checking that accumulation started at %f",
                         time.time() - self.start_time)

    def write_readings(self, destination_spec, seqno, icount=1):
        """
        Output the accumulated photodiode readings to a text file.
        """

        self.destination = destination_spec
        logger.info("PD destination directory = %s",self.destination)

        # make sure Photodiode readout has had enough time to run
        pd_filename = os.path.join(self.destination,"Photodiode_Readings.txt")

        print("The ultimate pd filename is ",pd_filename)

        logger.info("Photodiode about to be readout at %f",
                         time.time() - self.start_time)
        readTimeout = Duration.ofSeconds(1000)
        result = bbsub.sendSynchCommand(readTimeout, "readPDbuffer", pd_filename)
        logger.info("Photodiode readout accumulation finished at %f",
                         time.time() - self.start_time)
#        logger.info("Photodiode readout accumulation finished at %f, %s",
#                         time.time() - self.start_time, result.getResult())

        return pd_filename

# Not currently used ... to be removed once its inutility is confirmed
    def add_pd_time_history(self, fits_files, pd_filename):
        "Add the photodiode time history as an extension to the FITS files."
        for fits_file in fits_files:
            full_path = glob.glob('%s/*/%s' % (self.destination, fits_file))[0]
#            command = "addBinaryTable %s %s AMP0.MEAS_TIMES AMP0_MEAS_TIMES AMP0_A_CURRENT %d" % (pd_filename, full_path, self.start_time)
#            sub.ts8.synchCommand(200, command)
#            logger.info("Photodiode readout added to fits file %s",
#                             fits_file)

    def get_readings(self, fits_files, seqno, icount):
        """
        Output the accumulated photodiode readings to a text file and
        write that time history to the FITS files as a binary table
        extension.
        """
        pd_filename = write_readings(seqno, icount)
        try:
            add_pd_time_history(fits_files, pd_filename)
        except TypeError:
            # We must be using a subsystem-proxy for the ts8
            # subsystem.  TODO: Find a better way to handle the
            # subsystem-proxy case.
            pass
