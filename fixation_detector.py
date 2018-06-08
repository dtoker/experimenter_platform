from detection_component import DetectionComponent

class FixationDetector(DetectionComponent):

    #Preetpal's Online/Realtime fixation algorithm
    @gen.coroutine
    def run(self):
        print "detecting Fixations"
        #list of lists, each containing [starttime, endtime, duration, endx, endy]
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
                else:
                    yield
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
                        else:
                            yield
                    #Get next 7 element chunk of data
                    nextX = self.x[array_index : (array_index + array_iterator)]
                    nextY = self.y[array_index : (array_index + array_iterator)]
                    nextTime = self.time[array_index : (array_index + array_iterator)]
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
                        else:
                            yield
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
                    DummyController.fixationReceived = True
                    DummyController.fixationBuffer = Efix
                    break
        yield Efix

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
