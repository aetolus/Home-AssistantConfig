import appdaemon.plugins.hass.hassapi as hass
import datetime
import localvars

#
# EXAMPLE appdaemon.yaml entry below
#
# notifications:
#   module: notifications
#   class: notifications
#

class Notifications(hass.Hass):
    def initialize(self):
        # Morning Update
        self.listen_state(self.morning_update_enable, entity='input_select.house', old='Sleep', new='Morning')
        self.listen_state(self.morning_update_motion_upstairs, entity='binary_sensor.xiaomi_motion_upstairs', old='off', new='on', constrain_input_select='input_select.house,Morning')
        self.listen_state(self.morning_update_read, entity='binary_sensor.xiaomi_motion_kitchen', old='off', new='on', constrain_input_select='input_select.house,Morning')
        self.listen_state(self.morning_update_read, entity='binary_sensor.aeotec_motion', old='off', new='on', constrain_input_select='input_select.house,Morning')
        # HomeAssistant Update Released
        self.listen_state(self.ha_updates, entity='sensor.latest_ha_version')
        # Train Travel
        self.listen_state(self.train_travel, entity='sensor.travel_train_craigieburn')
        # Welcome Home
        self.listen_state(self.welcome_home_start, entity='input_select.house', old='Away', new='Home')
        # Moe Travel
        self.listen_state(self.travel_alert_moe, entity='sensor.acurus_to_moe')
        self.listen_state(self.traintest, entity='sensor.ptv')

    # Read Morning Update
    def morning_update_enable(self, entity, attribute, old, new, kwargs):
        self.log("Reached morning_update_enable, localvars.Notify_Morning_Update is: " + str(localvars.Notify_Morning_Update))
        if localvars.Notify_Morning_Update == 0:
            self.log("Morning update enabled. Waiting for motion upstairs")
            localvars.Notify_Morning_Update = 1

    def morning_update_motion_upstairs(self, entity, attribute, old, new, kwargs):
        self.log("Reached morning_update_motion_upstairs, localvars.Notify_Morning_Update is: " + str(localvars.Notify_Morning_Update))
        if localvars.Notify_Morning_Update == 1:
            self.log("Motion detected upstairs. Waiting for motion downstairs.")
            localvars.Notify_Morning_Update = 2

    def morning_update_read(self, entity, attribute, old, new, kwargs):
        self.log("reached morning_update_read, localvars.Notify_Morning_Update is: " + str(localvars.Notify_Morning_Update))
        if localvars.Notify_Morning_Update != 2:
            return
        self.log("Motion detected by " + entity + ". Reading morning update.")
        localvars.Notify_Morning_Update = 0
        self.utilities = self.get_app('utilities')
        if self.utilities.is_weekday() == True:
            self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload='call: weekday_alarm')
        else:
            self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload='call: weekend_alarm')

    # Notify about new HomeAssistant Updates
    def ha_updates(self, entity, attribute, old, new, kwargs):
        if 'b' not in self.get_state('sensor.latest_ha_version'):
            self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="Home Assistant " + self.get_state('sensor.latest_ha_version') + " is now available.")

    # Notify if delays on the train station
    def train_travel(self, entity, attribute, old, new, kwargs):
        self.utilities = self.get_app('utilities')
        if self.utilities.is_weekday() == False:
            return

        if self.now_is_between("04:30:00", "08:00:00") and self.get_state('binary_sensor.proximity_kyle') == 'on':
            if self.get_state('group.kyle') == 'home':
                topic = 'notifications/newmsg/tts'
            else:
                topic = 'notifications/newmsg/telegram'
            if 'Alert' in new:
                self.call_service("mqtt/publish", topic=topic, payload="There is currently a " + self.get_state('sensor.travel_train_craigieburn') + " on the Craigieburn line.")
            elif 'Delays' in new:
                self.call_service("mqtt/publish", topic=topic, payload="There are currently " + self.get_state('sensor.travel_train_craigieburn') + " on the Craigieburn line.")
            elif new == "Good service":
                self.call_service("mqtt/publish", topic=topic, payload="Good service has been restored on the Cragieburn line.")

        if self.now_is_between("14:00:00", "17:00:00") and self.get_state('binary_sensor.proximity_kyle') == 'off':
            if 'Alert' in new:
                self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="There is currently a " + self.get_state('sensor.travel_train_craigieburn') + " on the Craigieburn line.")
            elif 'Delays' in new:
                self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="There are currently " + self.get_state('sensor.travel_train_craigieburn') + " on the Craigieburn line.")
            elif new == "Good service":
                self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="Good service has been restored on the Cragieburn line.")

    # Welcome Home
    def welcome_home_start(self, entity, attribute, old, new, kwargs):
        self.log("welcome_home_start")
        # Cancel any previous open handles
        try:
            self.cancel_listen_state(self.door_opened_handle)
        except:
            self.log('self.door_opened_handle does not exist, no need to cancel.')
        # Convert times to same format for comparison
        sep = '.'
        door_last_opened = self.get_state(entity='binary_sensor.xiaomi_door_front', attribute='last_changed')
        door_last_opened = door_last_opened.split(sep, 1)[0]
        door_last_opened = datetime.datetime.strptime(door_last_opened, '%Y-%m-%dT%H:%M:%S')
        starttime = datetime.datetime.utcnow().isoformat()
        starttime = starttime.split(sep, 1)[0]
        starttime = datetime.datetime.strptime(starttime, '%Y-%m-%dT%H:%M:%S')
        difftime = (int(abs(door_last_opened - starttime).total_seconds()))
        # If door was last opened less than 5 minutes ago, cancel
        if difftime < 300:
            return
        # Otherwise wait for door to open
        self.door_opened_handle = self.listen_state(self.welcome_home_door_opened, entity='binary_sensor.xiaomi_door_front', new='on')

    def welcome_home_door_opened(self, entity, attribute, old, new, kwargs):
        self.log("welcome_home_door_opened")
        day = datetime.datetime.today().weekday()
        try:
            self.cancel_listen_state(self.door_opened_handle)
            self.log('cancelled self.door_opened_handle')
        except:
            self.log('self.door_opened_handle does not exist')
        self.log('continued after exception')
        if self.get_state("group.announcements") == 'on' or day in [0, 2, 4] and self.now_is_between("14:00:00", "19:00:00"):
            self.call_service("mqtt/publish", topic='notifications/newmsg/tts', payload='call: welcome_home')
            if self.get_state("binary_sensor.xiaomi_door_garage_exterior") == 'on':
                self.call_service("mqtt/publish", topic='notifications/newmsg/tts', payload='call: garage_door_open')
            if self.get_state("input_boolean.call_dishwasher") == 'on':
                self.call_service("mqtt/publish", topic='notifications/newmsg/tts', payload='call: dishwasher_ready')
            if self.get_state("input_boolean.call_washing") == 'on':
                self.call_service("mqtt/publish", topic='notifications/newmsg/tts', payload='call: washing_ready')
            if day in [0, 2, 4] and self.now_is_between("14:00:00", "19:00:00"):
                self.call_service("mqtt/publish", topic='notifications/newmsg/tts', payload='The animals need fresh water today.')
            self.turn_off("group.announcements")

    def travel_alert_moe(self, entity, attribute, old, new, kwargs):
        if int(new) >= 105 and int(new) < 120 and int(old) < 105:
            self.call_service("mqtt/publish", topic='notifications/newmsg/telegram', payload='Travel time from Acurus to Moe is over 1:45')
        elif int(new) >= 120 and int(old) < 120:
            self.call_service("mqtt/publish", topic='notifications/newmsg/telegram', payload='Travel time from Acurus to Moe is over 2 hours')
        elif int(new) < 105 and int(old) >= 105:
            self.call_service("mqtt/publish", topic='notifications/newmsg/telegram', payload='Travel time from Acurus to Moe back below 1:45')

    def traintest(self, entity, attribute, old, new, kwargs):
        if old == 'Unknown' and new != 'Unknown':
            self.call_service("mqtt/publish", topic='notifications/newmsg/telegram', payload="The next train is scheduled to depart Oak Park at {}".format(new))

            
