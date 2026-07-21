"""
Nearest Clinic Finder - Global + Nigerian Focus
Works anywhere in the world with Nigerian emphasis.

Includes a two-level location fallback system:
  Level 1: GPS                (smartphone, via browser)
  Level 2: Registered Address (fallback for everyone else)
"""

import requests
import math
import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from auth import get_user_data

# ============================================
# NIGERIAN CLINICS DATABASE (For faster lookup)
# ============================================
NIGERIAN_CLINICS = [
    # Lagos
    {
        "name": "Lagos University Teaching Hospital (LUTH)",
        "lat": 6.5158,
        "lng": 3.3612,
        "address": "Idi-Araba, Surulere, Lagos",
        "phone": "+234 1 583 8000",
        "emergency_contact": "+234 1 583 8001",
        "type": "hospital",
        "country": "Nigeria",
        "state": "Lagos"
    },
    {
        "name": "Reddington Hospital",
        "lat": 6.4531,
        "lng": 3.4068,
        "address": "12 Idowu Martins Street, Victoria Island, Lagos",
        "phone": "+234 1 271 2345",
        "emergency_contact": "+234 1 271 2346",
        "type": "hospital",
        "country": "Nigeria",
        "state": "Lagos"
    },
    {
        "name": "St. Nicholas Hospital",
        "lat": 6.4535,
        "lng": 3.3980,
        "address": "57 Campbell Street, Lagos Island, Lagos",
        "phone": "+234 1 263 5145",
        "emergency_contact": "+234 1 263 5146",
        "type": "hospital",
        "country": "Nigeria",
        "state": "Lagos"
    },
    {
        "name": "Eko Hospital",
        "lat": 6.4315,
        "lng": 3.4268,
        "address": "31 Mobolaji Bank Anthony Way, Ikeja, Lagos",
        "phone": "+234 1 291 4091",
        "emergency_contact": "+234 1 291 4092",
        "type": "hospital",
        "country": "Nigeria",
        "state": "Lagos"
    },
    {
        "name": "Lagos State University Teaching Hospital (LASUTH)",
        "lat": 6.5700,
        "lng": 3.3760,
        "address": "Ikeja, Lagos",
        "phone": "+234 1 773 0000",
        "emergency_contact": "+234 1 773 0001",
        "type": "hospital",
        "country": "Nigeria",
        "state": "Lagos"
    },

    # Abuja
    {
        "name": "National Hospital Abuja",
        "lat": 9.0481,
        "lng": 7.4767,
        "address": "Plot 132, Central District, Abuja",
        "phone": "+234 9 523 9000",
        "emergency_contact": "+234 9 523 9001",
        "type": "hospital",
        "country": "Nigeria",
        "state": "FCT"
    },
    {
        "name": "Garki Hospital Abuja",
        "lat": 9.0400,
        "lng": 7.4700,
        "address": "Garki Area 10, Abuja",
        "phone": "+234 9 290 3333",
        "emergency_contact": "+234 9 290 3334",
        "type": "hospital",
        "country": "Nigeria",
        "state": "FCT"
    },

    # Port Harcourt
    {
        "name": "University of Port Harcourt Teaching Hospital (UPTH)",
        "lat": 4.8020,
        "lng": 7.0060,
        "address": "Choba, Port Harcourt, Rivers State",
        "phone": "+234 84 232 191",
        "emergency_contact": "+234 84 232 192",
        "type": "hospital",
        "country": "Nigeria",
        "state": "Rivers"
    },
    {
        "name": "Braithwaite Memorial Specialist Hospital",
        "lat": 4.7900,
        "lng": 7.0250,
        "address": "Old GRA, Port Harcourt, Rivers State",
        "phone": "+234 84 233 400",
        "emergency_contact": "+234 84 233 401",
        "type": "hospital",
        "country": "Nigeria",
        "state": "Rivers"
    },

    # Ibadan
    {
        "name": "University College Hospital (UCH) Ibadan",
        "lat": 7.3880,
        "lng": 3.8960,
        "address": "Queen Elizabeth Road, Ibadan, Oyo State",
        "phone": "+234 2 241 1768",
        "emergency_contact": "+234 2 241 1769",
        "type": "hospital",
        "country": "Nigeria",
        "state": "Oyo"
    },

    # Kano
    {
        "name": "Aminu Kano Teaching Hospital",
        "lat": 11.9960,
        "lng": 8.5480,
        "address": "Zaria Road, Kano",
        "phone": "+234 64 666 000",
        "emergency_contact": "+234 64 666 001",
        "type": "hospital",
        "country": "Nigeria",
        "state": "Kano"
    },

    # Enugu
    {
        "name": "University of Nigeria Teaching Hospital (UNTH)",
        "lat": 6.4300,
        "lng": 7.5100,
        "address": "Ituku-Ozalla, Enugu",
        "phone": "+234 42 253 300",
        "emergency_contact": "+234 42 253 301",
        "type": "hospital",
        "country": "Nigeria",
        "state": "Enugu"
    },
]

