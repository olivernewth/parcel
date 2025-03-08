"""Sensor platform for Parcel integration."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_CODES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Parcel sensor entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = []
    
    # First refresh
    await coordinator.async_config_entry_first_refresh()
    
    # Add active deliveries sensors
    if coordinator.data and "active" in coordinator.data:
        for delivery in coordinator.data["active"]:
            sensors.append(ParcelDeliverySensor(coordinator, delivery, "active"))
    
    # Add recent deliveries sensors
    if coordinator.data and "recent" in coordinator.data:
        for delivery in coordinator.data["recent"]:
            # Only add if not already added
            if not any(s.unique_id == delivery["tracking_number"] for s in sensors):
                sensors.append(ParcelDeliverySensor(coordinator, delivery, "recent"))
    
    async_add_entities(sensors, True)


class ParcelDeliverySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Parcel delivery sensor."""

    def __init__(self, coordinator, delivery, delivery_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._delivery = delivery
        self._delivery_type = delivery_type
        self._tracking_number = delivery["tracking_number"]
        self._description = delivery["description"]
        self._attr_name = f"Parcel {self._description}"
        self._attr_unique_id = self._tracking_number
        
    @property
    def state(self):
        """Return the state of the sensor."""
        status_code = self._get_current_delivery().get("status_code")
        return STATUS_CODES.get(status_code, "Unknown")
    
    @property
    def icon(self):
        """Return the icon of the sensor."""
        status_code = self._get_current_delivery().get("status_code")
        if status_code == 0:  # Delivered
            return "mdi:package-variant-closed"
        elif status_code == 4:  # Out for delivery
            return "mdi:truck-delivery"
        elif status_code == 3:  # Ready for pickup
            return "mdi:store"
        elif status_code == 6:  # Delivery failed
            return "mdi:alert"
        elif status_code == 7:  # Exception
            return "mdi:alert-circle"
        else:
            return "mdi:package"
    
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        delivery = self._get_current_delivery()
        attrs = {
            "tracking_number": delivery.get("tracking_number"),
            "description": delivery.get("description"),
            "carrier": delivery.get("carrier_code"),
            "status_code": delivery.get("status_code"),
            "status": STATUS_CODES.get(delivery.get("status_code"), "Unknown"),
        }
        
        # Add expected delivery date if available
        if date_expected := delivery.get("date_expected"):
            attrs["expected_date"] = date_expected
            
        if timestamp_expected := delivery.get("timestamp_expected"):
            attrs["expected_timestamp"] = datetime.fromtimestamp(timestamp_expected).isoformat()
        
        # Add events if available
        events = delivery.get("events", [])
        if events:
            # Get the latest event
            latest_event = events[0] if events else {}
            
            attrs["latest_event"] = latest_event.get("event")
            attrs["latest_event_date"] = latest_event.get("date")
            attrs["latest_event_location"] = latest_event.get("location")
            
            # Add all events
            attrs["events"] = events
        
        return attrs
    
    def _get_current_delivery(self):
        """Get the current delivery data."""
        if not self.coordinator.data:
            return {}
            
        # Look in active deliveries first
        for delivery in self.coordinator.data.get("active", []):
            if delivery["tracking_number"] == self._tracking_number:
                return delivery
                
        # Then check recent deliveries
        for delivery in self.coordinator.data.get("recent", []):
            if delivery["tracking_number"] == self._tracking_number:
                return delivery
                
        # Return the last known state if not found
        return self._delivery
