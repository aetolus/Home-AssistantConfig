import appdaemon.plugins.hass.hassapi as hass
import datetime
import random
#
# App to localize frequently used functions
#
#
# class HelloWorld(hass.Hass):
#     def initialize(self):
#         self.utilities = self.get_app('utilities')
#         self.log('Tomorrow is {}'.format(self.utilities.day_of_week())
#
class Utilities(hass.Hass):

    def initialize(self):
        pass

    def is_weekday(self):
        day = datetime.datetime.today().weekday()
        if day in [0, 1, 2, 3, 4]:
            is_weekday = True
        else:
            is_weekday = False
        return is_weekday

    def day_of_week(self):
        day = datetime.datetime.today().weekday()
        if day in [0]:
            day_of_week = 'Mon'
        elif day in [1]:
            day_of_week = 'Tue'
        elif day in [2]:
            day_of_week = 'Wed'
        elif day in [3]:
            day_of_week = 'Thu'
        elif day in [4]:
            day_of_week = 'Fri'
        elif day in [5]:
            day_of_week = 'Sat'
        elif day in [6]:
            day_of_week = 'Sun'
        return day_of_week