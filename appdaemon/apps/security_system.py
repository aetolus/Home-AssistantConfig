import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta
import time

#
# Hello World App
#
# Args:
#

class SecuritySystem(hass.Hass):

    def initialize(self):
        self.listen_state(self.security_enable, entity='input_select.house', new='Away', duration=5)
        self.listen_state(self.security_disable, entity='input_select.house', new='Home')
        self.listen_state(self.security_alert, entity='binary_sensor.aeotec_motion', old='off', new='on', constrain_input_boolean='input_boolean.security_system_state')
        self.listen_state(self.security_alert, entity='binary_sensor.xiaomi_motion_kitchen', old='off', new='on', constrain_input_boolean='input_boolean.security_system_state')
        self.listen_state(self.security_alert, entity='binary_sensor.xiaomi_motion_upstairs', old='off', new='on', constrain_input_boolean='input_boolean.security_system_state')
        self.listen_state(self.security_alert, entity='binary_sensor.xiaomi_door_front', old='off', new='on', constrain_input_boolean='input_boolean.security_system_state')
        self.listen_state(self.security_alert, entity='binary_sensor.xiaomi_door_sliding', old='off', new='on', constrain_input_boolean='input_boolean.security_system_state')
        self.listen_state(self.security_alert, entity='binary_sensor.xiaomi_door_garage_interior', old='off', new='on', constrain_input_boolean='input_boolean.security_system_state')
        self.listen_state(self.security_alert, entity='binary_sensor.xiaomi_door_garage_exterior', old='off', new='on', constrain_input_boolean='input_boolean.security_system_state')

    def security_enable(self, entity, attribute, old, new, kwargs):
        self.call_service('input_boolean/turn_on', entity_id='input_boolean.speech_notifications')
        self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload="The security system will be armed in 60 seconds.")
        self.run_in(self.security_enable_01, seconds=20)

    def security_enable_01(self, kwargs):
        if self.get_state("input_select.house") != 'Away':
            return
        self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload="40 seconds.")
        self.run_in(self.security_enable_02, seconds=20)

    def security_enable_02(self, kwargs):
        if self.get_state("input_select.house") != 'Away':
            return
        self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload="20 seconds.")
        self.run_in(self.security_enable_03, seconds=10)

    def security_enable_03(self, kwargs):
        if self.get_state("input_select.house") != 'Away':
            return
        self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload="10 seconds.")
        self.run_in(self.security_enable_04, seconds=10)

    def security_enable_04(self, kwargs):
        if self.get_state("input_select.house") != 'Away':
            return
        self.call_service('input_boolean/turn_on', entity_id='input_boolean.security_system_state')
        self.call_service("mqtt/publish", topic="notifications/newmsg/alert", payload="Security system armed.")
        self.call_service('input_boolean/turn_off', entity_id='input_boolean.speech_notifications')

    def security_disable(self, entity, attribute, old, new, kwargs):
        if old == 'Away' or old == 'Vacation':
            self.call_service('input_boolean/turn_off', entity_id='input_boolean.security_system_state')
            self.call_service("mqtt/publish", topic="notifications/newmsg/alert", payload="Security system disarmed.")

    def security_alert(self, entity, attribute, old, new, kwargs):
        if self.get_state("input_select.house") == 'Away':
            self.call_service('input_boolean/turn_on', entity_id='input_boolean.speech_notifications')
            self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload="You have 60 seconds to disable the alarm.")
            self.run_in(self.security_alert_01, seconds=20, pass_entity=entity)

    def security_alert_01(self, kwargs):
        entity = kwargs["pass_entity"]
        if self.get_state("input_select.house") != 'Away':
            return
        self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload="40 seconds.")
        self.run_in(self.security_alert_02, seconds=20, pass_entity=entity)

    def security_alert_02(self, kwargs):
        entity = kwargs["pass_entity"]
        if self.get_state("input_select.house") != 'Away':
            return
        self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload="20 seconds.")
        self.run_in(self.security_alert_03, seconds=10, pass_entity=entity)

    def security_alert_03(self, kwargs):
        entity = kwargs["pass_entity"]
        if self.get_state("input_select.house") != 'Away':
            return
        self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload="10 seconds.")
        self.run_in(self.security_alert_04, seconds=10, pass_entity=entity)

    def security_alert_04(self, kwargs):
        entity = kwargs["pass_entity"]
        if self.get_state("input_select.house") != 'Away':
            return
        self.call_service('input_boolean/turn_off', entity_id='input_boolean.speech_notifications')
        # Send alert notification
        if entity == 'binary_sensor.xiaomi_door_front':
            self.call_service("mqtt/publish", topic="notifications/newmsg/alert", payload='Front Door opened.')
        elif entity == 'binary_sensor.binary_sensor.xiaomi_door_sliding':
            self.call_service("mqtt/publish", topic="notifications/newmsg/alert", payload='Sliding Door opened.')
        elif entity == 'binary_sensor.xiaomi_door_garage_interior':
            self.call_service("mqtt/publish", topic="notifications/newmsg/alert", payload='Interior Garage Door Opened.')
        elif entity == 'binary_sensor.xiaomi_door_garage_exterior':
            self.call_service("mqtt/publish", topic="notifications/newmsg/alert", payload='Exterior Garage Door Opened.')
        elif entity == 'binary_sensor.aeotec_motion':
            self.call_service("mqtt/publish", topic="notifications/newmsg/alert", payload='Motion detected in the Living Room.')
        elif entity == 'binary_sensor.xiaomi_motion_kitchen':
            self.call_service("mqtt/publish", topic="notifications/newmsg/alert", payload='Motion detected in the Kitchen.')
        elif entity == 'binary_sensor.xiaomi_motion_upstairs':
            self.call_service("mqtt/publish", topic="notifications/newmsg/alert", payload='Motion detected in the Staircase.')

        if self.get_state(entity='input_select.house') == 'Vacation':
            return