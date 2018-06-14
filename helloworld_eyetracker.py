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
from dummy_controller import DummyController
from fixation_detector import FixationDetector
from application.app_state_controller import ApplicationStateController
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
        self.app_state_control = ApplicationStateController()
        self.tobii_controller = TobiiController()
        self.tobii_controller.liveWebSocket.add(self)
        self.tobii_controller.waitForFindEyeTracker()
        print self.tobii_controller.eyetrackers

    @gen.coroutine
    def on_message(self, message):
        print message == "close"
        print("Should be destroying")
        if (message == "close"):
            self.eb.runOnlineFix = False
            print("destroying")
            DummyController.receiveFixations = False
            self.eb.stopTracking()
            self.eb.destroy()
            return
        else:
            self.eb.activate(self.eb.eyetrackers.keys()[0])
            self.eb.startTracking()
            self.fixation_component = FixationDetector(self.eb, self.app_state_control, liveWebSocket = self.eb.liveWebSocket)
            self.fixation_component.start()
            print "tracking started"

    def on_close(self):
        print("WebSocket closed")


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8000)
    controller = DummyController()
    IOLoop.instance().add_callback(callback = controller.wait_for_fixation_2)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
