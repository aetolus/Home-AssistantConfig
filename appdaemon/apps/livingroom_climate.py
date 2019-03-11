import appdaemon.plugins.hass.hassapi as hass

#
# livingroom_climate:
#   module: livingroom_climate
#   class: LivingRoomClimate
#

class LivingRoomClimate(hass.Hass):
    def initialize(self): 
        self.listen_state(self.livingroom_climate_off, entity='group.proximity', old='on', new='off')
        self.listen_state(self.livingroom_climate_off, entity='input_select.house', new='Sleep')
        self.listen_state(self.livingroom_climate_check, entity='sensor.aeotec_zw100_multisensor_6_temperature')
        self.listen_state(self.livingroom_climate_check, entity='input_select.livingroom_climate', new='Off')
        self.listen_state(self.livingroom_climate_check, entity='group.proximity', old='off', new='on')
        self.listen_state(self.livingroom_climate_check, entity='input_select.livingroom_climate')
        self.listen_state(self.livingroom_climate_check, entity='input_select.house', constrain_input_select='input_select.house,Morning,Home')
        
    def livingroom_climate_off(self, entity, attribute, old, new, kwargs):
        self.log('Turning off due to ' + entity + ' changing state to ' + new)
        self.call_service('remote/send_command', entity_id='remote.livingroom', device='40031105', command='Off')
        self.call_service("mqtt/publish", topic="livingroom/climate", payload="Off")

    def livingroom_climate_off_postcheck(self, kwargs):
        self.log('Turning off due to postcheck')
        self.call_service('remote/send_command', entity_id='remote.livingroom', device='40031105', command='Off')
        self.call_service("mqtt/publish", topic="livingroom/climate", payload="Off")

    def livingroom_climate_check(self, entity, attribute, old, new, kwargs):
        # Return if any of the following are true
        if self.get_state("input_select.livingroom_climate") == 'Off':
            return
        if self.get_state("group.proximity") == 'off' and float(self.get_state("sensor.dark_sky_daytime_high_apparent_temperature_0")) < float(30):
            return
        if self.get_state("input_select.house") == 'Sleep':
            return

        # Perform checks
        if self.get_state("input_select.livingroom_climate") == 'Auto':
            self.run_in(self.livingroom_climate_auto, seconds=0, pass_entity=entity)
        elif entity == 'input_select.livingroom_climate' and new == 'Off':
            self.run_in(self.livingroom_climate_off_postcheck, seconds=0)
        elif entity == 'input_select.livingroom_climate' and new != 'Off':
            self.run_in(self.livingroom_climate_on, seconds=0, pass_entity=entity)
        elif entity == 'sensor.aeotec_zw100_multisensor_6_temperature':
            self.run_in(self.livingroom_climate_on, seconds=0, pass_entity=entity)
        elif entity == 'input_select.house':
            self.run_in(self.livingroom_climate_on, seconds=0, pass_entity=entity)

    def livingroom_climate_on(self, kwargs):
        self.log('Reached livingroom_climate_on due to: ' + kwargs["pass_entity"])
        # Set standard variables
        desired_temp = float(self.get_state("input_select.livingroom_climate"))
        inside_temp = float(self.get_state("sensor.aeotec_zw100_multisensor_6_temperature"))
        outside_temp = float(self.get_state("sensor.bom_feels_like_c"))
        upper_tolerance = float(desired_temp + 0.5)
        lower_tolerance = float(desired_temp - 0.5)

        # Set variable 'mode'
        if inside_temp > desired_temp:# and outside_temp > desired_temp:
            mode = 'cool'
            self.call_service('variable/set_variable', variable='notify_climate_powersave', value='cool')
        elif inside_temp < desired_temp:# and outside_temp < desired_temp:
            mode = 'heat'
            self.call_service('variable/set_variable', variable='notify_climate_powersave', value='heat')
        #elif inside_temp > desired_temp and outside_temp < desired_temp or inside_temp < desired_temp and outside_temp > desired_temp:
            #mode = 'powersave'
            #self.call_service('variable/set_variable', variable='notify_climate_powersave', value='powersave')
        else:
            mode = 'off'
        self.log('Mode set to: ' + mode)

        # Reset desired_temp
        if mode == 'cool' and inside_temp > upper_tolerance:
            setting = 'cool_' + str(desired_temp)[:-2]
        elif mode == 'heat' and inside_temp < lower_tolerance:
            setting = 'heat_' + str(desired_temp)[:-2]
        #elif mode == 'powersave':
            #setting = 'Off'
        else:
            setting = 'Off'
        self.log('Setting is: ' + setting)

        # Set Thermostat
        self.call_service('remote/send_command', entity_id='remote.livingroom', device='40031105', command=setting)
        self.call_service("mqtt/publish", topic="livingroom/climate", payload=setting)

    def livingroom_climate_auto(self, kwargs):
        self.log('Reached livingroom_climate_auto due to: ' + kwargs["pass_entity"])
        # Set standard variables
        inside_temp = float(self.get_state("sensor.aeotec_zw100_multisensor_6_temperature"))
        outside_temp = float(self.get_state("sensor.bom_feels_like_c"))
        high_temp = float(self.get_state("sensor.dark_sky_daytime_high_apparent_temperature_0"))

        if inside_temp > 25: #and outside_temp > 25:
            mode = 'cool'
            self.call_service('variable/set_variable', variable='notify_climate_powersave', value='cool')
        elif high_temp > 35:
            mode = 'cool'
            self.call_service('variable/set_variable', variable='notify_climate_powersave', value='cool')
        elif inside_temp < 21: #and outside_temp < 18:
            mode = 'heat'
            self.call_service('variable/set_variable', variable='notify_climate_powersave', value='heat')
        #elif inside_temp > 25 and outside_temp < 21 or inside_temp < 21 and outside_temp > 24:
            #mode = 'powersave'
            #self.call_service('variable/set_variable', variable='notify_climate_powersave', value='powersave')
        else:
            mode = 'off'
        self.log('Mode set to: ' + mode)

        # Reset desired_temp
        if mode == 'cool' and inside_temp > 25.5:
            setting = 'cool_' + str(21)
        elif mode == 'cool' and high_temp > 35:
            setting = '21q'
        elif mode == 'heat' and inside_temp < 20.5:
            setting = 'heat_' + str(21)
        #elif mode == 'powersave':
            #setting = 'Off'
        else:
            setting = 'Off'
        self.log('Setting is: ' + setting)

        # Set Thermostat
        self.call_service('remote/send_command', entity_id='remote.livingroom', device='40031105', command=setting)
        self.call_service("mqtt/publish", topic="livingroom/climate", payload=setting)
