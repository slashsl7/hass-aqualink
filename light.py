"""
Support for Aqualink pool lights.
"""
import logging
import time
from typing import TYPE_CHECKING

from homeassistant.components.light import (
    ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, Light)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LIGHTS
from homeassistant.helpers.typing import HomeAssistantType

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['aqualink']

AQUALINK_DOMAIN = 'aqualink'

if TYPE_CHECKING:
    from .api import AqualinkLight


async def async_setup_entry(hass: HomeAssistantType,
                            config_entry: ConfigEntry,
                            async_add_entities) -> None:
    """Set up discovered switches."""
    devs = []
    for dev in hass.data[AQUALINK_DOMAIN][CONF_LIGHTS]:
        devs.append(HassAqualinkLight(dev))
    async_add_entities(devs, True)


class HassAqualinkLight(Light):
    def __init__(self, dev: 'AqualinkLight'):
        Light.__init__(self)
        self.dev = dev
        self._supported_features = None
     
    @property
    def name(self) -> str:
        return self.dev.name

    @property
    def is_on(self) -> bool:
        return self.dev.is_on

    def turn_on(self, **kwargs) -> None:
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        # Aqualink supports percentages in 25% increments.
        pct = int(round(brightness * 4.0 / 255)) * 25
        self.dev.turn_on(pct)
     
    def turn_off(self) -> None:
        self.dev.turn_off()

    @property
    def brightness(self) -> int:
        return self.dev.brightness * 255 / 100
     
    def update(self) -> None:
        if self._supported_features is None:
            self.get_features()
        self.dev.update()

    @property
    def supported_features(self) -> int:
        return self._supported_features
            
    def get_features(self):
        self._supported_features = 0

        if self.dev.is_dimmable:
            self._supported_features |= SUPPORT_BRIGHTNESS
