"""
This component provides HA sensor support for the worldtides.info API.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.PTV/
"""
import logging
from datetime import timedelta
import pytz, dateutil.parser

import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_USERNAME, CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE,
                                 CONF_NAME, STATE_UNKNOWN)
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'PTV'

SCAN_INTERVAL = timedelta(seconds=300)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the PTV sensor."""
    name = config.get(CONF_NAME)

    add_devices([PTVSensor(name)], True)


class PTVSensor(Entity):
    """Representation of a PTV sensor."""

    def __init__(self, name):
        """Initialize the sensor."""
        self._name = name
        self.data = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {}
        train1 = dateutil.parser.parse(self.data['departures'][0]['scheduled_departure_utc'])
        train1 = train1.astimezone(pytz.timezone("Australia/Melbourne"))
        train2 = dateutil.parser.parse(self.data['departures'][1]['scheduled_departure_utc'])
        train2 = train2.astimezone(pytz.timezone("Australia/Melbourne"))
        train3 = dateutil.parser.parse(self.data['departures'][2]['scheduled_departure_utc'])
        train3 = train3.astimezone(pytz.timezone("Australia/Melbourne"))
        attr['next_train'] = train1
        attr['second_train'] = train2
        attr['third_train'] = train3
        return attr

    @property
    def state(self):
        """Return the state of the device."""
        if self.data:
            next_train = dateutil.parser.parse(self.data['departures'][0]['scheduled_departure_utc'])
            next_train = next_train.astimezone(pytz.timezone("Australia/Melbourne"))
            return next_train
        return STATE_UNKNOWN

    def update(self):
        """Get the latest data from PTV API."""
        resource = 'http://timetableapi.ptv.vic.gov.au/v3/departures/route_type/0/stop/1149?platform_numbers=1&max_results=3&devid=3001212&signature=FBF7960634D43681897A24440C831065F275AA2E'

        try:
            self.data = requests.get(resource, timeout=10).json()
            _LOGGER.debug("Data = %s", self.data)
            _LOGGER.info("PTV data queried")
        except ValueError as err:
            _LOGGER.error("Check PTV %s", err.args)
            self.data = None
            raise