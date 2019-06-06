import appdaemon.plugins.hass.hassapi as hass
import time

#
# Hello World App
#
# Args:
#


class HueDimmerSwitches(hass.Hass):

    def initialize(self):
        self.listen_state(self.hue_dimmer_livingroom, entity='sensor.hue_dimmer_livingroom')
        self.listen_state(self.hue_dimmer_bedroom_wall, entity='sensor.hue_dimmer_bedroom_wall')
        self.listen_state(self.hue_dimmer_bedroom_bedside, entity='sensor.hue_dimmer_bedroom_bedside')

    def hue_dimmer_livingroom(self, entity, attribute, old, new, kwargs):
        if new == '4_hold_up':
            self.select_option('input_select.house', 'Sleep')

    def hue_dimmer_bedroom_wall(self, entity, attribute, old, new, kwargs):
        if new == '4_hold_up':
            self.select_option('input_select.house', 'Sleep')

    def hue_dimmer_bedroom_bedside(self, entity, attribute, old, new, kwargs):
        if new == '4_hold_up':
            self.select_option('input_select.house', 'Sleep')
