"""
Test the geocoding function with debugging
Run: python test_address.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests

def geocode_address(address_text: str):
    """Convert address to coordinates using OpenStreetMap Nominatim"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address_text,
            "format": "json",
            "limit": 1,
            "countrycodes": "ng"
        }
        headers = {"User-Agent": "GuardianAngelApp/1.0 (https://guardian-angel.com)"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            if results:
                return {
                    "lat": float(results[0]["lat"]),
                    "lng": float(results[0]["lon"]),
                    "formatted_address": results[0].get("display_name", address_text)
                }
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    return None

# ============================================
# Test addresses
# ============================================

test_addresses = [
    "12 Idowu Martins Street, Victoria Island, Lagos, Nigeria",
    "National Hospital, Abuja, Nigeria",
    "LUTH, Idi-Araba, Surulere, Lagos, Nigeria",
    "123 Main Street, New York, NY, USA",
]

print("=" * 60)
print("📍 TESTING GEOCODING FUNCTION")
print("=" * 60)

for address in test_addresses:
    print(f"\n🔍 Testing: {address}")
    result = geocode_address(address)
    
    if result:
        print(f"   ✅ Found!")
        print(f"   📍 Lat: {result['lat']}")
        print(f"   📍 Lng: {result['lng']}")
        print(f"   📍 Formatted: {result['formatted_address']}")
    else:
        print(f"   ❌ Not found")

print("\n" + "=" * 60)
print("✅ Test complete")