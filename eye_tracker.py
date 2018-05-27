
import sys

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

import numpy as np


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

		#Future work: Validity Checking
		#if ((gaze.LeftValidity != 0) & (gaze.RightValidity != 0)):

		self.time.append(gaze.Timestamp)



	#Pygaze: Offline fixation algorithm (*note mindur has to be defined here in microseconds)
	def fixation_detection(self, x, y, time, maxdist=35, mindur=60000):

        #Detects fixations, defined as consecutive samples with an inter-sample
        #distance of less than a set amount of pixels (disregarding missing data)

        #arguments
		# TODO: Numpy array??? Make sure it actually is numpy
        #x		-	numpy array of x positions
        #y		-	numpy array of y positions
        #time		-	numpy array of timestamps

        #keyword arguments
        #maxdist	-	maximal inter sample distance in pixels (default = 25)
        #mindur	-	minimal duration of a fixation in milliseconds; detected
                    #fixation candidates will be disregarded if they are below
                    #this duration (default = 100)

        #returns
        #Sfix, Efix
                    #Sfix	-	list of lists, each containing [starttime]
                    #Efix	-	list of lists, each containing [starttime, endtime, duration, endx, endy]

        # empty list to contain data
		Sfix = []
		Efix = []

		# loop through all coordinates
		si = 0
		fixstart = False


		for i in range(1, len(x)):
			# calculate Euclidean distance from the current fixation coordinate
			# to the next coordinate
			dist = ((x[si] - x[i])**2 + (y[si] - y[i])**2)**0.5
			# check if the next coordinate is below maximal distance
			if dist <= maxdist and not fixstart:
			# start a new fixation
				si = 0 + i
				fixstart = True
				Sfix.append(time[i])
			elif dist > maxdist and fixstart:
				# end the current fixation
				fixstart = False
				# only store the fixation if the duration is ok
				if time[i-1]-Sfix[-1] >= mindur:
					Efix.append((Sfix[-1], time[i - 1], time[i - 1] - Sfix[-1], x[si], y[si]))
				# delete the last fixation start if it was too short
				else:
					Sfix.pop(-1)
				si = 0 + i
			elif not fixstart:
				si += 1
		return Sfix, Efix




	#Preetpal's Online/Realtime fixation algorithm
	def onlinefix(self):
		#list of lists, each containing [starttime, endtime, duration, endx, endy]

		# TODO: Refactor into lost of tuples
		self.EndFixations = []
		#Keep track of index in x,y,time array
		array_index = 0
		#Used to get segments of size 7
		array_iterator = 7

		#this start variable is here so we can time out after 10 seconds
		start = time.time()

		newX = []
		newY = []
		newTime = []

		while(self.runOnlineFix):

			#function times out and returns after 45 seconds
			#if(time.time() > start + 10):
				#print "timed out after ten seconds"
				#print self.EndFixations
				#return self.EndFixations

			#Wait till array has enough data
			while(1):
				if(len(self.x) > array_index + array_iterator):
					break

			#Get segments of size 7
			curX = self.x[array_index:(array_index + array_iterator)]
			curY = self.y[array_index:(array_index + array_iterator)]
			curTime = self.time[array_index:(array_index + array_iterator)]

			newX = curX
			newY = curY
			newTime = curTime

			#Sfix	-	list of lists, each containing [starttime]
			#Efix	-	list of lists, each containing [starttime, endtime, duration, endx, endy]
			Sfix, Efix = self.fixation_detection(curX, curY, curTime)

			#When there is no end fixation detected yet
			while(1):
				#If start of fixation has not been detected yet
 				if(Sfix == []):
					array_index += array_iterator

					#Wait till array has filled with enough data
					while(1):
						if(len(self.x) > array_index + array_iterator):
							break

					#Get next 7 element chunk of data
					nextX = self.x[array_index:(array_index + array_iterator)]
					nextY = self.y[array_index:(array_index + array_iterator)]
					nextTime = self.time[array_index:(array_index + array_iterator)]

					#Append next segment with current arrays of interest
					#If no more curX we can just newX.extend(nextX)
					newX = curX + nextX
					newY = curY + nextY
					newTime = curTime + nextTime

					#Run fixation algorithm again with extended array
					Sfix, Efix = self.fixation_detection(newX, newY, newTime)


					#If no start detected, then we can use this to drop the first |array_iterator| items
					curX = nextX
					curY = nextY
					curTime = nextTime
				else:
					#Get that start fixation x and y values to display on front end
					SfixTime = Sfix[0]
					fixIndex = newTime.index(SfixTime)
					xVal = newX[fixIndex]
					yVal = newY[fixIndex]

					#Get the open websocket and send x and y values through it to front end
					# A start fixation has been detected!
					for ws in self.liveWebSocket:
						if ((xVal != -1280) & (yVal != -1024)):
							ws.write_message('{"x":"%d", "y":"%d"}' % (xVal, yVal))

					break

			#We are here because start fixation was detected
			while(1):
				if(Efix == []):
					array_index = array_index + array_iterator

					#Wait till array has enough data
					while(1):
						if(len(self.x) > array_index + array_iterator):
							break

					#Get next segment of data to append to current array of interest
					nextX = self.x[array_index:(array_index + array_iterator)]
					nextY = self.y[array_index:(array_index + array_iterator)]
					nextTime = self.time[array_index:(array_index + array_iterator)]

					newX.extend(nextX)
					newY.extend(nextY)
					newTime.extend(nextTime)

					Sfix, Efix = self.fixation_detection(newX, newY, newTime)

					#this code ensures that we handle the case where an end
					#fixation has been detected merely becasue it's the last item
					#in the array, so we want to keep going to be sure.
					if(Efix != []):
						EfixEndTime = Efix[0][1]
						if (EfixEndTime == self.time[-1]):
							Efix = []

			    #a genuine end fixation has been found!
				else:
					#Add the newly found end fixation to our collection of end fixations
					self.EndFixations.append(Efix)

					#Get time stamp for newly found end fixation
					EfixEndTime = Efix[0][1]
					#Update index to data points after newly found end fixation
					array_index = self.time.index(EfixEndTime) + 1

					#Fixation ended, get it off the screen!
					for ws in self.liveWebSocket:
						ws.write_message('{"x":"%d", "y":"%d"}' % (-3000, -3000))

					#May wanrt to use something like this in the future in there are performace issues
					#self.x = self.x[array_index:]
					#self.y = self.y[array_index:]
					#self.time = self.time[array_index:]
					#array_index = 0

					break

		return self.EndFixations



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
