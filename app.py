"""
This module handles the temperature and readyz endpoints for the API.
"""
from datetime import datetime, timedelta
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()

VERSION = "v3.2.1"
CACHE_TIMEOUT = 300  # Cache timeout set to 5 minutes

@app.get("/version")
def version() -> str:
    """Returns version"""
    return VERSION

@app.get("/temperature")
def temperature() -> dict:
    """Fetches temperature data from senseBoxes."""
    result = {"average": 0, "status": ""}
    phenomenon = "temperature"
    date = datetime.now().isoformat() + 'Z'

    res = requests.get(
        f"https://api.opensensemap.org/boxes?date={date}&phenomenon={phenomenon}",
        timeout=1000
    )
    
    all_boxes = res.json()
    c_count = 0
    c_total = 0

    for box in all_boxes:
        if 'sensors' not in box.keys():
            continue
        for sensor in box['sensors']:
            if 'unit' in sensor.keys() and 'lastMeasurement' in sensor.keys():
                if sensor['unit'] == '°C':
                    c_count += 1
                    c_total += float(sensor['lastMeasurement']['value'])

    if c_count == 0:
        return {"message": "No temperature data found."}

    result['average'] = c_total / c_count

    if result['average'] <= 10:
        result['status'] = "Too cold"
    elif 11 <= result['average'] <= 36:
        result['status'] = "good"
    else:
        result['status'] = "Too hot"

    return result

sensebox_cache = {
    "timestamp": datetime.utcnow() - timedelta(minutes=6),  # Initialize with an old timestamp
    "data": [],
}
SENSEBOX_URL = "https://api.opensensemap.org/boxes"

def fetch_sensebox_status():
    """Fetch status of senseBoxes."""
    global sensebox_cache  # Use the global cache variable

    # Check if the cache is older than CACHE_TIMEOUT
    current_time = datetime.utcnow()
    if (current_time - sensebox_cache['timestamp']).total_seconds() > CACHE_TIMEOUT:
        try:
            res = requests.get(SENSEBOX_URL, timeout=1000)
            if res.status_code == 200:
                sensebox_cache['data'] = res.json()
                sensebox_cache['timestamp'] = current_time
        except requests.RequestException:
            # In case of failure to fetch data, keep the old cache and do not update it
            pass

    return sensebox_cache['data']

@app.get("/readyz")
def readyz():
    """Returns status 200 unless more than 50% of senseBoxes are not accessible."""
    sensebox_data = fetch_sensebox_status()

    total_senseboxes = len(sensebox_data)
    if total_senseboxes == 0:
        raise HTTPException(status_code=503, detail="No senseBoxes available.")

    accessible_senseboxes = 0
    for box in sensebox_data:
        if 'sensors' in box.keys():
            accessible_senseboxes += 1

    # Determine if more than 50% + 1 senseBoxes are accessible
    required_accessible_boxes = (total_senseboxes // 2) + 1

    # Check if conditions for failure are met
    if accessible_senseboxes < required_accessible_boxes:
        # Check if the cache is older than CACHE_TIMEOUT
        cache_age = (datetime.utcnow() - sensebox_cache['timestamp']).total_seconds()
        if cache_age > CACHE_TIMEOUT:
            raise HTTPException(status_code=503, detail="More than 50% of senseBoxes are not accessible, and cache is stale.")

    return {"status": "ok"}
