refresh:
  name: Refresh
  description: "Force a refresh of all Parcel package data."

add_tracking:
  name: Add Tracking
  description: "Add a new tracking number to Parcel (Note: This is a placeholder service that won't actually work with the current API)."
  fields:
    carrier:
      name: Carrier
      description: "The carrier code (usps, fedex, ups, etc.)"
      required: true
      example: "usps"
      selector:
        text:
    tracking_number:
      name: Tracking Number
      description: "The tracking number for the package"
      required: true
      example: "9400123456789012345678"
      selector:
        text:
    description:
      name: Description
      description: "A description for this package"
      required: true
      example: "Amazon order - headphones"
      selector:
        text:
