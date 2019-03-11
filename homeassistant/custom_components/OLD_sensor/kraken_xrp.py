"""
This component provides HA sensor support for the worldtides.info API.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.worldtidesinfo/
"""
import logging
import time
from datetime import timedelta

import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, STATE_UNKNOWN)
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Kraken_XRP'

SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Kraken XRP sensor."""
    name = config.get(CONF_NAME)

    add_devices([KrakenXRPSensor(name)], True)


class KrakenXRPSensor(Entity):
    """Representation of a KrakenXRP sensor."""

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
        attr['AskPrice'] = self.data['result']['XXRPZEUR']['a']
        return attr

    @property
    def state(self):
        """Return the state of the device."""
        if self.data:
            return self.data['result']['XXRPZEUR']['a']
        else:
            return STATE_UNKNOWN

    def update(self):
        """Get the latest data from Kraken API."""
        resource = 'https://api.kraken.com/0/public/Ticker?pair=XRPEUR'

        try:
            self.data = requests.get(resource, timeout=10).json()
            _LOGGER.debug("Data = %s", self.data)
            _LOGGER.info("Kraken XRP data queried")
        except ValueError as err:
            _LOGGER.error("Check Kraken API %s", err.args)
            self.data = None
            raise
