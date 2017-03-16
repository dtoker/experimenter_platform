
import sys

sys.path.append('/Users/Preetpal/desktop/ubc_4/experimenter_platform/modules')

from tobii.eye_tracking_io.basic import EyetrackerException

import os
import datetime
import time

import tobii.eye_tracking_io.mainloop
import tobii.eye_tracking_io.browsing
import tobii.eye_tracking_io.eyetracker
import tobii.eye_tracking_io.time.clock
import tobii.eye_tracking_io.time.sync


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

		#Preetpal's code
		self.leftx = 0
		self.lefty = 0
		self.leftxarray = []
		self.leftyarray = []
		self.timearray = []
		
		# initialize communications
		tobii.eye_tracking_io.init()
		self.clock = tobii.eye_tracking_io.time.clock.Clock()
		self.mainloop_thread = tobii.eye_tracking_io.mainloop.MainloopThread()
		self.browser = tobii.eye_tracking_io.browsing.EyetrackerBrowser(self.mainloop_thread, lambda t, n, i: self.on_eyetracker_browser_event(t, n, i))
		self.mainloop_thread.start()
		
		
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
		
		self.gazeData.append(gaze)
		'''
		print 'Timestamp: ', gaze.Timestamp
		print 'LeftGazePoint2D: ', gaze.LeftGazePoint2D
		print 'RightGazePoint2D: ', gaze.RightGazePoint2D
		print 'LeftEyePosition3D: ', gaze.LeftEyePosition3D
		print 'RightEyePosition3D', gaze.RightEyePosition3D
		print 'LeftPupil: ', gaze.LeftPupil
		print 'RightPupil: ', gaze.RightPupil
		#Preetpal's code
		print 'Leftxarray: ', self.leftxarray
		print 'Leftyarray: ', self.leftyarray
		print 'TimeArray: ', self.timearray
		print '----------------------------------------'
		'''
		#Preetpal's code
		'''
		if self.leftx == 0:
			self.leftx = 1
		else: 
			self.leftx = 0 
		'''
		self.leftx = gaze.LeftGazePoint2D.x
		self.lefty = gaze.LeftGazePoint2D.y
		self.leftxarray.append(gaze.LeftGazePoint2D.x)
		self.leftyarray.append(gaze.LeftGazePoint2D.y)
		self.timearray.append(gaze.Timestamp)
		

"""
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

