"""Dose volume (ml)."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DEFAULT_VOLUME_ML, MAX_VOLUME_ML
from .entity import KamoerEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([DoseVolume(entry, entry.runtime_data)])


class DoseVolume(KamoerEntity, NumberEntity, RestoreEntity):
    _attr_name = "Dose volume"
    _attr_icon = "mdi:water"
    _attr_native_unit_of_measurement = "mL"
    _attr_native_min_value = 0
    _attr_native_max_value = MAX_VOLUME_ML
    _attr_native_step = 0.1
    _attr_mode = NumberMode.BOX

    def __init__(self, entry, client) -> None:
        super().__init__(entry, client, "dose_volume")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        try:
            self._client.volume_ml = float(last.state) if last else DEFAULT_VOLUME_ML
        except (TypeError, ValueError):
            self._client.volume_ml = DEFAULT_VOLUME_ML

    @property
    def native_value(self) -> float:
        return self._client.volume_ml

    async def async_set_native_value(self, value: float) -> None:
        # Stored only; the Start button sends it to the pump, so editing the number never moves the pump.
        self._client.volume_ml = float(value)
        self.async_write_ha_state()