# ============================================
# GLOBAL EMERGENCY NUMBERS
# ============================================
EMERGENCY_NUMBERS = {
    "Nigeria": {
        "ambulance": "112",
        "police": "199",
        "fire": "112",
        "general": "112",
        "ncdc": "0800 970 0000",
        "red_cross": "0800 732 7677"
    },
    "United States": {"ambulance": "911", "police": "911", "fire": "911", "general": "911"},
    "United Kingdom": {"ambulance": "999", "police": "999", "fire": "999", "general": "112"},
    "Canada": {"ambulance": "911", "police": "911", "fire": "911", "general": "911"},
    "Australia": {"ambulance": "000", "police": "000", "fire": "000", "general": "000"},
    "South Africa": {"ambulance": "10177", "police": "10111", "fire": "10177", "general": "112"},
    "India": {"ambulance": "102", "police": "100", "fire": "101", "general": "112"},
    "Kenya": {"ambulance": "999", "police": "999", "fire": "999", "general": "112"},
    "Ghana": {"ambulance": "193", "police": "191", "fire": "192", "general": "112"},
    "Egypt": {"ambulance": "123", "police": "122", "fire": "180", "general": "112"},
    "Brazil": {"ambulance": "192", "police": "190", "fire": "193", "general": "112"},
    "France": {"ambulance": "15", "police": "17", "fire": "18", "general": "112"},
    "Germany": {"ambulance": "112", "police": "110", "fire": "112", "general": "112"},
    "Japan": {"ambulance": "119", "police": "110", "fire": "119", "general": "119"},
    "China": {"ambulance": "120", "police": "110", "fire": "119", "general": "120"},
    "Default": {"ambulance": "112", "police": "112", "fire": "112", "general": "112"}
}

# ============================================
# DISTANCE CALCULATION
# ============================================
def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two GPS coordinates in kilometers."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ============================================
# DETECT COUNTRY FROM GPS
# ============================================
def detect_country_from_coords(lat: float, lng: float) -> str:
    """Detect country from GPS coordinates using reverse geocoding."""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lng, "format": "json", "accept-language": "en"}
        response = requests.get(url, params=params, timeout=5, headers={"User-Agent": "GuardianAngel/2.0"})
        if response.status_code == 200:
            data = response.json()
            return data.get("address", {}).get("country", "Default")
    except Exception:
        pass
    return "Default"

