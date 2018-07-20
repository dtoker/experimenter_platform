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
import backend.eye_tracker
from backend.eye_tracker import TobiiController
from backend.dummy_controller import DummyController
from backend.fixation_detector import FixationDetector
from backend.emdat_component import EMDATComponent
import csv

import thread
from threading import Thread
from tornado import gen
from tornado.ioloop import IOLoop
import params

from application.middleend.adaptation_loop import AdaptationLoop
from application.application_state_controller import ApplicationStateController
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

    def open(self):
        self.websocket_ping_interval = 0
        self.websocket_ping_timeout = float("inf")

        self.app_state_control = ApplicationStateController(2)
        self.adaptation_loop = AdaptationLoop(self.app_state_control)
        self.adaptation_loop.liveWebSocket.append(self)

        self.tobii_controller = TobiiController()
        self.tobii_controller.liveWebSocket.add(self)
        self.tobii_controller.waitForFindEyeTracker()
        print self.tobii_controller.eyetrackers
        self.fixation_component = FixationDetector(self.tobii_controller, self.adaptation_loop, liveWebSocket = self.tobii_controller.liveWebSocket)
        self.emdat_component = EMDATComponent(self.tobii_controller, self.adaptation_loop, callback_time = params.EMDAT_CALL_PERIOD)

    def on_message(self, message):
        if (message == "close"):
            print("destroying")
            #DummyController.receiveFixations = False
            self.emdat_component.execfile.close()
            self.fixation_component.stop()
            #self.emdat_component.stop()

            self.tobii_controller.stopTracking()
            self.tobii_controller.destroy()
            self.app_state_control.resetApplication()
            return
        elif (message == "next_task"):
            del self.fixation_component
            # TODO: Decide what to do with emdat when task finishes!
            self.tobii_controller.stop()
            self.tobii_controller.flush()
            self.app_state_control.changeTask(2)
            self.fixation_component = FixationDetector(self.tobii_controller, self.app_state_control, liveWebSocket = self.tobii_controller.liveWebSocket)
            #self.emdat_component = EMDATComponent(self.tobii_controller, self.app_state_control, liveWebSocket = self.tobii_controller.liveWebSocket, callback_time = 6000)
            self.tobii_controller.start()
            self.fixation_component.start()
            #self.emdat_component.start()
        else:

            self.tobii_controller.activate(self.tobii_controller.eyetrackers.keys()[0])
            self.tobii_controller.startTracking()
            self.fixation_component.start()
            self.emdat_component.start()
            print "tracking started"

    def on_close(self):
        print("WebSocket closed")

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8000)
    #controller = DummyController()
    #IOLoop.instance().add_callback(callback = controller.wait_for_fixation_2)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
