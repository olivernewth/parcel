# ...existing code...
from homeassistant.helpers.entity import Entity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # ...existing code...
    async_add_entities([ParcelSensor()])

class ParcelSensor(Entity):
    # ...existing code...
    @property
    def name(self):
        return "Parcel Sensor"

    @property
    def state(self):
        # ...existing code...
        return "state"
