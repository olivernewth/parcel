"""Config flow for Parcel integration."""
from __future__ import annotations

import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_API_KEY, DOMAIN, API_ENDPOINT


async def validate_api_key(api_key: str) -> None:
    """Validate the API key by making a request to the Parcel API."""
    headers = {"api-key": api_key}
    try:
        response = requests.get(API_ENDPOINT, headers=headers, timeout=10)
        response.raise_for_status()
        if not response.json().get("success"):
            raise InvalidAuth
    except requests.RequestException:
        raise CannotConnect


class ParcelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Parcel."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                await self.hass.async_add_executor_job(
                    validate_api_key, user_input[CONF_API_KEY]
                )
                # Create entry
                return self.async_create_entry(title="Parcel", data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
            }),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
