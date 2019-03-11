import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

#
# masterbedroom_climate:
#   module: masterbedroom_climate
#   class: masterbedroomClimate
#

class MasterBedroomClimate(hass.Hass):
    def initialize(self):
        self.listen_state(self.masterbedroom_climate, entity='input_select.bedroom_climate')
        self.run_daily(self.masterbedroom_climate_timer, datetime.time(4, 00, 0))
        self.run_daily(self.masterbedroom_climate_timer, datetime.time(7, 00, 0))
        self.run_daily(self.masterbedroom_climate_timer, datetime.time(17, 00, 0))
        self.run_daily(self.masterbedroom_climate_timer, datetime.time(23, 00, 0))

    def masterbedroom_climate(self, entity, attribute, old, new, kwargs):
        if new == 'Cool':
            self.call_service("script/xiaomi_remote_climate_cool_on")
        elif new == 'Heat':
            self.log("Heating command not taught yet")
        elif new == 'Off':
            self.call_service("script/xiaomi_remote_climate_off")

    def masterbedroom_climate_timer(self, kwargs):
        if self.get_state(entity='input_select.house') == 'Vacation':
            return
            
        if self.now_is_between("04:00:00", "04:01:00") or self.now_is_between("17:00:00", "17:01:00"):
            if float(self.get_state("sensor.room_master_climate")) > 22:
                self.select_option('input_select.bedroom_climate', 'Cool')
        elif self.now_is_between("07:00:00", "07:01:00") or self.now_is_between("23:00:00", "23:01:00"):
            self.select_option('input_select.bedroom_climate', 'Off')
