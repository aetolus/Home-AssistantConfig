import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Hello World App
#
# Args:
#

class Presence(hass.Hass):

    def initialize(self):
        time = datetime.time(0, 0, 0)
        self.run_minutely(self.check_lastupdated, time)

    def check_lastupdated(self, kwargs):
        kyle_lastupdated = datetime.datetime.now().timestamp() - self.convert_utc(self.entities.device_tracker.kyle_phone.last_updated).timestamp()
        sarah_lastupdated = datetime.datetime.now().timestamp() - self.convert_utc(self.entities.device_tracker.sarah_phone.last_updated).timestamp()
        if kyle_lastupdated > 5400 and 'device_tracker.kyle_phone' in self.get_state(entity="group.kyle", attribute='entity_id'):
            #self.call_service("mqtt/publish", topic='notifications/newmsg/telegram', payload="Removing device_tracker.kyle_phone from group.kyle")
            self.call_service("group/set", object_id="kyle", entities="device_tracker.kyle_phone_bt, device_tracker.kyle_phone_wifi")
        elif kyle_lastupdated < 5400 and 'device_tracker.kyle_phone' not in self.get_state(entity="group.kyle", attribute='entity_id'):
            #self.call_service("mqtt/publish", topic='notifications/newmsg/telegram', payload="Adding device_tracker.kyle_phone to group.kyle")
            self.call_service("group/set", object_id="kyle", entities="device_tracker.kyle_phone, device_tracker.kyle_phone_bt, device_tracker.kyle_phone_wifi")

        if sarah_lastupdated > 5400 and 'device_tracker.sarah_phone' in self.get_state(entity="group.sarah", attribute='entity_id'):
            self.call_service("mqtt/publish", topic='notifications/newmsg/telegram', payload="Removing device_tracker.sarah_phone from group.sarah")
            self.call_service("group/set", object_id="sarah", entities="device_tracker.sarah_phone_bt, device_tracker.sarah_phone_wifi")
        elif sarah_lastupdated < 5400 and 'device_tracker.sarah_phone' not in self.get_state(entity="group.sarah", attribute='entity_id'):
            self.call_service("mqtt/publish", topic='notifications/newmsg/telegram', payload="Adding device_tracker.sarah_phone to group.sarah")
            self.call_service("group/set", object_id="sarah", entities="device_tracker.sarah_phone, device_tracker.sarah_phone_bt, device_tracker.sarah_phone_wifi")