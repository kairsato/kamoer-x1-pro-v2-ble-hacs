"""Start / stop / refresh buttons."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory

from .entity import KamoerEntity


async def async_setup_entry(hass, entry, async_add_entities):
    c = entry.runtime_data
    async_add_entities([
        ActionButton(entry, c, "start", "Start dose", "mdi:play", c.start),
        ActionButton(entry, c, "stop", "Stop", "mdi:stop", c.stop),
        ActionButton(entry, c, "refresh", "Refresh status", "mdi:refresh", c.poll,
                     EntityCategory.DIAGNOSTIC),
    ])


class ActionButton(KamoerEntity, ButtonEntity):
    def __init__(self, entry, client, key, name, icon, action, category=None) -> None:
        super().__init__(entry, client, key)
        self._attr_name, self._attr_icon, self._action = name, icon, action
        self._attr_entity_category = category

    async def async_press(self) -> None:
        await self._action()
