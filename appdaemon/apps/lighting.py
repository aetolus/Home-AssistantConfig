import appdaemon.plugins.hass.hassapi as hass
import datetime
import time
#
# Hello World App
#
# Args:
#


class Lighting(hass.Hass):

    def initialize(self):
        # This is to allow time for sun.sun to initialise after a HASS restart
        self.run_in(self.initialise, seconds=15)

    def initialise(self, kwargs):
        # Adjust for motion timers
        # Wait for movement to turn lights on in the morning3
        self.listen_state(self.morning, entity='binary_sensor.lighting_motion_xiaomi_upstairs', old='off', new='on', constrain_input_select='input_select.house,Morning')
        self.listen_state(self.morning, entity='binary_sensor.lighting_motion_downstairs', old='off', new='on', constrain_input_select='input_select.house,Morning')
        self.listen_state(self.morning_off, entity='binary_sensor.lighting_motion_downstairs', new='off', constrain_input_select='input_select.house,Morning')
        # Turn lights off one hour after sunrise in the morning
        self.run_at_sunrise(self.morning_off_sunrise, offset=3600, constrain_input_select='input_select.house,Morning')
        # Fade lights in 90 minutes before sunset in the evening
        self.run_at_sunset(self.evening, offset=-5400, constrain_input_select='input_select.house,Home')
        # Start flux transition at sunset in the evening
        self.run_at_sunset(self.evening_flux_00, constrain_input_select='input_select.house,Home')
        # Dim lights before bed
        self.run_daily(self.evening_flux_02, datetime.time(21, 00, 0))
        self.run_daily(self.evening_flux_02, datetime.time(23, 00, 0))
        # Final light changes when house goes into Sleep mode
        self.listen_state(self.evening_sleep_00, new='Sleep', entity='input_select.house')
        # Nightlight
        self.listen_state(self.nightlight_upstairs_on, entity='binary_sensor.lighting_motion_xiaomi_upstairs', old='off', new='on', constrain_input_select='input_select.house,Sleep')
        self.listen_state(self.nightlight_downstairs_on, entity='binary_sensor.xiaomi_motion_kitchen', old='off', new='on', constrain_input_select='input_select.house,Sleep')
        self.listen_state(self.nightlight_off, entity='binary_sensor.lighting_motion_xiaomi_upstairs', new='off', constrain_input_select='input_select.house,Sleep')
        self.listen_state(self.nightlight_off, entity='binary_sensor.lighting_motion_downstairs', new='off', constrain_input_select='input_select.house,Sleep')

    def morning(self, entity, attribute, old, new, kwargs):
        sunrise_offset = self.parse_time("sunrise + 01:00:00")
        if self.time() < sunrise_offset and self.get_state('light.living_room') == 'off':
            self.log("Running first morning function")
            if entity == 'binary_sensor.lighting_motion_xiaomi_upstairs':
                self.call_service('light/turn_on', entity_id='light.living_room', profile='nightlight', brightness_pct='40')
                self.morning_00_handle = self.listen_state(self.morning_00_run_in, entity='binary_sensor.lighting_motion_downstairs', old='off', new='on', constrain_input_select='input_select.house,Morning')
            elif entity == 'binary_sensor.lighting_motion_downstairs':
                self.call_service('light/turn_on', entity_id='light.living_room', profile='nightlight', brightness_pct='40')
                self.run_in(self.morning_00, seconds=3)

    def morning_00_run_in(self, entity, attribute, old, new, kwargs):
        self.cancel_listen_state(self.morning_00_handle)
        self.run_in(self.morning_00, seconds=0)

    def morning_00(self, kwargs):
        self.call_service('light/turn_on', entity_id='light.living_room', kelvin=2200, brightness_pct='100', transition='3')
        #self.call_service('light/turn_on', entity_id='light.living_room', profile='nightlight', brightness_pct='100', transition='3') 
        self.run_in(self.morning_01, seconds=3)

    def morning_01(self, kwargs):
        self.call_service('light/turn_on', entity_id='light.living_room', kelvin=3900, brightness_pct='100', transition='3')
        #self.call_service('light/turn_on', entity_id='light.living_room', profile='bright', brightness_pct='100', transition='3')
        self.run_in(self.morning_02, seconds=4)

    def morning_02(self, kwargs):
        self.call_service('light/turn_on', entity_id='light.living_room', kelvin=5600, brightness_pct='100', transition='3')
        #self.call_service('light/turn_on', entity_id='light.living_room', profile='standard', brightness_pct='100', transition='3')

    def morning_off(self, entity, attribute, old, new, kwargs):
        self.log(entity)
        if entity == 'binary_sensor.lighting_motion_xiaomi_upstairs':
            self.call_service('light/turn_off', entity_id='light.upstairs')
        elif entity == 'binary_sensor.lighting_motion_downstairs':
            self.call_service('light/turn_off', entity_id='light.living_room', transition='10')

    def morning_off_sunrise(self, kwargs):
        self.call_service('light/turn_off', entity_id='light.living_room')

    def evening(self, kwargs):
        if self.get_state('light.living_room') == 'on':
            return

        if self.now_is_between("sunset - 01:30:00", "sunset - 00:45:00"):
            # If more than 45 minutes and less than 90 minutes until sunset, fading lights in
            self.log("More than 45 minutes and less than 90 minutes until sunset, fading lights in")
            #self.call_service('light/turn_on', entity_id='light.living_room', profile='standard', brightness_pct=75)
            self.call_service('light/turn_on', entity_id='light.living_room', kelvin=5600, brightness_pct='75')
            self.run_in(self.evening_transition, seconds=30)
        elif self.time() > self.parse_time("sunset - 00:45:00"):
            # If arrived home past 45 minutes to sunset, set lights to 100%
            self.log("Arrived home past 45 minutes to sunset, set lights to 100%")
            #self.call_service('light/turn_on', entity_id='light.living_room', profile='standard')
            self.call_service('light/turn_on', entity_id='light.living_room', kelvin=5600, brightness_pct='100')
            self.run_in(self.evening_transition, seconds=30)

    def evening_transition(self, kwargs):
        seconds_to = (int(abs(self.sunset() - self.datetime()).total_seconds()) / 2)
        self.log("Starting evening_transition, setting transition time to: " + str(seconds_to))
        #self.call_service('light/turn_on', entity_id='light.living_room', profile='standard', transition=seconds_to)
        self.call_service('light/turn_on', entity_id='light.living_room', kelvin=5600, brightness_pct='100', transition=seconds_to)

    def evening_flux_00(self, kwargs):
        end_time = (str(self.date())) + " 21:00:00" 
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        transition_time = (int(abs(end_time - self.datetime()).total_seconds() / 2))
        if self.get_state('light.living_room') == 'on':
            self.log("Starting evening_flux_00, setting transition time to: " + str(transition_time))
            #self.call_service('light/turn_on', entity_id='light.living_room', xy_color=['0.4576', '0.4099'], transition=transition_time)
            self.call_service('light/turn_on', entity_id='light.living_room', kelvin=3900, brightness_pct='100', transition=transition_time)
            self.run_in(self.evening_flux_01, seconds=transition_time)

    def evening_flux_01(self, kwargs):
        end_time = (str(self.date())) + " 21:00:00" 
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        transition_time = (int(abs(end_time - self.datetime()).total_seconds()))
        if self.get_state('light.living_room') == 'on':
            self.log("Starting evening_flux_01, setting transition time to: " + str(transition_time))
            #self.call_service('light/turn_on', entity_id='light.living_room', xy_color=['0.5609', '0.4042'], transition=transition_time)
            self.call_service('light/turn_on', entity_id='light.living_room', kelvin=2200, brightness_pct='100', transition=transition_time)

    def evening_flux_02(self, kwargs):
        day = datetime.datetime.today().weekday()
        if self.get_state('light.living_room') == 'on':
            if day in [0, 1, 2, 3, 6] and self.now_is_between("21:00:00", "21:00:59"):
                #self.call_service('light/turn_on', entity_id='light.living_room', xy_color=['0.5609', '0.4042'], brightness_pct='40', transition='1800')
                self.call_service('light/turn_on', entity_id='light.living_room', kelvin=2200, brightness_pct='75', transition=1800)
            elif day in [4, 5] and self.now_is_between("23:00:00", "23:00:59"):
                #self.call_service('light/turn_on', entity_id='light.living_room', xy_color=['0.5609', '0.4042'], brightness_pct='40', transition='1800')
                self.call_service('light/turn_on', entity_id='light.living_room', kelvin=2200, brightness_pct='75', transition=1800)

    def evening_sleep_00(self, entity, attribute, old, new, kwargs):
        #self.call_service('light/turn_on', entity_id='light.living_room', profile='nightlight', brightness_pct='40')
        self.call_service('light/turn_on', entity_id='light.living_room', kelvin=2200, brightness_pct='50')
        #self.call_service('light/turn_on', entity_id='light.upstairs', color_name='orange', brightness_pct='100')
        #self.run_in(self.evening_sleep_01, seconds=600)

    def evening_sleep_01(self, kwargs):
        self.call_service('light/turn_off', entity_id=['light.living_room', 'light.upstairs'])
        self.call_service('light/turn_off', entity_id=['light.living_room', 'light.upstairs'])
        self.call_service('light/turn_off', entity_id=['light.living_room', 'light.upstairs'])

    def nightlight_upstairs_on(self, entity, attribute, old, new, kwargs):
        if self.get_state('light.upstairs') == 'off':
            self.call_service('light/turn_on', entity_id='light.upstairs', color_name='red', brightness_pct='100')

    def nightlight_downstairs_on(self, entity, attribute, old, new, kwargs):
        if self.get_state('light.living_room') == 'off':
            self.call_service('light/turn_on', entity_id='light.living_room', profile='nightlight', brightness_pct='20', transition='5')          

    def nightlight_off(self, entity, attribute, old, new, kwargs):
        self.log(entity)
        if entity == 'binary_sensor.lighting_motion_xiaomi_upstairs':
            self.call_service('light/turn_off', entity_id='light.upstairs')
        elif entity == 'binary_sensor.lighting_motion_downstairs':
            self.call_service('light/turn_off', entity_id='light.living_room', transition='10')


