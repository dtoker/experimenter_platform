from abc import abstractmethod
from tornado import gen
from tornado.ioloop import IOLoop, PeriodicCallback

class DetectionComponent():

    def __init__(self, tobii_controller, adaptation_loop, is_periodic = False, callback_time = 600000, liveWebSocket = None):
        self.tobii_controller  = tobii_controller
        self.adaptation_loop = adaptation_loop
        self.application_state_controller = self.adaptation_loop.app_state_controller
        self.is_periodic = is_periodic
        self.callback_time = callback_time
        self.liveWebSocket = liveWebSocket
        print("querying db")
        self.AOIS = self.application_state_controller.getAoiMapping()
        print("queried db")

    @abstractmethod
    def notify_app_state_controller(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def start(self):
        if (self.is_periodic):
            cb = PeriodicCallback(callback = self.run, callback_time = self.callback_time)
            cb.start()
        else:
            IOLoop.instance().add_callback(callback = self.run)
