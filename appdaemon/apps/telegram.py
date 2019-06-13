import appdaemon.plugins.hass.hassapi as hass

#
# Hello World App
#
# Args:
#

class Telegram(hass.Hass):

    def initialize(self):
        self.listen_event(self.update_homeassistant, event="telegram_command")

    def update_homeassistant(self, event_id, payload_event, *args):
        assert event_id == 'telegram_command'
        user_id = payload_event['user_id']
        command = payload_event['command']
        if command == '/update':
            self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="Updating HomeAssistant now. You will be notified on restart.")
            self.call_service("shell_command/update_homeassistant")
        elif command == '/clean':
            self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="Pruning docker images now.")
            self.call_service("shell_command/cleanup_homeassistant")
        elif command == '/reboot_win10':
            self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="Issuing reboot command to WIN10 now.")
            self.call_service("shell_command/reboot_win10")
        elif command == '/where':
            sarah_location = self.get_state(entity='sensor.google_geocode_sarah')
            self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="Sarah's location is: " + sarah_location)
        elif command == '/trains':
            self.call_service("mqtt/publish", topic="notifications/newmsg/telegram", payload="The next train service is scheduled for " + self.get_state(entity="sensor.ptv", attribute="train0_scheduled") + " with an estimated departure time of " + self.get_state(entity="sensor.ptv", attribute="train0_estimated") + " followed by " + self.get_state(entity="sensor.ptv", attribute="train1_scheduled"))