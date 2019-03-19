"""
Support for Holman iWater

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.holman_iwater/
"""
import logging
import platform
import subprocess as sp

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchDevice
from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.script import Script

REQUIREMENTS = ['pygatt[GATTTOOL]==3.2.0']

_LOGGER = logging.getLogger(__name__)

CONF_MAC_ADDRESS = 'mac_address'

DEFAULT_NAME = 'holman_iwater'
DEFAULT_BLE_TIMEOUT = 10

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC_ADDRESS): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up a wake on lan switch."""
    mac_address = config.get(CONF_MAC_ADDRESS)
    name = config.get(CONF_NAME)

    add_entities([HolmanSwitch(
        hass, name, mac_address)], True)


class HolmanSwitch(SwitchDevice):
    """Representation of a wake on lan switch."""

    def __init__(
            self, hass, name, mac_address):
        """Initialize the Holman iWater switch."""
        import pygatt
        self._hass = hass
        self._name = name
        self._mac_address = mac_address
        self._state = False

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    def turn_on(self, **kwargs):
        """Turn the device on."""
        on_command = ['/usr/bin/gatttool', '-i', 'hci0', '-b', 'D5:D3:E0:82:10:BD', '-t', 'random', '--char-write-req', '-a', '0x0014', '-n', '01000020']
        sp.call(on_command)


    def turn_off(self, **kwargs):
        """Turn the device off."""
        off_command = ['/usr/bin/gatttool', '-i', 'hci0', '-b', 'D5:D3:E0:82:10:BD', '-t', 'random', '--char-write-req', '-a', '0x0014', '-n', '01000000']
        sp.call(off_command)