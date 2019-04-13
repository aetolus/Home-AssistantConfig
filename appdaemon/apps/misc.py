import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

class Miscellaneous(hass.Hass):
    def initialize(self):
        self.listen_state(self.internet_down, entity='binary_sensor.connection_internet', old='on', new='off', duration='300')

    def internet_down(self, entity, attribute, old, new, kwargs):
        self.log("Internet connection down")
        if self.get_state('binary_sensor.connection_network') == 'on':
            self.log("Sending reboot command to router")
            self.call_service('shell_command/reboot_router')
            self.log("Waiting for router to go offline")
            self.network_down_handle = self.listen_state(self.network_down, entity='binary_sensor.connection_network', old='on', new='off')

    def network_down(self, entity, attribute, old, new, kwargs):
        self.log("Router is offline")
        self.network_up_handle = self.listen_state(self.network_up, entity='binary_sensor.connection_network', old='off', new='on')
        self.log("Waiting for router to come back online")

    def network_up(self, entity, attribute, old, new, kwargs):
        self.log("Router is online")
        self.internet_up_handle = self.listen_state(self.internet_up, entity='binary_sensor.connection_network', old='off', new='on')
        self.log("Waiting for internet to come back up")

    def internet_up(self, entity, attribute, old, new, kwargs):
        self.call_service("mqtt/publish", topic="notifications/newmsg", payload='Internet connection restored.')
        self.cancel_listen_state(self.network_down_handle)
        self.cancel_listen_state(self.network_up_handle)
        self.cancel_listen_state(self.internet_up_handle)
