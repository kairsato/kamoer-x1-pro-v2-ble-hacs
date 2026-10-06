"""Kamoer X2SR water changer over Bluetooth Low Energy."""
from __future__ import annotations

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .client import KamoerClient
from .const import CONF_ADDRESS, CONF_NAME

PLATFORMS = [Platform.NUMBER, Platform.BUTTON, Platform.SENSOR]

type KamoerConfigEntry = ConfigEntry[KamoerClient]


async def async_setup_entry(hass: HomeAssistant, entry: KamoerConfigEntry) -> bool:
    address = entry.data[CONF_ADDRESS]

    def get_device():
        return bluetooth.async_ble_device_from_address(hass, address, connectable=True)

    entry.runtime_data = KamoerClient(get_device, entry.data.get(CONF_NAME) or address)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: KamoerConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
