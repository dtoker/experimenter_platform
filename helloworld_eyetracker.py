import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import os.path

import sqlite3
import datetime
import json
import random

# Imports required for EYE TRACKING Code:
import tornado.websocket
import time
import eye_tracker
from eye_tracker import TobiiController
import csv

import thread
from threading import Thread
from tornado import gen
from tornado.ioloop import IOLoop
##########################################

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        #connects url with code
        handlers = [
            (r"/", MainHandler),
            (r"/fixation", FixationHandler),
            (r"/websocket", EchoWebSocketHandler)

        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        #initializes web app
        tornado.web.Application.__init__(self, handlers, **settings)

#each ____Handler is associated with a url
#def get is for when a http get request is made to the url
#def post is for when a http post request is made to the url(ex: form is submitted)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #displays contents of index.html
        self.redirect('/fixation')


class FixationHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("fixations.html")

# tornado.websocket.WebSocketHandler is specific to Tornado, is the super class to control websockets
class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):

    #eb = None

    def open(self):
        '''
        print "WebSocket opened"

        #create the controller to the eye tracker
        eb = TobiiController() #TobiiController is the main class of eye_tracker.py

        #Add self(which is a websocket) to the eyetracker object
        eb.liveWebSocket.add(self)
        print "eb created"

        eb.waitForFindEyeTracker() #wait 'till it's found
        print eb.eyetrackers #we found one!
        eb.activate(eb.eyetrackers.keys()[0]) #activate

        #Start tracking gaze data
        eb.startTracking()
        print "tracking started"

        eb.liveWebSocket.add(self)

        #Load Preetpal's online fixation code
        #returns: [list of lists, each containing [starttime, endtime, duration, endx, endy]
        myOnlineFixations =  eb.onlinefix()

        #ADD STOP BUTTON

        #Write out a CSV Log file of the gaze interaction
        fl = open('myOnlineFixations.csv', 'wb')
        writer = csv.writer(fl)
        writer.writerow(['fixation_index', 'start_time', 'end_time', 'duration', 'end_x', 'end_Y'])
        fixation_index = 1
        for values in myOnlineFixations:
            writer.writerow([fixation_index] + values[0])
            fixation_index = fixation_index + 1
        fl.close()

        #clean up eye tracking tracking and object
        eb.stopTracking()
        eb.destroy()
        '''

    #not sure if needed
    @gen.coroutine
    def on_message(self, message):
        print message
        if (message == "stop"):
            self.eb.runOnlineFix = False
        #self.write_message(u"Time Stamp: " + str(time.time()))
        #print("sending message from server")
        print "WebSocket opened"

        #create the controller to the eye tracker
        self.eb = TobiiController() #TobiiController is the main class of eye_tracker.py

        #Add self(which is a websocket) to the eyetracker object
        self.eb.liveWebSocket.add(self)
        print "eb created"

        self.eb.waitForFindEyeTracker() #wait 'till it's found
        print self.eb.eyetrackers #we found one!
        self.eb.activate(self.eb.eyetrackers.keys()[0]) #activate

        #Start tracking gaze data
        self.eb.startTracking()
        print "tracking started"

        self.eb.liveWebSocket.add(self)

        #Load Preetpal's online fixation code
        #returns: [list of lists, each containing [starttime, endtime, duration, endx, endy]
        myOnlineFixations = None
        while (myOnlineFixations == None):
            myOnlineFixations = yield self.eb.onlinefix()
        print myOnlineFixations

        #ADD STOP BUTTON
        #Write out a CSV Log file of the gaze interaction
        fl = open('myOnlineFixations.csv', 'wb')
        writer = csv.writer(fl)
        writer.writerow(['fixation_index', 'start_time', 'end_time', 'duration', 'end_x', 'end_Y'])
        fixation_index = 1
        for values in myOnlineFixations:
            writer.writerow([fixation_index] + values[0])
            fixation_index = fixation_index + 1
        fl.close()

        #clean up eye tracking tracking and object
        self.eb.stopTracking()
        self.eb.destroy()

    def on_close(self):
        print("WebSocket closed")

#main function is first thing to run when application starts
def main():
    tornado.options.parse_command_line()
    #Application() refers to 'class Application'
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
