"""Config flow for Parcel Package Tracking."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_FILTER_MODE,
    CONF_SCAN_INTERVAL,
    FILTER_MODES,
    DEFAULT_FILTER_MODE,
    DEFAULT_SCAN_INTERVAL,
)


class ParcelOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Parcel options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_FILTER_MODE,
                        default=self.config_entry.options.get(
                            CONF_FILTER_MODE, 
                            self.config_entry.data.get(CONF_FILTER_MODE, DEFAULT_FILTER_MODE)
                        ),
                    ): vol.In(FILTER_MODES),
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, 
                            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=15, max=180)),
                }
            ),
        )


@callback
def register_options_flow(config_entry):
    """Register options flow for Parcel."""
    config_entry.async_register_updates(ParcelOptionsFlowHandler)
