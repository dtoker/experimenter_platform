
from eye_tracker import TobiiController

class ExperimenterPlatform():


    def __init__(self):
        self.eb = TobiiController() #TobiiController is the main class of eye_tracker.py
        self.eb.liveWebSocket.add(self)
        self.eb.waitForFindEyeTracker() #wait 'till it's found
        print "eb created"
        print self.eb.eyetrackers #we found one!
        self.eb.activate(self.eb.eyetrackers.keys()[0]) #activate
        self.eb.startTracking()
        print "tracking started"

        print('hi')

    def initialize_platform(self):
        controller = DummyController()
        IOLoop.instance().add_callback(callback = controller.wait_for_fixation)
        IOLoop.instance().add_callback(callback = self.eb.onlinefix)
