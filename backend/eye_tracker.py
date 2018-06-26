
import sys
from ... import params
#This sets the path in our computer to where the eyetracker stuff is located
#sys.path.append('/Users/Preetpal/desktop/ubc_4/experimenter_platform/modules')
sys.path.append('C:\\Users\\admin\\Desktop\\experimenter_platform\\modules')

from tobii.eye_tracking_io.basic import EyetrackerException

import os
import datetime
import time

import tobii.eye_tracking_io.mainloop
import tobii.eye_tracking_io.browsing
import tobii.eye_tracking_io.eyetracker
import tobii.eye_tracking_io.time.clock
import tobii.eye_tracking_io.time.sync
import csv
import numpy as np
from tornado import gen
from dummy_controller import DummyController

class TobiiController:

	"""Class to handle communication to Tobii eye trackers, as well as some
	display operations"""

	def __init__(self):

		"""Initializes TobiiController instances

		keyword arguments
		None
		"""
		# eye tracking
		self.eyetracker = None
		self.eyetrackers = {}
		self.gazeData = []
		self.eventData = []
		self.datafile = None
		#Preetpal's code for fixation
		self.x = []
		self.y = []
		self.time = []
		self.validity = []
		self.pupilsize = []
		self.pupilvelocity = []
		self.head_distance = []
		self.EndFixations = []
		#This contains the websocket to send data to be displayed on front end
		self.liveWebSocket = set()
		self.runOnlineFix = True
		# initialize communications
		tobii.eye_tracking_io.init()
		self.clock = tobii.eye_tracking_io.time.clock.Clock()
		self.mainloop_thread = tobii.eye_tracking_io.mainloop.MainloopThread()
		self.browser = tobii.eye_tracking_io.browsing.EyetrackerBrowser(self.mainloop_thread, lambda t, n, i: self.on_eyetracker_browser_event(t, n, i))
		self.mainloop_thread.start()

		# for computing pupil velocity
		self.last_pupil_left = -1
		self.last_pupil_right = -1
		self.LastTimestamp = -1
		self.init_emdat_global_features()

	def waitForFindEyeTracker(self):

		"""Keeps running until an eyetracker is found

		arguments
		None

		keyword arguments
		None

		returns
		None		--	only returns when an entry has been made to the
					self.eyetrackers dict
		"""

		while len(self.eyetrackers.keys())==0:
			pass

	def on_eyetracker_browser_event(self, event_type, event_name, eyetracker_info):

		"""Adds a new or updates an existing tracker to self.eyetrackers,
		if one is available

		arguments
		event_type		--	a tobii.eye_tracking_io.browsing.EyetrackerBrowser
						event
		event_name		--	don't know what this is for; probably passed
						by some underlying Tobii function, specifying
						a device name; it's not used within this
						function
		eyetracker_info	--	a struct containing information on the eye
						tracker (e.g. it's product_id)

		keyword arguments
		None

		returns
		False			--	returns False after adding a new tracker to
						self.eyetrackers or after deleting it
		"""

		# When a new eyetracker is found we add it to the treeview and to the
		# internal list of eyetracker_info objects
		if event_type == tobii.eye_tracking_io.browsing.EyetrackerBrowser.FOUND:
			self.eyetrackers[eyetracker_info.product_id] = eyetracker_info
			return False

		# Otherwise we remove the tracker from the treeview and the eyetracker_info list...
		del self.eyetrackers[eyetracker_info.product_id]

		# ...and add it again if it is an update message
		if event_type == tobii.eye_tracking_io.browsing.EyetrackerBrowser.UPDATED:
			self.eyetrackers[eyetracker_info.product_id] = eyetracker_info
		return False

	def destroy(self):

		"""Removes eye tracker and stops all operations

		arguments
		None

		keyword arguments
		None

		returns
		None		--	sets self.eyetracker and self.browser to None;
					stops browser and the
					tobii.eye_tracking_io.mainloop.MainloopThread
		"""

		self.eyetracker = None
		self.browser.stop()
		self.browser = None
		self.mainloop_thread.stop()

	############################################################################
	# activation methods
	############################################################################

	def activate(self,eyetracker):

		"""Connects to specified eye tracker

		arguments
		eyetracker	--	key for the self.eyetracker dict under which the
					eye tracker to which you want to connect is found

		keyword arguments
		None

		returns
		None		--	calls TobiiController.on_eyetracker_created, then
					sets self.syncmanager
		"""

		eyetracker_info = self.eyetrackers[eyetracker]
		print "Connecting to:", eyetracker_info
		tobii.eye_tracking_io.eyetracker.Eyetracker.create_async(self.mainloop_thread,
													 eyetracker_info,
													 lambda error, eyetracker: self.on_eyetracker_created(error, eyetracker, eyetracker_info))

		while self.eyetracker==None:
			pass
		self.syncmanager = tobii.eye_tracking_io.time.sync.SyncManager(self.clock,eyetracker_info,self.mainloop_thread)

	def on_eyetracker_created(self, error, eyetracker, eyetracker_info):

		"""Function is called by TobiiController.activate, to handle all
		operations after connecting to a tracker has been succesfull

		arguments
		error			--	some Tobii error message
		eyetracker		--	key for the self.eyetracker dict under which
						the eye tracker that is currently connected
		eyetracker_info	--	name of the eye tracker to which a
						connection has been established

		keyword arguments
		None

		returns
		None or False	--	returns nothing and sets self.eyetracke on
						connection success; returns False on failure
		"""

		if error:
			print("WARNING! libtobii.TobiiController.on_eyetracker_created: Connection to %s failed because of an exception: %s" % (eyetracker_info, error))
			if error == 0x20000402:
				print("WARNING! libtobii.TobiiController.on_eyetracker_created: The selected unit is too old, a unit which supports protocol version 1.0 is required.\n\n<b>Details:</b> <i>%s</i>" % error)
			else:
				print("WARNING! libtobii.TobiiController.on_eyetracker_created: Could not connect to %s" % (eyetracker_info))
			return False

		self.eyetracker = eyetracker

	def startTracking(self):

		"""Starts the collection of gaze data

		arguments
		None

		keyword arguments
		None

		returns
		None		--	resets both self.gazeData and self.eventData, then
					sets TobiiTracker.on_gazedata as an event callback
					for self.eyetracker.events.OnGazeDataReceived and
					calls self.eyetracker.StartTracking()
		"""

		self.gazeData = []
		self.eventData = []
		self.eyetracker.events.OnGazeDataReceived += self.on_gazedata
		self.eyetracker.StartTracking()

		#Preetpal's Code to initialize/empty arrays to be used in fixation algorithm
		self.x = []
		self.y = []
		self.time = []
		self.validity = []
		self.pupilsize = []
		self.pupilvelocity = []
		self.head_distance = []

	def stopTracking(self):

		"""Starts the collection of gaze data

		arguments
		None

		keyword arguments
		None

		returns
		None		--	calls self.eyetracker.StopTracking(), then unsets
					TobiiTracker.on_gazedata as an event callback for
					self.eyetracker.events.OnGazeDataReceived, and
					calls TobiiTracker.flushData before resetting both
					self.gazeData and self.eventData
		"""

		self.eyetracker.StopTracking()
		self.eyetracker.events.OnGazeDataReceived -= self.on_gazedata
		#self.flushData()
		self.gazeData = []
		self.eventData = []
		#Preetpals code
		#Empty the arrays needed for fixation algorithm
		#May need to also empty the websocket set
		self.x = []
		self.y = []
		self.time = []
		self.validity = []
		self.pupilsize = []
		self.pupilvelocity = []
		self.head_distance = []

	def on_gazedata(self,error,gaze):

		"""Adds new data point to the data collection (self.gazeData)

		arguments
		error		--	some Tobii error message, isn't used in function
		gaze		--	Tobii gaze data struct

		keyword arguments
		None

		returns
		None		--	appends gaze to self.gazeData list
		"""

		#Don't need raw gaze so this code is commented out
		#self.gazeData.append(gaze)

		#Below code is just print statements that are commented out
		'''
		print 'Timestamp: ', gaze.Timestamp
		print 'LeftGazePoint2D: ', gaze.LeftGazePoint2D
		print 'RightGazePoint2D: ', gaze.RightGazePoint2D
		print 'LeftEyePosition3D: ', gaze.LeftEyePosition3D
		print 'RightEyePosition3D', gaze.RightEyePosition3D
		print 'LeftPupil: ', gaze.LeftPupil
		print 'RightPupil: ', gaze.RightPupil
		'''

		#Below code checks to see if the gaze data is valid. If it is valid then
		#we average the left and right. Else we use the valid eye. We are multiplying
		#by 1280 and 1024 because those are the dimensions of the monitor and since
		#the gaze values returned are between 0 and 1
		if ((gaze.LeftGazePoint2D.x >= 0) & (gaze.RightGazePoint2D.x >= 0)):
			self.x.append(((gaze.LeftGazePoint2D.x + gaze.RightGazePoint2D.x)/2) * 1280)
			self.y.append(((gaze.LeftGazePoint2D.y + gaze.RightGazePoint2D.y)/2) * 1024)
		elif (gaze.LeftGazePoint2D.x >= 0):
			self.x.append(gaze.LeftGazePoint2D.x * 1280)
			self.y.append(gaze.LeftGazePoint2D.y * 1024)
		elif (gaze.RightGazePoint2D.x >= 0):
			self.x.append(gaze.RightGazePoint2D.x * 1280)
			self.y.append(gaze.RightGazePoint2D.y * 1024)
		else:
			self.x.append(-1 * 1280)
			self.y.append(-1 * 1024)
		# Pupil size feature
		self.pupilsize.append(self.get_pupil_size(gaze.LeftPupil, gaze.RightPupil))
		if (self.last_pupil_right != -1):
			self.pupilvelocity.append(self.get_pupil_velocity(self.last_pupil_left, self.last_pupil_right, gaze.LeftPupil, gaze.RightPupil, gaze.Timestamp - self.LastTimestamp))
		#Future work: Validity Checking
		#if ((gaze.LeftValidity != 0) & (gaze.RightValidity != 0)):
		self.time.append(gaze.Timestamp)
		self.head_distance.append(self.get_distance(gaze.LeftEyePosition3D.z, gaze.RightEyePosition3D.z))
		self.validity.append(gaze.LeftValidity == 0 or gaze.RightValidity == 0)
		# for pupil velocity
		self.last_pupil_left = gaze.LeftPupil
		self.last_pupil_right = gaze.LeftPupil
		self.LastTimestamp = gaze.Timestamp

	def add_fixation(self, x, y, duration):
		self.EndFixations.append((x, y, duration))

	def get_pupil_size(self, pupilleft, pupilright):
	    '''
	    If recordings for both eyes are available, return their average,
	    else return value for a recorded eye (if any)
	    Args:
	        pupilleft - recording of pupil size on left eye
	        pupilright - recording of pupil size on right eye
	    Returns:
	        pupil size to generate pupil features with.
	    '''
	    if pupilleft is None and pupilright is None:
	        return -1
	    if pupilleft is None:
	        return pupilright
	    if pupilright is None:
	        return pupilleft
	    return (pupilleft + pupilright) / 2.0


	def get_pupil_velocity(self, last_pupilleft, last_pupilright, pupilleft, pupilright, time):
	    if (last_pupilleft is None or pupilleft is None) and (last_pupilright is None or pupilright is None):
	        return -1
	    if (last_pupilleft is None or pupilleft is None):
	        return abs(pupilright - last_pupilright) / time
	    if (last_pupilright is None or pupilright is None):
	        return abs(pupilleft - last_pupilleft) / time
	    return abs( (pupilleft + pupilright) / 2 - (last_pupilleft + last_pupilright) / 2 ) / time

	def get_distance(self, distanceleft, distanceright):
	    if distanceleft is None and distanceright is None:
	        return -1
	    if distanceleft is None:
	        return distanceright
	    if distanceright is None:
	        return distanceleft
	    return (distanceleft + distanceright) / 2.0

	def init_emdat_global_features(self):
		self.emdat_global_features = {}
		# Pupil features
		self.emdat_global_features['numpupilsizes']		= 0
		self.emdat_global_features['numpupilvelocity']  = 0
		self.emdat_global_features['meanpupilsize'] 			= -1
		self.emdat_global_features['stddevpupilsize'] 			= -1
		self.emdat_global_features['maxpupilsize'] 			= -1
		self.emdat_global_features['minpupilsize'] 			= -1
		#self.emdat_global_features['startpupilsize'] 			= -1
		#self.emdat_global_features['endpupilsize'] 			= -1
		self.emdat_global_features['meanpupilvelocity'] 		= -1
		self.emdat_global_features['stddevpupilvelocity'] 		= -1
		self.emdat_global_features['maxpupilvelocity'] 		= -1
		self.emdat_global_features['minpupilvelocity'] 		= -1
		# Distance features
		self.emdat_global_features['numdistancedata']							= 0
		self.emdat_global_features['meandistance'] 			= -1
		self.emdat_global_features['stddevdistance'] 			= -1
		self.emdat_global_features['maxdistance'] 				= -1
		self.emdat_global_features['mindistance'] 				= -1
		#self.emdat_global_features['startdistance'] 			= -1
		#self.emdat_global_features['enddistance'] 			= -1
		# Saccade features
		"""
		self.emdat_global_features['numsaccades'] 				= 0
		self.emdat_global_features['sumsaccadedistance'] 		= -1
		self.emdat_global_features['meansaccadedistance'] 		= -1
		self.emdat_global_features['stddevsaccadedistance'] 	= -1
		self.emdat_global_features['longestsaccadedistance'] 	= -1
		self.emdat_global_features['sumsaccadeduration'] 		= -1
		self.emdat_global_features['meansaccadeduration'] 		= -1
		self.emdat_global_features['stddevsaccadeduration'] 	= -1
		self.emdat_global_features['longestsaccadeduration'] 	= -1
		self.emdat_global_features['meansaccadespeed'] 		= -1
		self.emdat_global_features['stddevsaccadespeed'] 		= -1
		self.emdat_global_features['maxsaccadespeed'] 			= -1
		self.emdat_global_features['minsaccadespeed'] 			= -1
		self.emdat_global_features['fixationsaccadetimeratio'] = -1
		"""
		# Path features
		self.emdat_global_features['numfixdistances'] = 0
		self.emdat_global_features['numabsangles'] = 0
		self.emdat_global_features['numrelangles'] = 0
		self.emdat_global_features['meanpathdistance'] 		= -1
		self.emdat_global_features['sumpathdistance'] 			= -1
		self.emdat_global_features['stddevpathdistance'] 		= -1
		self.emdat_global_features['eyemovementvelocity'] 		= -1
		self.emdat_global_features['sumabspathangles'] 		= -1
		self.emdat_global_features['abspathanglesrate'] 		= -1
		self.emdat_global_features['meanabspathangles']		= -1
		self.emdat_global_features['stddevabspathangles']		= -1
		self.emdat_global_features['sumrelpathangles'] 		= -1
		self.emdat_global_features['relpathanglesrate'] 		= -1
		self.emdat_global_features['meanrelpathangles']		= -1
		self.emdat_global_features['stddevrelpathangles'] 		= -1
		# Fixation features
		self.emdat_global_features['numfixations'] 			= 0
		self.emdat_global_features['fixationrate'] 			= -1
		self.emdat_global_features['meanfixationduration'] 	= -1
		self.emdat_global_features['stddevfixationduration'] 	= -1
		self.emdat_global_features['sumfixationduration'] 		= -1
		self.emdat_global_features['fixationrate'] 			= -1

	def flush(self):
		self.x = []
		self.y = []
		self.time = []
		self.validity = []

#Original code provided by Roberto showing how to start the the eyetracker
"""
#this will be called from a tornado handler
if __name__ == "__main__":
    eb = TobiiController()
    eb.waitForFindEyeTracker()
    print eb.eyetrackers
    eb.activate(eb.eyetrackers.keys()[0])

    eb.startTracking()
    time.sleep(10)
    eb.stopTracking()

    eb.destroy()
"""
