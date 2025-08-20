"""Expanded option aliases for transform normalization.

Each key is a canonical option name.  The value lists representative
synonyms or variants that may appear in listing data so the transform
step can normalize them to the canonical label.
"""

# Authoritative expanded options mapping lives here.
# Synonym lists are not exhaustive—just the common phrases we expect to
# encounter in scraped data.
OPTIONS = {
    # Sport Chrono package variants
    "Sport Chrono": [
        "Sport Chrono Package",
        "Sport Chrono Package Plus",
        "Sport Chrono Plus",
    ],

    # Porsche Active Suspension Management
    "PASM": [
        "PASM",
        "Porsche Active Suspension Management",
        "Active Suspension Management",
        "Electronic Damper Control",
    ],

    # Porsche Sport Exhaust system
    "Porsche Sport Exhaust": [
        "Porsche Sport Exhaust",
        "Sport Exhaust System",
        "Sport Exhaust",
        "PSE",
    ],

    # Limited slip differential
    "Limited Slip Differential": [
        "Limited Slip Differential",
        "LSD",
        "Rear Differential Lock",
    ],

    # Porsche Ceramic Composite Brakes
    "PCCB": [
        "PCCB",
        "Porsche Ceramic Composite Brakes",
        "Ceramic Brakes",
        "Carbon Ceramic Brakes",
    ],

    # Bose premium audio
    "Bose Audio": [
        "Bose Audio",
        "Bose Surround Sound",
        "Bose High End Sound",
        "Bose Premium Audio",
    ],

    # PCM navigation system
    "PCM Navigation": [
        "PCM Navigation",
        "Porsche Communication Management",
        "Navigation Module",
        "Navigation System",
        "PCM",
        "Nav System",
    ],

    # Seat heating
    "Heated Seats": [
        "Heated Seats",
        "Seat Heating",
        "Heated Front Seats",
        "Seat Heater",
    ],

    # Seat ventilation / cooling
    "Ventilated Seats": [
        "Ventilated Seats",
        "Seat Ventilation",
        "Cooled Seats",
        "Seat Cooling",
    ],

    # Porsche Dynamic Light System
    "PDLS": [
        "PDLS",
        "Porsche Dynamic Light System",
        "Dynamic Light System",
        "Dynamic Lighting",
    ],

    # Xenon / Bi-Xenon headlights
    "Xenon Headlights": [
        "Xenon Headlights",
        "Bi-Xenon Headlights",
        "Bi-Xenon",
        "HID Headlights",
    ],

    # Sport seat variants
    "Sport Seats": [
        "Sport Seats",
        "Sport Seat",
        "Adaptive Sport Seats",
        "Sport Seats Plus",
    ],
}

