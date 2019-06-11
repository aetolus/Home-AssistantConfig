import appdaemon.plugins.hass.hassapi as hass
import datetime
from datetime import timedelta
import urllib
import json
#
# Hello World App
#
# Args:
#

class ServiceDownload(hass.Hass):

    def initialize(self):
        if self.now_is_between("14:00:00", "15:59:59") and self.get_state(entity='binary_sensor.connection_win10') == 'off':
            self.run_in(self.download_on, seconds=0)
        self.run_daily(self.download_on, datetime.time(14, 00, 0))
        self.run_daily(self.download_off, datetime.time(16, 00, 0))
        #self.listen_state(self.power_on_pc, entity='sensor.media_player_livingroom_tv_source', new='Plex', constrain_input_select='input_select.house,Morning,Home')
        
    def download_on(self, kwargs):
        self.call_service('homeassistant/turn_on', entity_id='input_boolean.scheduled_download')
        if self.get_state(entity='binary_sensor.connection_win10') == 'off':
            self.call_service('switch/turn_on', entity_id='switch.win10')
        if self.get_state(entity='group.people') == 'not_home':
            self.win10_up_handle = self.listen_state(self.win10_up, entity='binary_sensor.connection_win10', old='off', new='on', duration=180)
    
    def win10_up(self, entity, attribute, old, new, kwargs):
        self.cancel_listen_state(self.win10_up_handle)
        self.log("Reached win10_up & cancelled handle")
        start_date = self.date()
        end_date = start_date + timedelta(days=1)
        sonarr_api = "https://tv.tai.net.au/api/calendar?apikey=25dcdffff367495dba3e20a9e2ccc7b5&start=" + str(start_date) + "&end=" + str(end_date)
        with urllib.request.urlopen(sonarr_api) as url:
            data = json.loads(url.read().decode())
            self.log("Checked data")
            if not data:
                self.log("No shows available for download today... Shutting down")
                self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="No shows available for download today... Shutting down WIN10.")
                self.run_in(self.download_off, seconds=0)
            else:
                self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="Scheduled downloads have started.")
                self.call_service('rest_command/sabnzbd_speedlimit_off')

    def download_off(self, kwargs):
        self.call_service('homeassistant/turn_off', entity_id='input_boolean.scheduled_download')
        #self.call_service('rest_command/sabnzbd_speedlimit_on')
        if self.get_state(entity='group.proximity') == 'on':
            return
        else:
            self.call_service('switch/turn_off', entity_id='switch.win10')

    def power_on_pc(self, entity, attribute, old, new, kwargs):
        if old == 'Plex':
            return
        if self.get_state(entity='binary_sensor.connection_win10') == 'off':
            self.call_service('switch/turn_on', entity_id='switch.win10')
            self.call_service("mqtt/publish", topic='notifications/newmsg', payload='Powering on Plex server now, please wait a moment.')