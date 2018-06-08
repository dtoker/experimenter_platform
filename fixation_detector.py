from detection_component import DetectionComponent
from dummy_controller import DummyController

class FixationDetector(DetectionComponent):

    def __init__(self, tobii_controller, AOIs):
        super().__init__(tobii_controller)
        self.AOIs = AOIs
        self.runOnlineFix = True

    #Preetpal's Online/Realtime fixation algorithm
    @gen.coroutine
    def run(self):
        #list of lists, each containing [starttime, endtime, duration, endx, endy]
		self.EndFixations = []
		#Keep track of index in x,y,time array
		array_index = 0
		#Used to get segments of size 7
		array_iterator = 7
		#this start variable is here so we can time out after 10 seconds
		#start = time.time()

        # Stream of raw data from Tobii
        raw_x = self.tobii_controller.x
        raw_y = self.tobii_controller.y
        raw_time = self.tobii_controller.time
        raw_validity = self.tobii_controller.validity
        # To be passed to fixation algorithm
		newX = []
		newY = []
		newTime = []
		newValid = []
		while(self.runOnlineFix):
			#function times out and returns after 45 seconds
			#if(time.time() > start + 10):
				#print "timed out after ten seconds"
				#print self.EndFixations
				#return self.EndFixations
			#Wait till array has enough data
			while(1):
				if(len(raw_x) > array_index + array_iterator):
					break
				else:
					yield
			#Get segments of size 7
			curX = raw_x[array_index:(array_index + array_iterator)]
			curY = raw_y[array_index:(array_index + array_iterator)]
			curTime = raw_time[array_index:(array_index + array_iterator)]
			curValid = raw_validity[array_index:(array_index + array_iterator)]
			newX = curX
			newY = curY
			newTime = curTime
			newValid = curValid
			#Sfix	-	list of lists, each containing [starttime]
			#Efix	-	list of lists, each containing [starttime, endtime, duration, endx, endy]
			Sfix, Efix = self.fixation_detection(curX, curY, curTime, curValid)
			#When there is no end fixation detected yet
			while(1):
				#If start of fixation has not been detected yet
				if(Sfix == []):
					array_index += array_iterator
					#Wait till array has filled with enough data
					while(1):
						if(len(raw_x) > array_index + array_iterator):
							break
						else:
							yield
					#Get next 7 element chunk of data
					nextX = raw_x[array_index : (array_index + array_iterator)]
					nextY = raw_y[array_index : (array_index + array_iterator)]
					nextTime = raw_time[array_index : (array_index + array_iterator)]
					nextValid = raw_validity[array_index : (array_index + array_iterator)]

					#Append next segment with current arrays of interest
					#If no more curX we can just newX.extend(nextX)
					newX = curX + nextX
					newY = curY + nextY
					newTime = curTime + nextTime
					newValid = curValid + nextValid
					#Run fixation algorithm again with extended array
					Sfix, Efix = self.fixation_detection(newX, newY, newTime, newValid)

					#If no start detected, then we can use this to drop the first |array_iterator| items
					curX = nextX
					curY = nextY
					curTime = nextTime
					curValid = nextValid
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
						if(len(raw_x) > array_index + array_iterator):
							break
						else:
							yield
					#Get next segment of data to append to current array of interest
					nextX = raw_x[array_index:(array_index + array_iterator)]
					nextY = raw_y[array_index:(array_index + array_iterator)]
					nextTime = raw_time[array_index:(array_index + array_iterator)]
					nextValid = raw_validity[array_index:(array_index + array_iterator)]
					newX.extend(nextX)
					newY.extend(nextY)
					newTime.extend(nextTime)
					newValid.extend(nextValid)
					Sfix, Efix = self.fixation_detection(newX, newY, newTime, newValid)
					#this code ensures that we handle the case where an end
					#fixation has been detected merely becasue it's the last item
					#in the array, so we want to keep going to be sure.
					# TODO: Make sure this actually ever happens
					if(Efix != []):
						EfixEndTime = Efix[0][1]
						if (EfixEndTime == raw_time[-1]):
							Efix = []
				#a genuine end fixation has been found!
				else:
					#Add the newly found end fixation to our collection of end fixations
					self.EndFixations.append(Efix)
					#Get time stamp for newly found end fixation
					EfixEndTime = Efix[0][1]

					#Update index to data points after newly found end fixation
					start_fix = raw_time.index(Sfix[0])
					array_index = raw_time.index(EfixEndTime) + 1
					points_in_fixation = array_index - start_fix
					x_fixation = 0
					y_fixation = 0
					for i in range(points_in_fixation):
						if (raw_x[start_fix + i] > 0):
							x_fixation += raw_x[start_fix + i]
							y_fixation += raw_y[start_fix + i]
						else:
							points_in_fixation -= 1
					x_fixation /= points_in_fixation
					y_fixation /= points_in_fixation
					#Fixation ended, get it off the screen!
					for ws in self.liveWebSocket:
						ws.write_message('{"x":"%d", "y":"%d"}' % (-3000, -3000))
					#May wanrt to use something like this in the future in there are performace issues
					#raw_x = raw_x[array_index:]
					#raw_y = raw_y[array_index:]
					#raw_time = raw_time[array_index:]
					#array_index = 0
					DummyController.x_from_tobii = raw_x
					DummyController.y_from_tobii = raw_y
					DummyController.time_from_tobii = raw_time
					DummyController.fixationBuffer.append((start_fix, array_index - 1, x_fixation, y_fixation))

                    self.notify_app_state_controller(x_fixation, y_fixation)
					break
		yield Efix


	#Pygaze: Offline fixation algorithm (*note mindur has to be defined here in microseconds)
    ## TODO: CLEAN THIS UP ITS UGLY
	def fixation_detection(self, x, y, time, validity, maxdist=35, mindur=60000):

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
		invalid_count = 0
		last_valid = 0

		fixstart = False

		for i in range(1, len(x)):
			print(x[i], y[i])
			#print(validity[i])
			# calculate Euclidean distance from the current fixation coordinate
			# to the next coordinate
			dist = ((x[si] - x[i])**2 + (y[si] - y[i])**2)**0.5

			# check if the next coordinate is below maximal distance
			if dist <= maxdist and not fixstart:
				print("fix found")
				#print("fixstart happened")
				si = i
				# if point is not valid, don't treat it as start of a fixation
				if not validity[i]:
					print("fix found invalid")
					continue
				# start a new fixation
				fixstart = True
				Sfix.append(time[i])
				# Currently last valid point
				last_valid = i
				invalid_count = 0
			# If the fixation started before and the distance between
			# fixation start and current point is too big
			elif dist > maxdist and fixstart:
				#print("condition ment")
				# end the current fixation
				# If point is not valid
				print('endfix')
				if not validity[i]:
					print('endfix invalid')
					# if we don't have more than 9 consequtive invalid points
					# then we're ok
					if (invalid_count <= 9):
						invalid_count += 1
						continue
					# if more than 9, we take treat the last valid point as the end of
					# fixation
					else:
						duration = time[last_valid] - Sfix[-1]
						#print("duration invalid is %d" % duration)
						if duration >= mindur:
							Efix.append((Sfix[-1], time[last_valid], time[last_valid] - Sfix[-1], x[last_valid], y[last_valid]))
							break
						else:
							Sfix.pop(-1)
							fixstart = False
							si = 0 + i
							invalid_count = 0
							continue
				elif not validity[i-1]:
					duration = time[last_valid] - Sfix[-1]
					#print("duration invalid is %d" % duration)
					if duration >= mindur:
						Efix.append((Sfix[-1], time[last_valid], time[last_valid] - Sfix[-1], x[last_valid], y[last_valid]))
						break
					else:
						Sfix.pop(-1)
						fixstart = False
						si = 0 + i
						invalid_count = 0
						continue
				fixstart = False
				# only store the fixation if the duration is ok
				#print("duration invalid is %d" % (time[i-1] - Sfix[-1]))
				if time[i-1] - Sfix[-1] >= mindur:
					Efix.append((Sfix[-1], time[i - 1], time[i - 1] - Sfix[-1], x[si], y[si]))
					break
				# delete the last fixation start if it was too short
				else:
					print("dur too small")
					Sfix.pop(-1)
				si = 0 + i
				last_valid = si
				invalid_count = 0
			elif not fixstart:
				print('not fixstart')
				si += 1
				if validity[i]:
					last_valid = i
			# If within a fixation and within distance,
			# current point should be valid.
			elif fixstart:
				print('valid stuff')
				last_valid = i
				invalid_count = 0
		return Sfix, Efix

    def notify_app_state_controller(self, x, y):
        for aoi in self.AOIs:
            if (fixation_inside_aoi(x, y, aoi)):
                yield #update_controller_and_usermodel()

    def stop(self):
        #TODO: Maybe something else?
        self.runOnlineFix = False

def fixation_inside_aoi(x,y,poly):
    """Determines if a point is inside a given polygon or not

        The algorithm is called "Ray Casting Method".

    Args:
        poly: is a list of (x,y) pairs defining the polgon

    Returns:
        True or False.
    """
    n = len(poly)

    if n == 0:
        return False

    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside
