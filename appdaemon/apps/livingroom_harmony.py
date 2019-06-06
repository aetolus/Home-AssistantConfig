import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

#
# EXAMPLE appdaemon.yaml entry below
#
# livingroom_climate:
#   module: livingroom_harmony
#   class: LivingRoomHarmony
#

class LivingRoomHarmony(hass.Hass):
    lg_apps = ['Netflix', 'Plex', 'YouTube']

    def initialize(self):
        self.listen_event(self.livingroom_harmony_start, event='MQTT_MESSAGE', namespace='mqtt', topic = 'livingroom/tv')
        self.listen_state(self.livingroom_tv_volume, entity='media_player.livingroom_tv', attribute='source')
        self.listen_state(self.livingroom_tv_volume, entity='media_player.livingroom_sonos', attribute='media_artist', new='TV')
        self.listen_state(self.livingroom_sonos_music, entity='media_player.livingroom_sonos', attribute='media_artist')

    def livingroom_harmony_start(self, event, event_data, kwargs):
        if event_data['payload'] == 'Off':
            self.call_service('remote/turn_on', entity_id='remote.livingroom', activity='PowerOff')
        elif event_data['payload'] == 'TV' and self.get_state('media_player.livingroom_tv') != 'off':
            self.call_service('media_player/select_source', entity_id='media_player.livingroom_tv', source='Live TV')
        else: 
            self.log("Reached livingroom_harmony_start: " + event_data['payload'])
            if self.get_state('media_player.livingroom_tv') == 'off':
                self.log("Setting volume to 0.0")
                self.call_service('media_player/volume_set', entity_id='media_player.livingroom_sonos', volume_level=0.0)
                self.call_service('remote/turn_on', entity_id='remote.livingroom', activity='TV')
            self.run_in(self.livingroom_harmony_apps, seconds=0, new=event_data['payload'])

    def livingroom_harmony_apps(self, kwargs):
        self.log("Reached livingroom_harmony_apps")
        livingroom_tv = self.get_state("media_player.livingroom_tv")
        if kwargs["new"] == "TV":
            app = "Live TV"
        else:
            app = kwargs["new"]
        self.log("app is: " + app)
        if livingroom_tv == 'off':
            self.run_in(self.waittime, seconds=0, app=app, checks=0)
        elif livingroom_tv == 'playing':
            self.run_in(self.livingroom_harmony_apps_connected, seconds=0, app=app)
        if app == 'Plex' and self.get_state("binary_sensor.connection_win10") == 'off':
            self.turn_on("switch.win10")


    def waittime(self, kwargs):
        checks = kwargs["checks"]
        app = kwargs["app"]
        self.log(checks)
        if self.get_state("media_player.livingroom_tv") == 'playing':
            self.run_in(self.livingroom_harmony_apps_connected, seconds=0, app=app)
        elif checks < 12:
            if checks == 0 or checks == 4 or checks == 8:
                self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload="call: tv_waiting_wifi")
            checks = checks + 1
            self.run_in(self.waittime, seconds=5, app=app, checks=checks)
        elif checks >= 12:
            self.log("TV not on after 3 loops, sent PowerOn")
            self.call_service("mqtt/publish", topic="notifications/newmsg/tts", payload="TV not connected after 60 seconds, sent Power On")
            self.call_service('remote/send_command', entity_id='remote.livingroom', command='PowerOn', device='39894601')
            checks = 0
            self.run_in(self.waittime, seconds=20, app=app, checks=checks)
            
    def livingroom_harmony_apps_connected(self, kwargs):
        app = kwargs["app"]
        self.log("TV connected to Network")
        self.log("Changing LG TV Source to {}".format(app))
        self.call_service('media_player/select_source', entity_id='media_player.livingroom_tv', source=app)
        if app == "Live TV":
            self.livingroom_harmony_apps_connected_livetv_handle = self.listen_state(self.livingroom_harmony_apps_connected_livetv, entity='media_player.livingroom_tv', attribute="source", new='Live TV')

    def livingroom_harmony_apps_connected_livetv(self, entity, attribute, old, new, kwargs):
        self.log("Reached connect_livetv")
        self.cancel_listen_state(self.livingroom_harmony_apps_connected_livetv_handle)
        self.call_service('media_player/select_source', entity_id='media_player.livingroom_sonos', source='TV')
        self.call_service('media_player/play_media', entity_id='media_player.livingroom_tv', media_content_id='70', media_content_type="channel")

    def livingroom_tv_volume(self, entity, attribute, old, new, kwargs):
        if new == old or not new or not old:         
            return
        if entity == 'media_player.livingroom_sonos' and new == 'TV':
            self.call_service('media_player/volume_set', entity_id='media_player.livingroom_sonos', volume_level=0.2)
        elif new == 'Live TV':
            self.call_service('media_player/volume_set', entity_id='media_player.livingroom_sonos', volume_level=0.2)
        elif new == 'Netflix':
            self.call_service('media_player/volume_set', entity_id='media_player.livingroom_sonos', volume_level=0.2)
        elif new == 'Plex':
            self.call_service('media_player/volume_set', entity_id='media_player.livingroom_sonos', volume_level=0.3)
            if self.get_state("binary_sensor.connection_win10") == 'off':
                self.turn_on("switch.win10")

    def livingroom_sonos_music(self, entity, attribute, old, new, kwargs):
        if new == 'TV' or new == 'Joanna' or old == new or not new:
            return
        self.log(entity + " changed from " + old + " to " + new + ".")
        if self.entities.media_player.livingroom_tv.state == 'playing':
            self.log("Turning off TV.")
            self.call_service('media_player/select_source', entity_id='media_player.livingroom_tv', source='HDMI1')
            self.turn_off('media_player.livingroom_tv')
        self.log("Changing source to Music.")
        self.call_service('remote/turn_on', entity_id='remote.livingroom', activity='Music')