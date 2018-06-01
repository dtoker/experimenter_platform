

class DetectionComponent():

    def __init__(self, controller, is_periodic, callback_time):
        self.controller  = controller
        self.is_periodic = is_periodic
        self.callback_time = callback_time

    @abstractmethod
    def notify_app_state_controller(self):
        print('stub')

    @abstractmethod
    def run(self):
        print('stub')

    def start(self):
        if (self.is_periodic):
            cb = IOLoop.PeriodicCallback(callback = self.run(), self.callback_time)
            cb.start()
        else:
            IOLoop.instance().add_callback(callback = self.run())
