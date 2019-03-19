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
        self.run_daily(self.masterbedroom_climate_timer, datetime.time(6, 00, 0))
        self.run_daily(self.masterbedroom_climate_timer, datetime.time(18, 30, 0))
        self.run_daily(self.masterbedroom_climate_timer, datetime.time(22, 30, 0))

    def masterbedroom_climate(self, entity, attribute, old, new, kwargs):
        if new == 'Cool':
            self.call_service("script/xiaomi_remote_climate_cool_on")
        elif new == 'Heat':
            self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="Heating command for master bedroom has not been taught yet")
        elif new == 'Off':
            self.call_service("script/xiaomi_remote_climate_off")

    def masterbedroom_climate_timer(self, kwargs):
        if self.get_state(entity='input_select.house') == 'Vacation':
            return
            
        if self.now_is_between("04:00:00", "04:01:00") or self.now_is_between("18:30:00", "18:31:00"):
            if float(self.get_state("sensor.room_master_climate")) > 25:
                self.select_option('input_select.bedroom_climate', 'Cool')
            elif float(self.get_state("sensor.room_master_climate")) < 15:
                self.select_option('input_select.bedroom_climate', 'Heat')
        elif self.now_is_between("06:00:00", "06:01:00") or self.now_is_between("22:30:00", "22:31:00"):
            self.select_option('input_select.bedroom_climate', 'Off')
