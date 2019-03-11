import appdaemon.plugins.hass.hassapi as hass
import datetime
import time


#
# EXAMPLE appdaemon.yaml entry below
#
# helper_outdoors:
#   module: helper_outdoors
#   class: Outdoors
#

class Outdoors(hass.Hass):
    def initialize(self):
        # Rain Check
        self.listen_state(self.sprinkler_rain_check, entity='sensor.dark_sky_precip', new='rain')
        self.listen_state(self.sprinkler_rain_check, entity='sensor.dark_sky_precip', old='rain', duration=86400)
        # Run Sprinkler at 4:15am
        self.run_daily(self.sprinkler_on, datetime.time(4, 15, 0), constrain_days = "mon,thu")

    def sprinkler_rain_check(self, entity, attribute, old, new, kwargs):
        if new == 'rain':
            self.call_service('input_boolean/turn_on', entity_id='input_boolean.trigger_sprinker_rain')
        elif old == 'rain':
            self.call_service('input_boolean/turn_off', entity_id='input_boolean.trigger_sprinker_rain')

    def sprinkler_on(self, kwargs):
        if self.get_state('input_boolean.trigger_sprinker_rain') == 'on':
            return
        self.call_service('switch/turn_on', entity_id='switch.sprinkler')
        self.run_in(self.sprinkler_off, seconds=1200)

    def sprinkler_on(self, kwargs):
        self.call_service('switch/turn_on', entity_id='switch.sprinkler')