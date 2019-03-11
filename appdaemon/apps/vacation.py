import appdaemon.plugins.hass.hassapi as hass
import datetime
import time
#
# Hello World App
#
# Args:
#

class Vacation(hass.Hass):

    def initialize(self):
        # Lights
        self.run_at_sunrise(self.vacation_lights_00, offset=-3600)
        self.run_at_sunrise(self.vacation_lights_off)
        self.run_at_sunset(self.vacation_lights_01, offset=-1800)
        self.run_daily(self.vacation_lights_03, datetime.time(20, 30, 0))
        self.run_daily(self.vacation_lights_04, datetime.time(21, 0, 0))
        self.run_daily(self.vacation_lights_05, datetime.time(21, 30, 0))
        self.run_daily(self.vacation_lights_off, datetime.time(22, 00, 0))
        # Entertainment
        self.run_daily(self.tv_on, datetime.time(7, 00, 0))
        self.run_daily(self.tv_off, datetime.time(8, 30, 0))
        self.run_daily(self.tv_on, datetime.time(18, 00, 0))
        self.run_daily(self.tv_off, datetime.time(21, 30, 0))

    def vacation_lights_00(self, kwargs):
        self.call_service('light/turn_on', entity_id=['light.bedroom', 'light.living_room'], profile='standard')         

    def vacation_lights_01(self, kwargs):
        self.call_service('light/turn_on', entity_id=['light.bedroom', 'light.living_room'], profile='standard', brightness_pct='50')
        self.run_in(self.vacation_lights_02, seconds=30)

    def vacation_lights_02(self, kwargs):
        self.call_service('light/turn_on', entity_id=['light.bedroom', 'light.living_room'], profile='standard', brightness_pct='100', transition='1800')

    def vacation_lights_03(self, kwargs):
        self.call_service('light/turn_on', entity_id=['light.bedroom', 'light.living_room'], xy_color=['0.4576', '0.4099'], transition='1800')

    def vacation_lights_04(self, kwargs):
        self.call_service('light/turn_on', entity_id=['light.bedroom', 'light.living_room'], xy_color=['0.5609', '0.4042'], transition='1800')

    def vacation_lights_05(self, kwargs):
        self.call_service('light/turn_on', entity_id=['light.bedroom', 'light.living_room'], xy_color=['0.5609', '0.4042'], brightness_pct='40', transition='1800')

    def vacation_lights_off(self, kwargs):
        self.call_service('light/turn_off', entity_id=['light.living_room', 'light.bedroom', 'light.upstairs'])

    def tv_on(self, kwargs):
        self.call_service("mqtt/publish", topic="livingroom/tv", payload="TV")

    def tv_off(self, kwargs):
        self.call_service("mqtt/publish", topic="livingroom/tv", payload="Off")