import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, time
#
# Hello World App
#
# Args:
#

class Test(hass.Hass):

    def initialize(self):
        #pass
        difference = datetime.now().timestamp() - self.convert_utc(self.entities.binary_sensor.connection_win10.last_changed).timestamp()
        if difference > 300:
            self.log("PC has been powered off for 5 minutes")
        else:
            self.log("Power state changed less than 5 minutes ago")