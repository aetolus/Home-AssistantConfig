import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

class Miscellaneous(hass.Hass):
    def initialize(self):
        self.listen_state(self.internet_down, entity='binary_sensor.connection_internet', old='on', new='off', duration='300')

    def internet_down(self, entity, attribute, old, new, kwargs):
        self.log("Internet connection down.")
        if self.get_state('binary_sensor.connection_network') == 'on':
            self.log("Sending reboot command to router")
            self.call_service('shell_command/reboot_router')
            while self.get_state('binary_sensor.connection_network') == 'on':
                self.log("Waiting for router to reboot")
                time.sleep(5)
            while self.get_state('binary_sensor.connection_network') == 'off':
                self.log("Waiting for router to come back online")
                time.sleep(5)
            if self.get_state('input_select.house') == 'Away' or self.get_state('input_select.house') == 'Sleep':
                if self.get_state('binary_sensor.internet_connection' == 'off'):
                    while self.get_state('binary_sensor.internet_connection') == 'off':
                        time.sleep(600)
                        if self.get_state('binary_sensor.internet_connection' == 'off'):
                            self.call_service('shell_command/reboot_router')
                            while self.get_state('binary_sensor.connection_network') == 'on':
                                time.sleep(1)
                            while self.get_state('binary_sensor.connection_network') == 'off':
                                time.sleep(1)
            while self.get_state('binary_sensor.internet_connection') == 'off':
                self.log("Waiting for internet connection to come back up")
                time.sleep(5)
            self.call_service("mqtt/publish", topic="notifications/newmsg", payload='Internet connection restored.')
