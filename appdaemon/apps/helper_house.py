import appdaemon.plugins.hass.hassapi as hass
import datetime
import time


#
# EXAMPLE appdaemon.yaml entry below
#
# helper_house:
#   module: helper_house
#   class: HouseMode
#

class HouseMode(hass.Hass):
    def initialize(self):
        # Run when HomeAssistant restarts
        self.listen_event(self.start_homeassistant, event="plugin_started")
        # Run House State is due to change
        self.run_daily(self.set_mode_time, datetime.time(4, 00, 0))
        self.run_daily(self.set_mode_time, datetime.time(9, 0, 0))
        self.run_daily(self.set_mode_time, datetime.time(22, 0, 0))
        self.run_daily(self.set_mode_time, datetime.time(0, 0, 0))
        self.listen_state(self.set_mode, entity='group.people', new='home', old='not_home')
        self.listen_state(self.set_mode, entity='group.people', new='not_home', old='home')
        self.listen_state(self.set_mode, entity='group.proximity', new='off', old='on')
        self.listen_state(self.set_vacation_mode, entity='input_select.house', new='Away', duration=86400)
        # After the House State changes, run the relevant function
        self.listen_state(self.mode_morning, new='Morning', entity='input_select.house',constrain_input_boolean='input_boolean.guest_mode,off')
        self.listen_state(self.mode_home, new='Home', entity='input_select.house',constrain_input_boolean='input_boolean.guest_mode,off')
        self.listen_state(self.mode_sleep, new='Sleep', entity='input_select.house',constrain_input_boolean='input_boolean.guest_mode,off')
        self.listen_state(self.mode_away, new='Away', entity='input_select.house',constrain_input_boolean='input_boolean.guest_mode,off')
        self.listen_state(self.mode_vacation, new='Vacation', entity='input_select.house',constrain_input_boolean='input_boolean.guest_mode,off')
        # MISC
        self.listen_state(self.proximity, entity='binary_sensor.proximity_kyle', new='on')
        self.listen_state(self.proximity, entity='binary_sensor.proximity_sarah', new='on')
        self.listen_state(self.guest_mode_off, entity='input_boolean.guest_mode', old='on', new='off')
        self.run_daily(self.sleep_warning, datetime.time(21, 30, 0))
        self.run_daily(self.sleep_warning, datetime.time(23, 30, 0))

###
# THIS SECTION CONTAINS ALL THE FUNCTIONS FOR A HOME-ASSISTANT RESTART

    def start_homeassistant(self, event, data, kwargs):
        if self.get_state("input_select.house") != "Initializing":
            return

        self.log("HomeAssistant Restarted")
        self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="HomeAssistant restarted.")
        self.turn_off('group.all_automations')
        self.run_in(self.start_automations_enable, seconds=20)
        self.run_in(self.start_house_state_set, seconds=25)

    def start_automations_enable(self, kwargs):
        self.turn_on('group.all_automations')

    def start_house_state_set(self, kwargs):
        self.utilities = self.get_app('utilities')
        if self.get_state(entity='group.people') == 'not_home':
            self.log("Changing to Away")
            self.select_option('input_select.house', 'Away')
        elif self.now_is_between("04:00:00", "08:59:59"):
            self.log("Changing to Morning")
            self.select_option('input_select.house', 'Morning')
        elif self.utilities.day_of_week() in ['Mon', 'Tue', 'Wed', 'Thu', 'Sun'] and self.now_is_between("09:00:00", "21:59:59"):
            self.log("Changing to Home")
            self.select_option('input_select.house', 'Home')
        elif self.utilities.day_of_week() in ['Mon', 'Tue', 'Wed', 'Thu', 'Sun'] and self.now_is_between("22:00:00", "04:14:59"):
            self.log("Changing to Sleep")
            self.select_option('input_select.house', 'Sleep')
        elif self.utilities.day_of_week() in ['Fri', 'Sat'] and self.now_is_between("09:00:00", "23:59:59"):
            self.log("Changing to Home")
            self.select_option('input_select.house', 'Home')
        elif self.utilities.day_of_week() in ['Fri', 'Sat'] and self.now_is_between("00:00:00", "03:59:59"):
            self.log("Changing to Sleep")
            self.select_option('input_select.house', 'Sleep')
        self.log("HomeAssistant Restart Complete")

# HOME-ASSISTANT RESTART FUNCTIONS END HERE
###
# THIS SECTION CONTAINS ALL THE FUNCTIONS FOR SETTING THE HOUSE MODE

    def set_mode(self, entity, attribute, old, new, kwargs):
        # Change House Mode based on Presence changes
        if new == 'home' and old == 'not_home':
            self.select_option('input_select.house', 'Home')
        elif new == 'not_home' and old == 'home':
            self.select_option('input_select.house', 'Away')
        elif entity == 'group.proximity' and new == 'off' and old == 'on' and self.get_state(entity='group.people') == 'not_home':
            self.select_option('input_select.house', 'Away')

    def set_mode_time(self, kwargs):
        # Change House Mode based on Time
        if self.get_state(entity='group.people') == 'not_home':
            return

        if self.get_state(entity='input_select.house') == 'Vacation':
            return

        self.utilities = self.get_app('utilities')
        if self.now_is_between("04:00:00", "04:01:00"):
            self.log("Changing to Morning")
            self.select_option('input_select.house', 'Morning')
        elif self.now_is_between("09:00:00", "09:01:00"):
            self.log("Changing to Home")
            self.select_option('input_select.house', 'Home')
        elif self.utilities.day_of_week() in ['Mon', 'Tue', 'Wed', 'Thu', 'Sun'] and self.now_is_between("22:00:00", "22:01:00"):
            self.log("Changing to Sleep")
            self.select_option('input_select.house', 'Sleep')
        elif self.utilities.day_of_week() in ['Fri', 'Sat'] and self.now_is_between("00:00:00", "00:01:00"):
            self.log("Changing to Sleep")
            self.select_option('input_select.house', 'Sleep')

    def set_vacation_mode(self, entity, attribute, old, new, kwargs):
        # Change House Mode to Vacation
        self.select_option('input_select.house', 'Vacation')

