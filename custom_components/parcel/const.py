"""Constants for the Parcel integration."""

DOMAIN = "parcel"

# API
API_ENDPOINT = "https://api.parcel.app/external/deliveries/"
DEFAULT_SCAN_INTERVAL = 1800  # 30 minutes (well under rate limit of 20 requests/hour)

# Config
CONF_API_KEY = "api_key"

# Status codes
STATUS_CODES = {
    0: "Delivered",
    1: "Frozen",
    2: "In Transit",
    3: "Ready for Pickup",
    4: "Out for Delivery",
    5: "Not Found",
    6: "Delivery Failed",
    7: "Exception",
    8: "Information Received"
}
