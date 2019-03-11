from datetime import datetime
from datetime import timedelta
import appdaemon.plugins.hass.hassapi as hass
#
# Hello World App
#
# Args:
#


class CalendarAlarm(hass.Hass):

    def initialize(self):
        self.listen_state(self.alarm_set, entity='input_select.house', new='Sleep')
        
    def alarm_set(self, entity, attribute, old, new, kwargs):
        sep = " "
        start = self.get_state(entity="calendar.kyle", attribute="start_time")
        start_day = start.split(sep, 1)[0]
        today = self.date()
        today = str(today).split(sep, 1)[0]
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow = str(tomorrow).split(sep, 1)[0]
        if start_day == tomorrow or start_day == today:
            self.call_service('homeassistant/turn_on',entity_id='input_boolean.masterbedroom_service_alarm')
            start_time = start.split(sep, 1)[1]
            alarm_time = datetime.strptime(start_time, '%H:%M:%S') - datetime.strptime('02:00:00', '%H:%M:%S')
            sep = ':'
            alarm_hour = str(alarm_time).split(sep, 1)[0]
            alarm_min = str(alarm_time).split(sep, 1)[1]
            alarm_min = (alarm_min).split(sep, 1)[0]
            self.call_service('input_number/set_value', entity_id='input_number.alarm_hours', value=alarm_hour)
            self.call_service('input_number/set_value', entity_id='input_number.alarm_minutes', value=alarm_min)
        else:
            self.call_service('homeassistant/turn_off', entity_id='input_boolean.masterbedroom_service_alarm')
