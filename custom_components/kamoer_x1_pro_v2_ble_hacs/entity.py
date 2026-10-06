"""Shared entity base."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .client import KamoerClient
from .const import CONF_ADDRESS, DOMAIN


class KamoerEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry, client: KamoerClient, key: str) -> None:
        self._client = client
        address = entry.data[CONF_ADDRESS]
        self._attr_unique_id = f"{address}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address)}, name="Kamoer X1 Pro V2",
            manufacturer="Kamoer", model="x1 pro v2", connections={("bluetooth", address)})

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._client.add_listener(self.async_write_ha_state))
