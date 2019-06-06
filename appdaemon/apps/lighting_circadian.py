import appdaemon.plugins.hass.hassapi as hass
import datetime
import time
#
# Hello World App
#
# Args:
#


class Lighting(hass.Hass):

    def initialize(self):
        # This is to allow time for sun.sun to initialise after a HASS restart
        self.run_in(self.initialise, seconds=30)

    def initialise(self, kwargs):
        # Turn on lights when motion detected in the morning
        self.listen_state(self.morning, entity='binary_sensor.lighting_motion_xiaomi_upstairs', old='off', new='on', constrain_input_select='input_select.house,Morning')
        # Turn lights on 90 minutes before sunset in the evening
        self.run_at_sunset(self.evening, offset=-5400, constrain_input_select='input_select.house,Home')
        # Turn lights off 15 minutes after sleep mode
        self.listen_state(self.sleep, entity='input_select.house', new='Sleep', duration=900)

    def morning(self, entity, attribute, old, new, kwargs):
        self.turn_on('switch.circadian_lighting_circadian_lighting')
        self.call_service('light/turn_on', entity_id='light.living_room')

    def evening(self, kwargs):
        if self.time() > self.parse_time("sunset - 00:90:00"):
            # If arrived home past 90 minutes to sunset, set lights to 100%
            self.log("Arrived home past 90 minutes to sunset, set lights to 100%")
            self.call_service('light/turn_on', entity_id='light.living_room')

    def sleep(self, entity, attribute, old, new, kwargs):
        self.call_service('light/turn_off', entity_id='light.living_room')


