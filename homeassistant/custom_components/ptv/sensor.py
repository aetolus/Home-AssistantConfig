"""
This component provides HA sensor support for the Public Transport Victoria (PTV) API.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.ptv/
"""
import logging
from datetime import timedelta
import pytz, dateutil.parser, time

import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_USERNAME, CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE,
                                 CONF_NAME, STATE_UNKNOWN)
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'PTV'

SCAN_INTERVAL = timedelta(seconds=60)

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
        x = range(3)
        try:
            for i in x:
                if self.data['departures'][i]['scheduled_departure_utc']:
                    train_scheduled = dateutil.parser.parse(self.data['departures'][i]['scheduled_departure_utc'])
                    train_scheduled = train_scheduled.astimezone(pytz.timezone("Australia/Melbourne"))
                    attr["train{}_scheduled".format(i)] = train_scheduled.strftime("%I:%M:%S")
                if self.data['departures'][i]['estimated_departure_utc']:
                    train_estimated = dateutil.parser.parse(self.data['departures'][i]['estimated_departure_utc'])
                    train_estimated = train_estimated.astimezone(pytz.timezone("Australia/Melbourne"))
                    attr["train{}_estimated".format(i)] = train_estimated.strftime("%I:%M:%S")
        except Exception as e:
            _LOGGER.debug("[ATTR]Data unavailable")
            _LOGGER.error(e)
        return attr

    @property
    def state(self):
        """Return the state of the device."""
        if self.data:
            try:
                next_train_scheduled = dateutil.parser.parse(self.data['departures'][0]['scheduled_departure_utc'])
                next_train_estimated = dateutil.parser.parse(self.data['departures'][0]['estimated_departure_utc'])
                if (next_train_estimated - timedelta(minutes=10)) >= next_train_scheduled:
                    return str("Major Delays")
                elif (next_train_estimated - timedelta(minutes=5)) >= next_train_scheduled:
                    return str("Minor Delays")
                else:
                    return str("Good Service")
            except Exception as e:
                _LOGGER.debug("[STATE]Data unavailable")
                _LOGGER.debug(e)
                return "unknown"
        return STATE_UNKNOWN

    def update(self):
        """Get the latest data from PTV API."""
        resource = 'http://timetableapi.ptv.vic.gov.au/v3/departures/route_type/0/stop/1149?platform_numbers=1&max_results=3&devid=3001212&signature=FBF7960634D43681897A24440C831065F275AA2E'

        try:
            self.data = requests.get(resource, timeout=10).json()
            _LOGGER.debug("Data = %s", self.data)
            _LOGGER.info("PTV data queried")
        except Exception as err:
            _LOGGER.error("Check PTV %s", err.args)
            self.data = None
            raise