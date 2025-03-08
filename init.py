"""The Parcel Package Tracking integration."""
import asyncio
import logging
from datetime import timedelta

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    API_ENDPOINT,
    CONF_API_KEY,
    CONF_FILTER_MODE,
    CONF_SCAN_INTERVAL,
    DEFAULT_FILTER_MODE,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Parcel component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Parcel from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    filter_mode = entry.data.get(CONF_FILTER_MODE, DEFAULT_FILTER_MODE)
    
    # Calculate scan interval in seconds
    scan_interval_minutes = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    scan_interval = timedelta(minutes=scan_interval_minutes)

    session = async_get_clientsession(hass)
    coordinator = ParcelDataUpdateCoordinator(
        hass, session, api_key, filter_mode, scan_interval
    )

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class ParcelDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Parcel data."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        session: aiohttp.ClientSession, 
        api_key: str, 
        filter_mode: str,
        scan_interval: timedelta,
    ):
        """Initialize the coordinator."""
        self.session = session
        self.api_key = api_key
        self.filter_mode = filter_mode
        self.hass = hass

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )

    async def _async_update_data(self):
        """Fetch data from the Parcel API."""
        try:
            with async_timeout.timeout(30):
                return await self._fetch_data()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
        except asyncio.TimeoutError:
            raise UpdateFailed("Timeout fetching data from Parcel API")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error occurred: {err}")

    async def _fetch_data(self):
        """Get the latest data from the Parcel API."""
        url = f"{API_ENDPOINT}?filter_mode={self.filter_mode}"
        headers = {"api-key": self.api_key}

        async with self.session.get(url, headers=headers) as resp:
            data = await resp.json()
            
            if not data.get("success", False):
                error_msg = data.get("error_message", "Unknown error")
                _LOGGER.error("API error: %s", error_msg)
                raise UpdateFailed(f"API error: {error_msg}")
                
            return data.get("deliveries", [])
