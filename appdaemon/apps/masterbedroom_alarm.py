import appdaemon.plugins.hass.hassapi as hass
import datetime
import random

#
# masterbedroom_alarm:
#   module: masterbedroom_alarm
#   class: MasterBedroomAlarm
#

class MasterBedroomAlarm(hass.Hass):
    def initialize(self):
        time = datetime.time(0, 0, 0)
        self.run_minutely(self.check_alarm, time)

    def check_alarm(self, kwargs):
        current_date = self.date()
        current_time = self.time()
        current_time = current_time.strftime('%H:%M')
        alarm_lighting_time = self.get_state(entity = 'sensor.alarm_time') + ':00'
        alarm_lighting_time = self.parse_time(alarm_lighting_time)
        alarm_lighting_time = datetime.datetime.combine(current_date, alarm_lighting_time)
        alarm_lighting_time = alarm_lighting_time - datetime.timedelta(minutes=30)
        alarm_lighting_time = alarm_lighting_time.strftime('%H:%M')
        alarm_audio_time = self.get_state(entity = 'sensor.alarm_time')
        if alarm_lighting_time == current_time:
            self.log("Triggering sunrise simulation")
            self.run_in(self.fire_lighting, seconds=0)
        elif alarm_audio_time == current_time:
            self.log("Triggering audio")
            self.run_in(self.fire_audio, seconds=0)
        else:
            return

    def fire_lighting(self, kwargs):
        if self.get_state(entity = 'person.kyle') == 'not_home':
            self.log("Sunrise simulation scheduled, but Kyle isn't home")
        else:
            self.turn_off('switch.circadian_lighting_circadian_lighting')
            self.call_service('homeassistant/turn_on', entity_id='input_boolean.trigger_masterbedroom_service_alarm_on')
            self.call_service('light/turn_on', entity_id='light.master_bedroom_lamp_1_kyle', color_name='red', brightness_pct='1')
            self.run_in(self.fire_alarm_lighting_01, seconds=5)

    def fire_alarm_lighting_01(self, kwargs):
        if self.get_state(entity='input_boolean.trigger_masterbedroom_service_alarm_on') == 'off':
            return
        self.call_service('light/turn_on', entity_id='light.master_bedroom_lamp_1_kyle', color_temp=self.get_state(entity='sensor.circadian_values', attribute='colortemp'), brightness_pct=50, transition=895)
        self.run_in(self.fire_alarm_lighting_02, seconds=895)

    def fire_alarm_lighting_02(self, kwargs):
        if self.get_state(entity='input_boolean.trigger_masterbedroom_service_alarm_on') == 'off':
            return
        self.call_service('light/turn_on', entity_id='light.master_bedroom_lamp_1_kyle', color_temp=self.get_state(entity='sensor.circadian_values', attribute='colortemp'), brightness_pct=100, transition=900)

    def fire_audio(self, kwargs):
        if self.get_state(entity = 'person.kyle') == 'not_home':
            self.log("Audio scheduled, but Kyle isn't home")
        else:
            self.turn_on('switch.circadian_lighting_circadian_lighting')
            self.call_service('homeassistant/turn_on', entity_id='input_boolean.trigger_masterbedroom_service_alarm_on')
            self.run_in(self.fire_alarm_music_01, seconds=0)

    def fire_alarm_music_01(self, kwargs):
        AlarmMedia = ["EasyStreet.mp3", "RiseandShine.mp3", "9to5.mp3"]
        media_url = 'https://home.tai.net.au/local/soundfiles/Alarm/' + (random.choice(AlarmMedia))
        self.log(media_url)
        self.call_service('homeassistant/turn_on', entity_id='input_boolean.trigger_masterbedroom_service_alarm_on')
        self.call_service('media_player/turn_on', entity_id='media_player.chromecast_masterbedroom')
        self.call_service('media_player/volume_set', entity_id='media_player.chromecast_masterbedroom', volume_level='0.075')
        self.call_service('media_player/play_media', entity_id='media_player.chromecast_masterbedroom', media_content_id=media_url, media_content_type='audio/mp4')
        self.run_in(self.fire_alarm_music_02, seconds=10)

    def fire_alarm_music_02(self, kwargs):
        self.call_service('media_player/volume_set', entity_id='media_player.chromecast_masterbedroom', volume_level='0.0875')
        self.run_in(self.fire_alarm_music_03, seconds=10)

    def fire_alarm_music_03(self, kwargs):
        self.call_service('media_player/volume_set', entity_id='media_player.chromecast_masterbedroom', volume_level='0.1')
        self.run_in(self.fire_alarm_music_04, seconds=10)

    def fire_alarm_music_04(self, kwargs):
        self.call_service('media_player/volume_set', entity_id='media_player.chromecast_masterbedroom', volume_level='0.1125')
        self.run_in(self.fire_alarm_music_05, seconds=10)

    def fire_alarm_music_05(self, kwargs):
        self.call_service('media_player/volume_set', entity_id='media_player.chromecast_masterbedroom', volume_level='0.1375')
        self.run_in(self.fire_alarm_music_06, seconds=10)

    def fire_alarm_music_06(self, kwargs):
        self.call_service('media_player/volume_set', entity_id='media_player.chromecast_masterbedroom', volume_level='0.15')
        self.run_in(self.fire_alarm_music_07, seconds=10)

    def fire_alarm_music_07(self, kwargs):
        self.call_service('media_player/volume_set', entity_id='media_player.chromecast_masterbedroom', volume_level='0.1625')
        self.run_in(self.fire_alarm_music_08, seconds=10)

    def fire_alarm_music_08(self, kwargs):
        self.call_service('media_player/volume_set', entity_id='media_player.chromecast_masterbedroom', volume_level='0.175')