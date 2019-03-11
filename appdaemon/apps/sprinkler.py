import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

class Sprinkler(hass.Hass):
    
    def initialize(self):
        self.run_daily(self.record_rainfall, datetime.time(23, 00, 0))

    def record_rainfall(self, kwargs):
        self.utilities = self.get_app('utilities')
        day_of_week = self.utilities.day_of_week()
        self.log(day_of_week)
        rainfall = self.get_state(entity='sensor.bom_rain_today')
        self.call_service("mqtt/publish", topic="sprinkler/rainfall/" + day_of_week, payload=rainfall, retain="true")