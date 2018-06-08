

class DetectionComponent():

    def __init__(self, tobii_controller, is_periodic = False, callback_time = 600000, liveWebSocket = None):
        self.tobii_controller  = tobii_controller
        self.is_periodic = is_periodic
        self.callback_time = callback_time
        self.liveWebSocket = liveWebSocket

    @abstractmethod
    def notify_app_state_controller(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def start(self):
        if (self.is_periodic):
            cb = IOLoop.PeriodicCallback(callback = self.run(), self.callback_time)
            cb.start()
        else:
            IOLoop.instance().add_callback(callback = self.run())

    def stop(self):
        pass
