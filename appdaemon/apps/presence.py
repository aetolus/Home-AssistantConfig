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
        self.call_service("mqtt/publish", topic='owntracks/sarah/phone', payload='{"id":"39b8bbd6-ba0c-4b96-ac26-f74decc822c0","name":"Family","color":"7f26c2","type":"basic","createdAt":"1531564114","memberCount":"1","unreadMessages":"0","unreadNotifications":"0","features":{"ownerId":null,"skuId":null,"premium":"0","locationUpdatesLeft":0,"priceMonth":"0","priceYear":"0","skuTier":null},"members":[{"features":{"device":"1","smartphone":"1","nonSmartphoneLocating":"0","geofencing":"1","shareLocation":"1","shareOffTimestamp":null,"disconnected":"0","pendingInvite":"0","mapDisplay":"0"},"issues":{"disconnected":"0","type":null,"status":null,"title":null,"dialog":null,"action":null,"troubleshooting":"0"},"location":{"latitude":"0","longitude":"0","accuracy":"0","startTimestamp":1559030419,"endTimestamp":"1559030419","since":1559030419,"timestamp":"1559030419","name":null,"placeType":null,"source":null,"sourceId":null,"address1":null,"address2":"","shortAddress":"","inTransit":"0","tripId":null,"driveSDKStatus":null,"battery":"27.000001907349","charge":"1","wifiState":"1","speed":4.130000114440900205181605997495353221893310546875,"isDriving":"0","userActivity":null},"communications":[{"channel":"Voice","value":"+61418844849","type":"Home"},{"channel":"Email","value":"sarahkate.hayes@gmail.com","type":null}],"medical":null,"relation":null,"createdAt":"1531564114","activity":null,"id":"8d81e997-af42-4bf0-9d75-ba1ef143d5c9","firstName":"Sarah","lastName":"","loginEmail":"sarahkate.hayes@gmail.com","loginPhone":"+6112345678","avatar":null,"isAdmin":"1","pinNumber":null}]}', retain='true')

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
            self.call_service("group/set", object_id="sarah", entities="device_tracker.sarah_phone_bt, device_tracker.sarah_phone_wifi, device_tracker.supre_phone_bt, device_tracker.supre_phone_wifi")
        elif sarah_lastupdated < 5400 and 'device_tracker.sarah_phone' not in self.get_state(entity="group.sarah", attribute='entity_id'):
            self.call_service("mqtt/publish", topic='notifications/newmsg/telegram', payload="Adding device_tracker.sarah_phone to group.sarah")
            self.call_service("group/set", object_id="sarah", entities="device_tracker.sarah_phone, device_tracker.sarah_phone_bt, device_tracker.sarah_phone_wifi, device_tracker.supre_phone_bt, device_tracker.supre_phone_wifi")