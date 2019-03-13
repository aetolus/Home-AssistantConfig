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
        if new == '1_click_up':
            self.call_service('light/turn_on', entity_id='light.living_room', profile='standard', brightness_pct='100')
        elif new == '4_click_up':
            self.call_service('light/turn_off', entity_id='light.living_room')
        elif new == '4_hold_up':
            self.select_option('input_select.house', 'Sleep')

    def hue_dimmer_bedroom_wall(self, entity, attribute, old, new, kwargs):
        if new == '1_click_up':
            if self.get_state(entity='sun.sun') == 'below_horizon':
                self.call_service('light/turn_on', entity_id='light.bedroom', profile='relax')
            else:
                self.call_service('light/turn_on', entity_id='light.bedroom', profile='standard', brightness_pct='100')
        elif new == '4_click_up':
            self.call_service('light/turn_off', entity_id='light.bedroom')
        elif new == '4_hold_up':
            self.select_option('input_select.house', 'Sleep')

    def hue_dimmer_bedroom_bedside(self, entity, attribute, old, new, kwargs):
        if new == '1_click_up':
            if self.get_state(entity='sun.sun') == 'below_horizon':
                self.call_service('light/turn_on', entity_id='light.bedroom', profile='relax')
            else:
                self.call_service('light/turn_on', entity_id='light.bedroom', profile='standard', brightness_pct='100')
        elif new == '1_hold_up':
            self.call_service('light/turn_on', entity_id='light.bedroom', profile='reading')
        elif new == '3_hold_up':
            self.call_service('light/turn_on', entity_id='light.bedroom', color_name='red', brightness_pct='40', transition='150')
            time.sleep(300)
            self.call_service('light/turn_off', entity_id='light.bedroom', transition='150')   
        elif new == '4_click_up':
            self.call_service('light/turn_off', entity_id='light.bedroom')
        elif new == '4_hold_up':
            self.select_option('input_select.house', 'Sleep')