# ============================================
# FIND CLINICS - GLOBAL + NIGERIAN EMPHASIS
# ============================================
def find_clinics_openstreetmap(lat: float, lng: float, radius_km: float = 5.0) -> List[Dict]:
    """Find clinics using OpenStreetMap (works worldwide)."""
    radius_m = radius_km * 1000
    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lng});
      node["amenity"="clinic"](around:{radius_m},{lat},{lng});
    );
    out body;
    """

    try:
        response = requests.get(overpass_url, params={"data": query}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            clinics = []
            for element in data.get("elements", []):
                tags = element.get("tags", {})
                clinics.append({
                    "name": tags.get("name", "Unknown Clinic"),
                    "lat": element.get("lat", 0),
                    "lng": element.get("lon", 0),
                    "address": tags.get("addr:full", tags.get("addr:street", "N/A")),
                    "phone": tags.get("phone", "N/A"),
                    "type": "clinic" if tags.get("amenity") == "clinic" else "hospital",
                    "source": "OpenStreetMap"
                })
            return clinics
        return []
    except Exception:
        return []

def find_nearest_clinic(lat: float, lng: float, radius_km: float = 5.0) -> Optional[Dict]:
    """Find nearest clinic. Prioritizes Nigerian clinics if in Nigeria."""
    country = detect_country_from_coords(lat, lng)

    if country == "Nigeria":
        nigeria_clinics = []
        for clinic in NIGERIAN_CLINICS:
            distance = haversine(lat, lng, clinic["lat"], clinic["lng"])
            if distance <= radius_km:
                nigeria_clinics.append({**clinic, "distance_km": round(distance, 2)})

        if nigeria_clinics:
            nigeria_clinics.sort(key=lambda x: x["distance_km"])
            return nigeria_clinics[0]

    osm_clinics = find_clinics_openstreetmap(lat, lng, radius_km)
    if osm_clinics:
        for clinic in osm_clinics:
            clinic["distance_km"] = round(haversine(lat, lng, clinic["lat"], clinic["lng"]), 2)
        osm_clinics.sort(key=lambda x: x["distance_km"])
        return osm_clinics[0]

    return None

# ============================================
# GET EMERGENCY NUMBER BY COUNTRY
# ============================================
def get_emergency_number(lat: float, lng: float) -> Dict:
    """Get emergency numbers for the current country."""
    country = detect_country_from_coords(lat, lng)
    return EMERGENCY_NUMBERS.get(country, EMERGENCY_NUMBERS["Default"])


# ============================================================================
# TWO-LEVEL LOCATION SYSTEM
# Level 1: GPS  →  Level 2: Registered Address
#
# A third "cell tower" level was considered but dropped: resolving a phone
# number to a location via cell towers isn't something any public API
# provides — that capability belongs to telecom operators (or SS7-based
# services aimed at law enforcement, not a consumer health app). Rather than
# fake that level, a saved registered address is both more honest and more
# reliable as the fallback.
# ============================================================================

# ---------- Level 1: GPS (smartphone) ----------
def get_gps_location(browser_coords: Optional[Dict] = None) -> Optional[Dict]:
    """
    Return GPS coordinates already captured by the browser.

    Python running on the server has no direct access to a device's GPS chip —
    only the browser does. `browser_coords` should come from a JS geolocation
    component such as the `streamlit-geolocation` package:

        from streamlit_geolocation import streamlit_geolocation
        coords = streamlit_geolocation()   # returns {'latitude':.., 'longitude':.., ...}
        gps = get_gps_location({"lat": coords.get("latitude"), "lng": coords.get("longitude")})
    """
    if browser_coords and browser_coords.get("lat") is not None and browser_coords.get("lng") is not None:
        return {
            "lat": browser_coords["lat"],
            "lng": browser_coords["lng"],
            "accuracy": browser_coords.get("accuracy", "High (~10m)")
        }
    return None


# ---------- Level 2: Registered address (fallback) ----------
def get_registered_address(user_id: str) -> Optional[Dict]:
    """Get the user's saved home address/coordinates from their profile."""
    try:
        user_data = get_user_data(user_id)
        address = (user_data or {}).get("address", {})
        if address.get("lat") is not None and address.get("lng") is not None:
            return {
                "lat": address["lat"],
                "lng": address["lng"],
                "address": address.get("formatted_address", "N/A"),
                "accuracy": "Approximate (~100m, Registered Address)"
            }
    except Exception:
        pass
    return None


