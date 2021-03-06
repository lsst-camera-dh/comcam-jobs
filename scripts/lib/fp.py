#!/usr/bin/env ccs-script
from org.lsst.ccs.scripting import CCS
from org.lsst.ccs.bus.states import AlertState
from java.time import Duration
from ccs import proxies
import bot_bench

fp = CCS.attachProxy("comcam-fp")
autoSave = True
imageTimeout = Duration.ofSeconds(60)

def sanityCheck():
   #biasOn = fp.isBackBiasOn()
   #if not biasOn:
   #  print "WARNING: Back bias is not on"
   
   state = fp.getState()
   alert = state.getState(AlertState)
   if alert!=AlertState.NOMINAL:
      print "WARNING: focal-plane subsystem is in alert state %s" % alert 

def clear(n=1):
   print "Clearing CCDs (%d)" % n
   fp.clear(n)
   fp.waitForSequencer(Duration.ofSeconds(10))

def takeBias(fitsHeaderData):
   # TODO: This may not be the best way to take bias images
   # It may be better to define a takeBias command at the subsystem layer, since
   # this could skip the startIntegration/endIntegration and got straigh to readout
   return takeExposure(fitsHeaderData=fitsHeaderData)    

def takeExposure(exposeCommand=None, fitsHeaderData=None):
   sanityCheck()
   clear()
   print "Setting FITS headers %s" % fitsHeaderData
   fp.setHeaderKeywords(fitsHeaderData)
   imageName = fp.startIntegration()
   print "Image name: %s" % imageName
   if exposeCommand: 
      extraData = exposeCommand()
      if extraData:
          fp.setHeaderKeywords(extraData)
   fp.endIntegration()
   if autoSave:
     return (imageName, fp.waitForFitsFiles(imageTimeout))
   else:
     fp.waitForImages(imageTimeout)
     return (imageName, None)    

def takeCombinedExposure(exposeCommand=None, fitsHeaderData=None, secondExposeCommand=None):
   sanityCheck()
   clear()
   print "Setting FITS headers %s" % fitsHeaderData
   fp.setHeaderKeywords(fitsHeaderData)
   imageName = fp.startIntegration()
   print "Image name: %s" % imageName
   if exposeCommand:
      exposeCommand()
   if secondExposeCommand:
      bot_bench.setSpotFilter('open') # change to actual name for an open spot
      secondExposeCommand()
   fp.endIntegration()
   if autoSave:
     return (imageName, fp.waitForFitsFiles(imageTimeout))
   else:
     fp.waitForImages(imageTimeout)
     return (imageName, None)   

      
   

