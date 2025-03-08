"""Constants for the Parcel Package Tracking integration."""

DOMAIN = "parcel"

# Configuration constants
CONF_API_KEY = "api_key"
CONF_FILTER_MODE = "filter_mode"
CONF_SCAN_INTERVAL = "scan_interval"

# API constants
API_ENDPOINT = "https://api.parcel.app/external/deliveries/"
DEFAULT_FILTER_MODE = "active"
FILTER_MODES = ["active", "recent"]
DEFAULT_SCAN_INTERVAL = 30  # 30 minutes to respect 20 requests/hour limit

# Status code to text mapping
STATUS_CODES = {
    0: "Completed",
    1: "Frozen",
    2: "In Transit",
    3: "Ready for Pickup",
    4: "Out for Delivery",
    5: "Not Found",
    6: "Delivery Attempt Failed",
    7: "Exception",
    8: "Waiting for Carrier"
}

# Carrier code to name mapping (common carriers)
CARRIER_NAMES = {
    "usps": "USPS",
    "fedex": "FedEx",
    "ups": "UPS",
    "dhl": "DHL",
    "amzlus": "Amazon Logistics",
    "canadapost": "Canada Post",
    "royalmail": "Royal Mail",
    "auspost": "Australia Post",
    "jpost": "Japan Post",
    "lasership": "LaserShip",
    "ontrac": "OnTrac"
    # Add more as needed
}

# Icons for different status types
STATUS_ICONS = {
    0: "mdi:package-variant-closed-check",  # Completed
    1: "mdi:package-variant-closed-remove", # Frozen
    2: "mdi:truck-delivery",                # In Transit
    3: "mdi:store",                         # Ready for Pickup
    4: "mdi:truck-fast",                    # Out for Delivery
    5: "mdi:help-circle",                   # Not Found
    6: "mdi:package-variant-closed-alert",  # Delivery Attempt Failed
    7: "mdi:alert-circle",                  # Exception
    8: "mdi:package-variant-closed-clock"   # Waiting for Carrier
}

# Entity IDs
ATTR_TRACKING_NUMBER = "tracking_number"
ATTR_CARRIER = "carrier"
ATTR_STATUS = "status"
ATTR_DESCRIPTION = "description"
ATTR_EXPECTED_DATE = "expected_date"
ATTR_LATEST_EVENT = "latest_event"
ATTR_LATEST_EVENT_LOCATION = "latest_event_location"
ATTR_LATEST_EVENT_TIME = "latest_event_time"
ATTR_EVENTS = "events"
