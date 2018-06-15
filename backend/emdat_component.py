
from detection_component import DetectionComponent


class EMDATComponent(DetectionComponent):


    #TODO: Remove websocket
    def  __init__(self, tobii_controller, is_periodic, callback_time, liveWebSocket):
        #TODO: Specify which features should be calculated
        super().__init__(tobii_controller, is_periodic, callback_time, liveWebSocket)


    def notify_app_state_controller(self):
        self.merge_features()
        """
        Code to send features to AppStateController
        """
    
    def run(self):
        # TODO: Calculate the features
        pass


    def merge_features():
        pass