# SETTING HOUSE MODE FUNCTIONS END HERE
###
# THIS SECTIONS CONTAINS ALL THE FUNCTIONS THAT MAKE RELEVANT CHANGES FOR HOUSE MODE

    def mode_morning(self, entity, attribute, old, new, kwargs):
        # Enabling House Mode Morning
        self.call_service('input_boolean/turn_on', entity_id='input_boolean.speech_notifications')
        self.call_service('media_player/volume_set', entity_id='media_player.livingroom_sonos', volume_level='0.1')

    def mode_home(self, entity, attribute, old, new, kwargs):
        # Enabling House Mode Home
        self.call_service('input_boolean/turn_on', entity_id='input_boolean.speech_notifications')
        self.call_service('media_player/volume_set', entity_id='media_player.livingroom_sonos', volume_level='0.25')

        if old == 'Away' or old == 'Vacation':
            livingroom_lights = self.get_app("lighting")
            livingroom_lights.evening(kwargs)
            if self.get_state(entity='light.living_room') == 'off' and float(self.get_state(entity='sensor.aeotec_zw100_multisensor_6_luminance')) < 11.0:
                self.call_service('light/turn_on', entity_id='light.living_room', profile='standard', brightness_pct='100', transition='10')
            
    def mode_sleep(self, entity, attribute, old, new, kwargs):
        # Enabling House Mode Sleep
        if self.get_state(entity='light.bedroom') == 'on':
            self.call_service('light/turn_on', entity_id=['light.bedroom', 'light.living_room'], color_name='red', brightness_pct='40', transition='270')
        self.call_service("mqtt/publish", topic="livingroom/tv", payload="Off")
        self.call_service('rest_command/sabnzbd_speedlimit_off')
        self.call_service('input_boolean/turn_off', entity_id='input_boolean.speech_notifications')
        self.call_service('media_player/volume_set', entity_id='media_player.livingroom_sonos', volume_level='0.1')

        if self.get_state(entity='binary_sensor.plex_playing') != 'off':
            self.win10_off_handle = self.listen_state(self.win10_off, entity='binary_sensor.plex_playing', new='off', duration=300)
        else:
            self.call_service('switch/turn_off', entity_id='switch.win10')

    def mode_away(self, entity, attribute, old, new, kwargs):
        # Enabling House Mode Away
        self.call_service("mqtt/publish", topic="livingroom/tv", payload="Off")
        self.call_service('input_boolean/turn_off', entity_id='input_boolean.speech_notifications')
        self.call_service('media_player/volume_set', entity_id='media_player.livingroom_sonos', volume_level='0.25')
        self.call_service('rest_command/sabnzbd_speedlimit_off')
        self.call_service('light/turn_off', entity_id=['light.living_room', 'light.bedroom', 'light.upstairs'])
        if self.now_is_between("14:00:00", "16:00:00"):
            return
        elif self.get_state(entity='switch.win10') == 'on':
            self.call_service('shell_command/sleep_win10')

    def mode_vacation(self, entity, attribute, old, new, kwargs):
        # Enabling House Mode Vacation
        self.call_service('homeassistant/turn_off', entity_id='automation.masterbedroom_service_alarm')

# SETTING HOUSE MODE STATES FUNCTIONS END HERE
###
# MISC House Helper Functions

    def proximity(self, entity, attribute, old, new, kwargs):
        if self.get_state(entity='group.people') == 'home':
            if 'kyle' in entity and self.get_state('group.kyle') == 'not_home':
                self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload='Kyle is ' + self.get_state(entity="sensor.travel_kyle", attribute="distance") + ' from home.')
            elif 'sarah' in entity and self.get_state('group.sarah') == 'not_home':
                self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload='Sarah is ' + self.get_state(entity="sensor.travel_sarah", attribute="distance") + ' from home.')
            
# Sleep Warning

    def sleep_warning(self, kwargs):
        self.utilities = self.get_app('utilities')
        if self.utilities.day_of_week() in ['Mon', 'Tue', 'Wed', 'Thu', 'Sun'] and self.now_is_between("21:30:00", "22:00:00"):
            self.call_service('notify/livingroom_tv', message='House entering sleep mode in 30 minutes.')
        elif self.utilities.day_of_week() in ['Fri', 'Sat'] and self.now_is_between("23:30:00", "00:00:00"):
            self.call_service('notify/livingroom_tv', message='House entering sleep mode in 30 minutes.')

# Win10 Off

    def win10_off(self, entity, attribute, old, new, kwargs):
        self.cancel_listen_state(self.win10_off_handle)
        self.call_service('switch/turn_off', entity_id='switch.win10')

# Guest mode turned off
    def guest_mode_off(self, entity, attribute, old, new, kwargs):
        self.call_service('homeassistant/turn_off', entity_id='input_boolean.guest_mode')

