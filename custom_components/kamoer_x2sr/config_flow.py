"""Config flow: found by Bluetooth name (KAMOER_X*), or picked from nearby devices."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.components.bluetooth import (BluetoothServiceInfoBleak,
                                                async_discovered_service_info)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_ADDRESS, CONF_NAME, DOMAIN


class KamoerConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._discovery: BluetoothServiceInfoBleak | None = None
        self._found: dict[str, str] = {}

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak) -> ConfigFlowResult:
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name}
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None) -> ConfigFlowResult:
        assert self._discovery is not None
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovery.name,
                data={CONF_ADDRESS: self._discovery.address, CONF_NAME: self._discovery.name})
        self._set_confirm_only()
        return self.async_show_form(step_id="confirm", description_placeholders={
            "name": self._discovery.name, "address": self._discovery.address})

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._found[address], data={CONF_ADDRESS: address, CONF_NAME: self._found[address]})
        current = self._async_current_ids()
        self._found = {i.address: i.name for i in async_discovered_service_info(self.hass, False)
                       if i.name.upper().startswith("KAMOER") and i.address not in current}
        if not self._found:
            return self.async_abort(reason="no_devices_found")
        return self.async_show_form(step_id="user", data_schema=vol.Schema(
            {vol.Required(CONF_ADDRESS): vol.In({a: f"{n} ({a})" for a, n in self._found.items()})}))
