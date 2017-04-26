
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

import numpy as np
import thread 

#new stuff i need to fix 
#import helloworld


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
		#Preetpal's code for fixation 
		self.counter = 0
		self.x = []
		self.y = []
		self.time = []
		self.EndFixations = []
		self.liveWebSocket = set()
		
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

		#Preetpal's Code 
		self.x = []
		self.y = []
		self.time = []
		

		'''
		online_fixation.onlinefix(xDataForFixation, yDataForFixation, timeDataForFixation)
		'''


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
		
		#Don't need raw gaze so this code is commented out 
		#self.gazeData.append(gaze)
		'''
		print 'Timestamp: ', gaze.Timestamp
		print 'LeftGazePoint2D: ', gaze.LeftGazePoint2D
		print 'RightGazePoint2D: ', gaze.RightGazePoint2D
		print 'LeftEyePosition3D: ', gaze.LeftEyePosition3D
		print 'RightEyePosition3D', gaze.RightEyePosition3D
		print 'LeftPupil: ', gaze.LeftPupil
		print 'RightPupil: ', gaze.RightPupil
		#Preetpal's code
		print 'x: ', self.x
		
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


		#self.leftx = gaze.LeftGazePoint2D.x
		#self.lefty = gaze.LeftGazePoint2D.y
		#self.leftxarray.append(gaze.LeftGazePoint2D.x)
		#self.leftyarray.append(gaze.LeftGazePoint2D.y)
		#self.timearray.append(gaze.Timestamp)

		'''
		Preetpals Comment:
		When gazeData array is 7 send it to fixation algorithm and erase array 
		create a variable to act as a counter 
		if counter reaches 7 send array to fixation detecter and set counter back to 0
			and erase arrays 
		'''
		#Preetpal's code 
		#self.counter = self.counter + 1 

		#Multiplying by the dimensions of my laptop screen 
		self.x.append(gaze.LeftGazePoint2D.x * 1440)
		self.y.append(gaze.LeftGazePoint2D.y * 900)
		self.time.append(gaze.Timestamp)

	def fixation_detection(self, x, y, time, maxdist=35, mindur=60):
    	
        #Detects fixations, defined as consecutive samples with an inter-sample
        #distance of less than a set amount of pixels (disregarding missing data)

        #arguments
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


		for i in range(1,len(x)):
			# calculate Euclidean distance from the current fixation coordinate
			# to the next coordinate
			dist = ((x[si]-x[i])**2 + (y[si]-y[i])**2)**0.5
			# check if the next coordinate is below maximal distance
			if dist <= maxdist and not fixstart:
			# start a new fixation
				si = 0 + i
				fixstart = True
				Sfix.append([time[i]])
			elif dist > maxdist and fixstart:
				# end the current fixation
				fixstart = False
				# only store the fixation if the duration is ok
				if time[i-1]-Sfix[-1][0] >= mindur:
					Efix.append([Sfix[-1][0], time[i-1], time[i-1]-Sfix[-1][0], x[si], y[si]])
				# delete the last fixation start if it was too short
				else:
					Sfix.pop(-1)
				si = 0 + i
			elif not fixstart:
				si += 1
		return Sfix, Efix

	def onlinefix(self):
		self.EndFixations = []
		array_index = 0
		array_iterator = 7

		#this start variable is here so we can time out after 10 seconds 
		start = time.time()

		newX = []
		newY = []
		newTime = []

		while(1):
			#time.sleep(0.0583)
			#function times out and returns after 10 seconds 
			if(time.time() > start + 30):
				print "timed out after ten seconds"
				print self.EndFixations
				return self.EndFixations

			#Wait till array has enough data 
			while(1):
				if(len(self.x) - array_index > 7):
					break

			#print "in outter loop"
			curX = self.x[array_index:(array_index + array_iterator)]
			curY = self.y[array_index:(array_index + array_iterator)]
			curTime = self.time[array_index:(array_index + array_iterator)]

			newX = curX
			newY = curY
			newTime = curTime

			#if(curX == []):
				#break

			print "before calling fixation_detection in outter loop"
			print "printing curX and curY"
			print curX
			print curY
			[Sfix, Efix] = self.fixation_detection(curX, curY, curTime)
			print "after calling fixation_detection in outter loop"
			print Sfix
			print Efix
			#When there is no fixation detected yet
			while(1):
				#time.sleep(0.0583)
				print "in inner loop"
 				if(Sfix == []):
					print "in inner loop if statement"
					array_index = array_index + array_iterator

					#Wait till array has enough data 
					while(1):
						if(len(self.x) - array_index > 7):
							break

					nextX = self.x[array_index:(array_index + array_iterator)]
					nextY = self.y[array_index:(array_index + array_iterator)]
					nextTime = self.time[array_index:(array_index + array_iterator)]

                
					print "newX in 1st while loop"
					print newX
					print "nextX in 1st while loop:"
					print nextX

					print "curX in 1st while loop:"
					print curX 

					newX = curX + nextX
					print "newX after extending in 1st while loop"
					print newX
					newY = curY + nextY
					newTime = curTime + nextTime
					print "calling method in first inner loop"
					[Sfix, Efix] = self.fixation_detection(newX, newY, newTime)
					print "after calling in first inner loop"

					curX = nextX
					curY = nextY
					curTime = nextTime
				else:
					#new stuff I need to fix 
					#helloworld.EchoWebSocketHandler.updateSquare(0.5,0.5)
					SfixTime = Sfix[0][0]
					fixIndex = newTime.index(SfixTime)
					xVal = newX[fixIndex]
					yVal = newY[fixIndex]
					print "************printing xVal and yVal *****************"
					print xVal
					print yVal
					for ws in self.liveWebSocket:
						if ((xVal != -1440) & (yVal != -900)):
							ws.write_message('{"x":"%d", "y":"%d"}' % (xVal, yVal))

					break 
				#if(nextX == []):
					#break

			#When fixation is detected

			#######
			while(1):
				#time.sleep(0.0583)
				print "in second inner while loop"
				if(Efix == []):
					print "in second inner while loop if statement"
					array_index = array_index + array_iterator

					#Wait till array has enough data 
					while(1):
						if(len(self.x) - array_index > 7):
							break

					nextX = self.x[array_index:(array_index + array_iterator)]
					nextY = self.y[array_index:(array_index + array_iterator)]
					nextTime = self.time[array_index:(array_index + array_iterator)] 

					

					print "newX in 2nd while loop:"
					print newX
					print "nextX in 2nd while loop:"
					print nextX

					#newX should extend itself 
					#newX = newX.extend(nextX)
					newX.extend(nextX)
					print "*******newX after extending in 2nd while loop*******"
					print newX
					newY.extend(nextY)
					newTime.extend(nextTime)
					

					print "calling method in 2nd inner loop"
					[Sfix, Efix] = self.fixation_detection(newX, newY, newTime)
					print "after calling in 2nd inner loop"
					print Sfix
					print Efix
				else:
					self.EndFixations.append(Efix)
					EfixEndTime = Efix[0][1]
					'''
					print "printing newTime" 
					print newTime
					print "printing size of newTime"
					print len(newTime)
					print "printing EfixEndTime"
					print EfixEndTime
					print "printing next time"
					print nextTime
					print "printing array_index"
					print array_index
					print "printing index of newTime"
					print newTime.index(EfixEndTime)
					#endTimeIndex = nextTime.index(EfixEndTime)
					#array_index = array_index + endTimeIndex
					'''
					array_index = self.time.index(EfixEndTime) + 1

					for ws in self.liveWebSocket:
						ws.write_message('{"x":"%d", "y":"%d"}' % (-3000, -3000))

					#Emptying the gaze data arrays 
					self.x = []
					self.y = []
					self.time = []
					array_index = 0

					#print EndFixations
					#print a
					#array_index = array_index + array_iterator
					print "**************************appending EndFixations***********************"
					#print self.EndFixations
					break
				#if(nextX == []):
				#    break

		return self.EndFixations

		

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

