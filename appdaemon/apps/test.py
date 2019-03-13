import appdaemon.plugins.hass.hassapi as hass
import appdaemon.plugins.mqtt.mqttapi as mqtt
#
# Hello World App
#
# Args:
#

class Test(hass.Hass):

    def initialize(self):
        self.call_service("mqtt/publish", topic='alexa/tts/alexa/tts/LivingRoom_R', payload='The animals need fresh water today.')