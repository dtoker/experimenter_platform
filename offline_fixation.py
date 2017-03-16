import csv 
import numpy as np

def fixation_detection(x, y, time, maxdist=35, mindur=60):
        """
        Detects fixations, defined as consecutive samples with an inter-sample
        distance of less than a set amount of pixels (disregarding missing data)

        arguments
        x		-	numpy array of x positions
        y		-	numpy array of y positions
        time		-	numpy array of timestamps

        keyword arguments
        maxdist	-	maximal inter sample distance in pixels (default = 25)
        mindur	-	minimal duration of a fixation in milliseconds; detected
                    fixation candidates will be disregarded if they are below
                    this duration (default = 100)

        returns
        Sfix, Efix
                    Sfix	-	list of lists, each containing [starttime]
                    Efix	-	list of lists, each containing [starttime, endtime, duration, endx, endy]
        """

        # empty list to contain data
        Sfix = []
        Efix = []

        # loop through all coordinates
        si = 0
        fixstart = False
        print "in fixation algorithm"
        print x
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



def read(filename):
    with open(filename) as f:
        header = True
        gaze_x = []
        gaze_y = []
        timestamps = []


        for row in f:
            if header:
                header = False 
                continue 
            
            row_array = row.strip().split("\t")

            if (len(row_array) != 3):
                continue

            if row_array[0] == "" or row_array[1]  == "" or row_array[2]  == "":
                continue

            temptime = int(round(float(row_array[0])/1000.0, 0)) 

            x = int(row_array[1])
            y = int(row_array[2])
            gaze_x.append(x)
            gaze_y.append(y)
            timestamps.append(temptime)

        return timestamps, gaze_x, gaze_y

[time, x, y] = read('P18copy.txt')


def offlinefix(x, y, time):
    EndFixations = []
    array_index = 0
    array_iterator = 7

    newX = []
    newY = []
    newTime = []


    while(1): 
        print "in outter loop"
        curX = x[array_index:(array_index + array_iterator)]
        curY = y[array_index:(array_index + array_iterator)]
        curTime = time[array_index:(array_index + array_iterator)]

        newX = curX
        newY = curY
        newTime = curTime

        if(curX == []):
            break

        print "before calling fixation_detection in outter loop"
        [Sfix, Efix] = fixation_detection(curX, curY, curTime)
        print "after calling fixation_detection in outter loop"
        print Sfix
        print Efix
        #When there is no fixation detected yet
        while(1):
            print "in inner loop"
            if(Sfix == []):
                print "in inner loop if statement"
                array_index = array_index + array_iterator
                nextX = x[array_index:(array_index + array_iterator)]
                nextY = y[array_index:(array_index + array_iterator)]
                nextTime = time[array_index:(array_index + array_iterator)]
                
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
                [Sfix, Efix] = fixation_detection(newX, newY, newTime)
                print "after calling in first inner loop"

                curX = nextX
                curY = nextY
                curTime = nextTime
            else:
                break 
            if(nextX == []):
                break

        #When fixation is detected
        while(1):
            print "in second inner while loop"
            if(Efix == []):
                print "in second inner while loop if statement"
                array_index = array_index + array_iterator
                nextX = x[array_index:(array_index + array_iterator)]
                nextY = y[array_index:(array_index + array_iterator)]
                nextTime = time[array_index:(array_index + array_iterator)] 

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

                print "calling method in first inner loop"
                [Sfix, Efix] = fixation_detection(newX, newY, newTime)
                print "after calling in first inner loop"
                print Sfix
                print Efix
            else:
                EndFixations.append(Efix)
                

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
                array_index = time.index(EfixEndTime) + 1

                #print EndFixations

                #print a
                #array_index = array_index + array_iterator
                print "appending EndFixations"
                break
            if(nextX == []):
                break

    return EndFixations


myfixations =  offlinefix(x,y,time)

fl = open('myfixations.csv', 'w')

writer = csv.writer(fl)
writer.writerow(['start_time', 'end_time', 'duration', 'end_x', 'end_Y'])
for values in myfixations:
    writer.writerow(values[0])
fl.close()

#realtime_fixation(x,y,time)

#test()

#print fixation_detection(x,y,time)



