import appdaemon.plugins.hass.hassapi as hass
import appdaemon.plugins.mqtt.mqttapi as mqtt
#
# Hello World App
#
# Args:
#
class Test(hass.Hass):

    def initialize(self):
        #pass
        train_time = [self.get_state(entity="sensor.ptv", attribute="train0_scheduled"), self.get_state(entity="sensor.ptv", attribute="train0_estimated"), self.get_state(entity="sensor.ptv", attribute="train1_scheduled")]
        self.log(self.time())
        self.log(self.parse_time(train_time[0] + ":00").strftime("%-I %-M %p"))