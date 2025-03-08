"""The Parcel integration."""
import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import requests

from .const import API_ENDPOINT, CONF_API_KEY, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup(hass, config):
    """Set up the Parcel component from configuration.yaml."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Parcel from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    
    coordinator = ParcelDataUpdateCoordinator(hass, api_key)
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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
    """Class to manage fetching data from the API."""

    def __init__(self, hass, api_key):
        """Initialize."""
        self.api_key = api_key
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via API."""
        try:
            return await self.hass.async_add_executor_job(self._get_data)
        except requests.RequestException as error:
            raise UpdateFailed(f"Error communicating with API: {error}") from error

    def _get_data(self):
        """Get data from the API."""
        headers = {"api-key": self.api_key}
        active_response = requests.get(
            f"{API_ENDPOINT}?filter_mode=active", headers=headers, timeout=10
        )
        active_response.raise_for_status()
        active_data = active_response.json()
        
        recent_response = requests.get(
            f"{API_ENDPOINT}?filter_mode=recent", headers=headers, timeout=10
        )
        recent_response.raise_for_status()
        recent_data = recent_response.json()
        
        if not active_data.get("success") or not recent_data.get("success"):
            raise UpdateFailed("API reported unsuccessful request")
        
        return {
            "active": active_data.get("deliveries", []),
            "recent": recent_data.get("deliveries", [])
        }
