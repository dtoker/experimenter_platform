from detection_component import DetectionComponent
from dummy_controller import DummyController
from tornado import gen
import ast

class FixationDetector(DetectionComponent):

    def __init__(self, tobii_controller, application_state_controller, liveWebSocket):
        DetectionComponent.__init__(self, tobii_controller, application_state_controller, liveWebSocket = liveWebSocket)
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
        newX = []
        newY = []
        newTime = []
        newValid = []
        while(self.runOnlineFix):
            print("while started")
            while(1):
                if(len(self.tobii_controller.x) > array_index + array_iterator):
                    break
                else:
                    yield
            print("first yield")
            #Get segments of size 7
            curX, curY, curTime, curValid = self.get_data_batch(array_index, array_iterator)
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
                        if(len(self.tobii_controller.x) > array_index + array_iterator):
                            break
                        else:
                            yield
                    #Get next 7 element chunk of data
                    nextX, nextY, nextTime, nextValid = self.get_data_batch(array_index, array_iterator)
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
                            for aoi in self.AOIS:
                                if (fixation_inside_aoi(xVal, yVal, aoi)):
                                    print("sending to websocket")
                                    ws.write_message('{"x":"%d", "y":"%d"}' % (xVal, yVal))
                                    break
                    break
            #We are here because start fixation was detected
            while(1):
                if(Efix == []):
                    array_index = array_index + array_iterator
                    #Wait till array has enough data
                    while(1):
                    	if(len(self.tobii_controller.x) > array_index + array_iterator):
                            break
                    	else:
                            yield
                    #Get next segment of data to append to current array of interest
                    nextX, nextY, nextTime, nextValid = self.get_data_batch(array_index, array_iterator)
                    newX.extend(nextX)
                    newY.extend(nextY)
                    newTime.extend(nextTime)
                    newValid.extend(nextValid)
                    Sfix, Efix = self.fixation_detection(newX, newY, newTime, newValid)
                    #this code ensures that we handle the case where an end
                    #fixation has been detected merely becasue it's the last item
                    #in the array, so we want to keep going to be sure.
                    # TODO: Make sure this actually ever happens
                    #if(Efix != []):
                    #	EfixEndTime = Efix[0][1]
                    #	if (EfixEndTime == self.time[-1]):
                    #        Efix = []
                #a genuine end fixation has been found!
                else:
                    #Add the newly found end fixation to our collection of end fixations
                    self.tobii_controller.EndFixations.append(Efix)
                    #Get time stamp for newly found end fixation
                    EfixEndTime = Efix[0][1]
                    #Update index to data points after newly found end fixation
                    start_fix = self.tobii_controller.time.index(Sfix[0])
                    array_index = self.tobii_controller.time.index(EfixEndTime) + 1
                    points_in_fixation = array_index - start_fix
                    x_fixation = 0
                    y_fixation = 0
                    for i in range(points_in_fixation):
                        if (self.tobii_controller.x[start_fix + i] > 0):
                            x_fixation += self.tobii_controller.x[start_fix + i]
                            y_fixation += self.tobii_controller.y[start_fix + i]
                        else:
                            points_in_fixation -= 1
                    x_fixation /= points_in_fixation
                    y_fixation /= points_in_fixation
                    #Fixation ended, get it off the screen!
                    for ws in self.liveWebSocket:
                        print(len(self.AOIS))
                        for aoi in self.AOIS:
                            print(self.AOIS)
                            if (fixation_inside_aoi(x_fixation, y_fixation, aoi)):
                                print("sending to websocket")
                                ws.write_message('{"x":"%d", "y":"%d"}' % (x_fixation, y_fixation))
                                break
                    #May wanrt to use something like this in the future in there are performace issues
                    #self.x = self.x[array_index:]
                    #self.y = self.y[array_index:]
                    #self.time = self.time[array_index:]
                    #array_index = 0
                    #DummyController.x_from_tobii = self.tobii_controller.x
                    #DummyController.y_from_tobii = self.tobii_controller.y
                    #DummyController.time_from_tobii = self.tobii_controller.time
                    #DummyController.fixationBuffer.append((start_fix, array_index - 1, x_fixation, y_fixation))
                    break
        yield Efix

    def get_data_batch(self, array_index, array_iterator):
        return (self.tobii_controller.x[array_index : (array_index + array_iterator)],
                self.tobii_controller.y[array_index : (array_index + array_iterator)],
                self.tobii_controller.time[array_index : (array_index + array_iterator)],
                self.tobii_controller.validity[array_index : (array_index + array_iterator)])

    def fixation_detection(self, x, y, time, validity, maxdist=35, mindur=100000):

        #Detects fixations, defined as consecutive samples with an inter-sample
        #distance of less than a set amount of pixels (disregarding missing data)

        #arguments
        # TODO: Numpy array??? Make sure it actually is numpy
        #x        -	numpy array of x positions
        #y        -	numpy array of y positions
        #time        -	numpy array of timestamps

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
            #print(x[i], y[i])
        	#print(validity[i])
        	# calculate Euclidean distance from the current fixation coordinate
        	# to the next coordinate
            dist = ((x[si] - x[i])**2 + (y[si] - y[i])**2)**0.5

            # check if the next coordinate is below maximal distance
            if dist <= maxdist and not fixstart:
                #print("fix found")
                #print("fixstart happened")
                si = i - 1
                # if point is not valid, don't treat it as start of a fixation
                if not validity[i]:
                    #print("fix found invalid")
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
                #print('endfix')
                fixstart = False
                if not validity[i]:
                    #print('endfix invalid')
                    # if we don't have more than 9 consequtive invalid points
                    # then we're ok
                    if (invalid_count <= 9):
                    	#print("skipping")
                    	invalid_count += 1
                    	fixstart = True
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
                            si = 0 + i
                            invalid_count = 0
                            continue
                elif not validity[i-1]:
                    #print('prev pt invalid')
                    duration = time[last_valid] - Sfix[-1]
                    #print("duration invalid is %d" % duration)
                    if duration >= mindur:
                    	#print('return fix')
                    	Efix.append((Sfix[-1], time[last_valid], time[last_valid] - Sfix[-1], x[last_valid], y[last_valid]))
                    	break
                    else:
                    	#print('too short')
                    	Sfix.pop(-1)
                    	si = 0 + i
                    	invalid_count = 0
                    	continue
                # only store the fixation if the duration is ok
                #print("duration invalid is %d" % (time[i-1] - Sfix[-1]))
                if time[i-1] - Sfix[-1] >= mindur:
                    Efix.append((Sfix[-1], time[i - 1], time[i - 1] - Sfix[-1], x[si], y[si]))
                    break
                # delete the last fixation start if it was too short
                #print("dur too small")
                Sfix.pop(-1)
                si = self.find_new_start(x, y, maxdist, i, si)
                if (si != i):
                    fixstart = True
                    Sfix.append(time[si])
                last_valid = si
                invalid_count = 0
            elif not fixstart:
                #print('not fixstart')
                si += 1
                if validity[i]:
                    last_valid = i
        	# If within a fixation and within distance,
        	# current point should be valid.
            elif fixstart:
                #print('valid inside fix')
                last_valid = i
                invalid_count = 0
        return Sfix, Efix

    def find_new_start(self, x, y, maxdist, i, si):
        j = si + 1
        while(j < i):
            dist_i_j = ((x[i] - x[j])**2 + (y[i] - y[j])**2)**0.5
            if (dist_i_j <= maxdist):
                break
            j += 1
        return j



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




    inside = False
    poly = ast.literal_eval(str(poly))

    n = len(poly)
    if n == 0:
        return False
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
