"""Diagnostic sensors. The pump's replies are not decoded yet, so they are exposed raw."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import EntityCategory

from .entity import KamoerEntity


async def async_setup_entry(hass, entry, async_add_entities):
    c = entry.runtime_data
    async_add_entities([Reply(entry, c), LastError(entry, c)])


class Reply(KamoerEntity, SensorEntity):
    _attr_name = "Last reply"
    _attr_icon = "mdi:message-text"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry, client) -> None:
        super().__init__(entry, client, "last_reply")

    @property
    def native_value(self):
        r = self._client.last_reply
        return r[:255] if r else None


class LastError(KamoerEntity, SensorEntity):
    _attr_name = "Last error"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry, client) -> None:
        super().__init__(entry, client, "last_error")

    @property
    def native_value(self):
        return self._client.last_error
