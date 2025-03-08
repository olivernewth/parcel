"""Config flow for Parcel Package Tracking integration."""
import logging
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    API_ENDPOINT,
    CONF_API_KEY,
    CONF_FILTER_MODE,
    CONF_SCAN_INTERVAL,
    FILTER_MODES,
    DEFAULT_FILTER_MODE,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class ParcelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Parcel Package Tracking."""

    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the API key by attempting to connect to the API
            valid = await self._test_api_key(
                user_input[CONF_API_KEY], 
                user_input.get(CONF_FILTER_MODE, DEFAULT_FILTER_MODE)
            )

            if valid:
                # Create a unique ID based on the API key (first 8 chars)
                # This avoids exposing the full key while allowing multiple accounts
                unique_id = user_input[CONF_API_KEY][:8]
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, "Parcel Package Tracking"),
                    data=user_input,
                )
            else:
                errors["base"] = "invalid_api_key"

        # If there is no user input or there were errors, show the form again
        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_NAME, default="Parcel Package Tracking"): str,
                vol.Optional(CONF_FILTER_MODE, default=DEFAULT_FILTER_MODE): vol.In(FILTER_MODES),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=180)
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _test_api_key(self, api_key, filter_mode):
        """Test if the API key is valid."""
        try:
            session = async_get_clientsession(self.hass)
            url = f"{API_ENDPOINT}?filter_mode={filter_mode}"
            headers = {"api-key": api_key}

            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data.get("success", False)
                
        except (aiohttp.ClientError, asyncio.TimeoutError):
            _LOGGER.error("Error validating API key")
            return False
        except Exception as err:
            _LOGGER.exception("Unexpected error: %s", err)
            return False
