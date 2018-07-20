from detection_component import DetectionComponent
from tornado import gen
import math
from utils import *
import geometry
import time
from ... import params

class MLComponent(DetectionComponent):

    def __init__(self, tobii_controller, app_state_control, callback_time):
        DetectionComponent.__init__(self, tobii_controller, app_state_control, is_periodic = True, callback_time = callback_time)
        self.predicted_features = {}

    def run():
        ## Do something
        self.notify_app_state_controller()
        pass

    def notify_app_state_controller(self):
        pass
