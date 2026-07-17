"""
FIFA World Cup 2026 Stadiums & Operational Data Store
Provides rich mock and real-time operational data for key 2026 World Cup Host Venues.
"""

STADIUMS = {
    "metlife": {
        "id": "metlife",
        "name": "MetLife Stadium (New York / New Jersey)",
        "city": "East Rutherford, NJ",
        "capacity": 82500,
        "role": "Final Match Host",
        "gates": [
            {"id": "Gate A", "name": "Verizon Gate A", "status": "Smooth", "queue_time_min": 4, "crowd_density": 35},
            {"id": "Gate B", "name": "SAP Gate B", "status": "Moderate", "queue_time_min": 12, "crowd_density": 68},
            {"id": "Gate C", "name": "MetLife Gate C", "status": "Congested", "queue_time_min": 22, "crowd_density": 89},
            {"id": "Gate D", "name": "Pepsi Gate D", "status": "Smooth", "queue_time_min": 6, "crowd_density": 42},
        ],
        "concessions": [
            {"id": "c1", "name": "Hudson Street Halal & Vegan", "section": "Sec 108", "wait_min": 5, "dietary": ["Halal", "Vegan", "Gluten-Free"], "rating": 4.8},
            {"id": "c2", "name": "Liberty Craft Burgers & Tacos", "section": "Sec 124", "wait_min": 15, "dietary": ["Kosher Available", "Standard"], "rating": 4.5},
            {"id": "c3", "name": "Empanada & Arepa Express", "section": "Sec 214", "wait_min": 8, "dietary": ["Gluten-Free", "Vegetarian"], "rating": 4.9},
            {"id": "c4", "name": "Hydration & Coffee Hub", "section": "Sec 302", "wait_min": 3, "dietary": ["Beverages"], "rating": 4.6},
        ],
        "accessibility": [
            {"type": "Elevator", "location": "Plaza Level Gate A & Gate C", "status": "Operational", "wheelchair_assisted": True},
            {"type": "Sensory Room", "location": "Section 218 Concierge", "status": "Open", "quiet_zone": True},
            {"type": "Audio Description Hub", "location": "Guest Services Sec 117", "status": "Broadcasting Live", "frequency": "FM 88.5"},
            {"type": "Accessible Restroom", "location": "Sections 104, 118, 220, 312", "status": "Operational", "wheelchair_assisted": True}
        ],
        "transit": [
            {"mode": "Meadowlands Rail Line", "status": "Active (Departures every 6 mins)", "eco_rating": "A+", "est_wait_min": 10, "carbon_kg": 0.4},
            {"mode": "NYC Express Fan Shuttle", "status": "Active (Dedicated lane)", "eco_rating": "A", "est_wait_min": 12, "carbon_kg": 1.1},
            {"mode": "Rideshare Hub (Lot E)", "status": "Surge High - 25 min wait", "eco_rating": "C", "est_wait_min": 25, "carbon_kg": 4.8},
            {"mode": "Pedestrian Green Corridor", "status": "Clear", "eco_rating": "A++", "est_wait_min": 0, "carbon_kg": 0.0}
        ]
    },
    "sofi": {
        "id": "sofi",
        "name": "SoFi Stadium (Los Angeles)",
        "city": "Inglewood, CA",
        "capacity": 70000,
        "role": "US Opening Match Host",
        "gates": [
            {"id": "Entry 1", "name": "American Airlines VIP Entry", "status": "Smooth", "queue_time_min": 3, "crowd_density": 28},
            {"id": "Entry 5", "name": "South Plaza Entry 5", "status": "Congested", "queue_time_min": 18, "crowd_density": 82},
            {"id": "Entry 9", "name": "Lake Park Pedestrian Entry", "status": "Moderate", "queue_time_min": 9, "crowd_density": 55},
        ],
        "concessions": [
            {"id": "c101", "name": "Baja Fish Tacos & Bowls", "section": "Sec 120", "wait_min": 6, "dietary": ["Halal", "Gluten-Free", "Pescatarian"], "rating": 4.9},
            {"id": "c102", "name": "Plant-Based LA Gourmet", "section": "Sec 204", "wait_min": 4, "dietary": ["100% Vegan", "Organic"], "rating": 4.8},
        ],
        "accessibility": [
            {"type": "Express ADA Shuttle", "location": "Lake Park Lot to Section 100", "status": "Operational", "wheelchair_assisted": True},
            {"type": "Visual Sign AI Kiosk", "location": "Main Concourse Entry 5", "status": "Active", "quiet_zone": False}
        ],
        "transit": [
            {"mode": "K-Line Light Rail Shuttle", "status": "Active", "eco_rating": "A+", "est_wait_min": 8, "carbon_kg": 0.3},
            {"mode": "LAX Express Fan Bus", "status": "Active", "eco_rating": "A", "est_wait_min": 15, "carbon_kg": 1.2}
        ]
    },
    "azteca": {
        "id": "azteca",
        "name": "Estadio Azteca (Mexico City)",
        "city": "Mexico City, Mexico",
        "capacity": 87523,
        "role": "Tournament Opening Match Host",
        "gates": [
            {"id": "Acceso 1", "name": "Calzada de Tlalpan", "status": "Moderate", "queue_time_min": 14, "crowd_density": 71},
            {"id": "Acceso 3", "name": "Insurgentes Sur", "status": "Smooth", "queue_time_min": 7, "crowd_density": 40},
        ],
        "concessions": [
            {"id": "c201", "name": "Tacos al Pastor & Elote", "section": "Grada Baja 10", "wait_min": 9, "dietary": ["Traditional", "Gluten-Free"], "rating": 4.9},
            {"id": "c202", "name": "Aguas Frescas & Fruit Hub", "section": "Grada Alta 4", "wait_min": 2, "dietary": ["Vegan", "Hydration"], "rating": 4.7},
        ],
        "accessibility": [
            {"type": "ADA Ramp North", "location": "Acceso 1 Main Gate", "status": "Operational", "wheelchair_assisted": True},
            {"type": "Braille & Audio Tour", "location": "Gate 3 Information Center", "status": "Active", "quiet_zone": True}
        ],
        "transit": [
            {"mode": "Tren Ligero (Estación Estadio Azteca)", "status": "High Frequency", "eco_rating": "A+", "est_wait_min": 5, "carbon_kg": 0.2},
            {"mode": "Metrobús Express Line", "status": "Active", "eco_rating": "A", "est_wait_min": 10, "carbon_kg": 0.6}
        ]
    }
}

INCIDENTS_MOCK = [
    {
        "id": "INC-2026-901",
        "stadium_id": "metlife",
        "timestamp": "20:45:12",
        "location": "Gate C - Turnstiles 7 & 8",
        "category": "Crowd Bottleneck / Scanner Malfunction",
        "severity": "High",
        "description": "Optical scanner offline on 2 turnstiles leading to 350+ fans queuing into North Plaza.",
        "status": "In Progress",
        "assigned_to": "Mobile Tech Team Alpha & Volunteer Group 4",
        "ai_recommendation": "Deploy auxiliary hand scanners from Gate A; broadcast push notification to redirect ticket holders to Gate B (wait time < 4 min)."
    },
    {
        "id": "INC-2026-902",
        "stadium_id": "metlife",
        "timestamp": "20:30:00",
        "location": "Section 114 Concourse",
        "category": "Medical Assist / Heat Stress",
        "severity": "Medium",
        "description": "Fan reporting dizziness near Concession 2.",
        "status": "Resolved",
        "assigned_to": "Stadium Paramedic Unit 2",
        "ai_recommendation": "Dispatched water distribution cart and escorted fan to Section 218 Sensory Cooling Hub."
    }
]