# ---------- Orchestrator ----------
def get_user_location(user_id: str, browser_gps: Optional[Dict] = None) -> Dict:
    """
    Resolve the best available location for a user:
    Level 1 GPS → Level 2 Registered Address.

    Returns:
        {"lat": float|None, "lng": float|None, "method": str, "accuracy": str}
    """
    gps = get_gps_location(browser_gps)
    if gps:
        return {"lat": gps["lat"], "lng": gps["lng"], "method": "GPS", "accuracy": gps["accuracy"]}

    address = get_registered_address(user_id)
    if address:
        return {
            "lat": address["lat"], "lng": address["lng"],
            "method": "Registered Address", "accuracy": address["accuracy"]
        }

    return {"lat": None, "lng": None, "method": "None", "accuracy": "Unknown — no location source available"}


# ============================================
# BUILD EMERGENCY MESSAGE
# ============================================
def build_emergency_message(user_name: str, risk_level: str, confidence: float,
                             gps_link: str, clinic: Dict, country: str,
                             location_method: str = "GPS") -> str:
    """Build emergency SMS message with clinic and emergency info."""

    emergency_num = EMERGENCY_NUMBERS.get(country, EMERGENCY_NUMBERS["Default"])

    clinic_block = ""
    if clinic:
        clinic_block = f"""
🏥 NEAREST MEDICAL FACILITY:
Name: {clinic.get('name', 'Unknown')}
Distance: {clinic.get('distance_km', 'N/A')} km
Phone: {clinic.get('phone', 'N/A')}
Address: {clinic.get('address', 'N/A')}
"""
    else:
        clinic_block = "\n⚠️ No clinic found within 5km.\n"

    message = f"""
🚨 GUARDIAN ANGEL EMERGENCY ALERT 🚨

👤 User: {user_name}
📍 Risk Level: {risk_level}
📊 Confidence: {confidence * 100:.1f}%
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📍 GPS Location: {gps_link}
📡 Location Source: {location_method}
{clinic_block}
📞 EMERGENCY NUMBERS ({country}):
Ambulance: {emergency_num.get('ambulance', '112')}
Police: {emergency_num.get('police', '112')}
Fire: {emergency_num.get('fire', '112')}

⚠️ This is an automated emergency alert.
Please dispatch emergency services immediately.
"""
    return message

# ============================================
# CLINIC DASHBOARD UI
# ============================================
def clinic_dashboard_ui():
    """Streamlit UI for clinic dashboard."""
    st.markdown("### 🏥 Clinic Emergency Dashboard")
    st.markdown("---")

    st.info("📋 This dashboard shows incoming emergency alerts from Guardian Angel users.")

    with st.expander("🏥 Nigerian Clinics in Database"):
        df = pd.DataFrame(NIGERIAN_CLINICS)
        st.dataframe(df[["name", "state", "phone", "emergency_contact"]], use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📞 Recent Alerts")
    alerts = []
    if alerts:
        df_alerts = pd.DataFrame(alerts)
        st.dataframe(df_alerts, use_container_width=True)
    else:
        st.success("✅ No incoming emergencies. All clear!")

# ============================================
# GLOBAL EMERGENCY NUMBERS DISPLAY
# ============================================
def emergency_numbers_display(lat: float, lng: float, location_method: str = None):
    """Display emergency numbers for current location."""
    country = detect_country_from_coords(lat, lng)
    numbers = get_emergency_number(lat, lng)

    method_line = f'<p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #5B6B62;">📡 Location source: {location_method}</p>' if location_method else ""

    st.markdown(f"""
        <div style="background: #E4F1EC; padding: 15px; border-radius: 10px; border-left: 4px solid #1F6F5C;">
            <h4 style="color: #1F6F5C; margin: 0;">📞 Emergency Numbers in {country}</h4>
            <p style="margin: 5px 0;">
                <strong>Ambulance:</strong> {numbers.get('ambulance', '112')} &nbsp;|&nbsp;
                <strong>Police:</strong> {numbers.get('police', '112')} &nbsp;|&nbsp;
                <strong>Fire:</strong> {numbers.get('fire', '112')}
            </p>
            <p style="margin: 0; font-size: 0.85rem; color: #5B6B62;">General Emergency: {numbers.get('general', '112')}</p>
            {method_line}
        </div>
    """, unsafe_allow_html=True)