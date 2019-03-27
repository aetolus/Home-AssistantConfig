import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

class Sprinkler(hass.Hass):
    
    def initialize(self):
        self.run_daily(self.record_rainfall, datetime.time(23, 45, 0))
        self.run_daily(self.check_rainfall, datetime.time(4, 0, 30))

    def record_rainfall(self, kwargs):
        self.utilities = self.get_app('utilities')
        day_of_week = self.utilities.day_of_week()
        rainfall = self.get_state(entity='sensor.bom_rain_today')
        self.call_service("mqtt/publish", topic="sprinkler/rainfall/" + day_of_week, payload=rainfall, retain="true")

    def check_rainfall(self, kwargs):
        self.utilities = self.get_app('utilities')
        if self.utilities.day_of_week() == 'Mon':
            monday = self.get_state("sensor.bom_rain_today")
            sunday = self.get_state("sensor.sprinkler_rainfall_sun")
            saturday = self.get_state("sensor.sprinkler_rainfall_sat")
            friday = self.get_state("sensor.sprinkler_rainfall_fri")
            thursday = self.get_state("sensor.sprinkler_rainfall_thu")
            total_rainfall = float(monday) + float(sunday) + float(saturday) + float(friday) + float(thursday)
        elif self.utilities.day_of_week() == 'Thu':
            thursday = self.get_state("sensor.bom_rain_today")
            wednesday = self.get_state("sensor.sprinkler_rainfall_wed")
            tuesday = self.get_state("sensor.sprinkler_rainfall_tue")
            monday = self.get_state("sensor.sprinkler_rainfall_mon")
            total_rainfall = float(thursday) + float(wednesday) + float(tuesday) + float(monday)
        else:
            return
        if total_rainfall > 3.0:
            self.log('Switching sprinkler off due to ' + str(total_rainfall) + 'mm rainfall.')
            self.call_service('shell_command/sprinkler_off')


