"""Sensor platform for Parcel package tracking."""
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    ATTR_TRACKING_NUMBER,
    ATTR_CARRIER,
    ATTR_STATUS,
    ATTR_DESCRIPTION,
    ATTR_EXPECTED_DATE,
    ATTR_LATEST_EVENT,
    ATTR_LATEST_EVENT_LOCATION,
    ATTR_LATEST_EVENT_TIME,
    ATTR_EVENTS,
    STATUS_CODES,
    CARRIER_NAMES,
    STATUS_ICONS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Parcel sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Wait for first data to be available
    await coordinator.async_config_entry_first_refresh()
    
    # Create a sensor for each package
    sensors = []
    for package in coordinator.data:
        sensors.append(ParcelSensor(coordinator, package))
    
    async_add_entities(sensors, True)


class ParcelSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Parcel sensor."""

    def __init__(self, coordinator, package_data):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._package_data = package_data
        self._tracking_number = package_data.get("tracking_number", "")
        self._carrier_code = package_data.get("carrier_code", "")
        self._status_code = package_data.get("status_code", 5)  # Default to "Not Found"
        self._description = package_data.get("description", "")
        
        # Set the unique ID to be the tracking number
        self._attr_unique_id = f"parcel_{self._tracking_number}"
        
        # Set the entity name based on description and carrier
        carrier_name = CARRIER_NAMES.get(self._carrier_code, self._carrier_code.upper())
        self._attr_name = f"{self._description} ({carrier_name})"
        
        # Set initial state and attributes
        self._update_state_and_attributes()

    @property
    def device_info(self):
        """Return device information for this entity."""
        return {
            "identifiers": {(DOMAIN, "parcel_tracker")},
            "name": "Parcel Package Tracker",
            "manufacturer": "Parcel",
            "model": "Package Tracker",
            "sw_version": "1.0.0",
        }

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return STATUS_ICONS.get(self._status_code, "mdi:package-variant")

    def _update_state_and_attributes(self) -> None:
        """Update state and attributes based on the latest package data."""
        # Try to find the updated package data in the coordinator
        for package in self.coordinator.data:
            if package.get("tracking_number") == self._tracking_number:
                self._package_data = package
                self._status_code = package.get("status_code", self._status_code)
                break
                
        # Set the sensor state to the status code text
        self._attr_native_value = STATUS_CODES.get(self._status_code, "Unknown")
        
        # Extract events
        events = self._package_data.get("events", [])
        
        # Get the latest event if available
        latest_event = None
        latest_event_location = None
        latest_event_time = None
        
        if events:
            latest = events[0]  # Events are assumed to be in descending order
            latest_event = latest.get("event", "")
            latest_event_location = latest.get("location", "")
            latest_event_time = latest.get("date", "")
            
        # Get expected delivery date if available
        expected_date = self._package_data.get("date_expected", "")
        
        # Set attributes
        self._attr_extra_state_attributes = {
            ATTR_TRACKING_NUMBER: self._tracking_number,
            ATTR_CARRIER: CARRIER_NAMES.get(self._carrier_code, self._carrier_code),
            ATTR_STATUS: self._attr_native_value,
            ATTR_DESCRIPTION: self._description,
            ATTR_EXPECTED_DATE: expected_date,
            ATTR_LATEST_EVENT: latest_event,
            ATTR_LATEST_EVENT_LOCATION: latest_event_location,
            ATTR_LATEST_EVENT_TIME: latest_event_time,
            ATTR_EVENTS: events,
        }
        
    async def async_update(self) -> None:
        """Update the sensor."""
        await self.coordinator.async_request_refresh()
        self._update_state_and_attributes()
