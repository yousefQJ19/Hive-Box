"""
This module handles the temperature and readyz endpoints for the API.
"""
from datetime import datetime, timedelta
import requests
from fastapi import FastAPI, HTTPException,Response



app = FastAPI()

VERSION = "v0.0.1"
CACHE_TIMEOUT = 300  

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
        result['status'] = "Good" 
    else:
        result['status'] = "Too hot"

    return result


sensebox_cache = {
    "timestamp": datetime.utcnow() - timedelta(minutes=6),  
    "data": [],
}

SENSEBOX_URL = "https://api.opensensemap.org/boxes"

def fetch_sensebox_status():
    """Fetch status of senseBoxes."""
    global sensebox_cache  

    current_time = datetime.utcnow()
    if (current_time - sensebox_cache['timestamp']).total_seconds() > CACHE_TIMEOUT:
        try:
            res = requests.get(SENSEBOX_URL, timeout=1000)
            if res.status_code == 200:
                sensebox_cache['data'] = res.json()
                sensebox_cache['timestamp'] = current_time
        except requests.RequestException:
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

    required_accessible_boxes = (total_senseboxes // 2) + 1

    if accessible_senseboxes < required_accessible_boxes:
        cache_age = (datetime.utcnow() - sensebox_cache['timestamp']).total_seconds()
        if cache_age > CACHE_TIMEOUT:
            raise HTTPException(status_code=503, detail="More than 50% of senseBoxes are not accessible, and cache is stale.")
    return {"status": "ok"} 



@app.get("/metrics")
def metrics() -> Response:
    """Fetch and return the raw response from the API."""
    SENSEBOX_URL = "https://api.opensensemap.org/boxes"
    try:
        res = requests.get(SENSEBOX_URL, timeout=10)
        if res.status_code == 200:
            return Response(content=res.text, media_type="application/json")
        else:
            return Response(content=f"Failed to fetch data, status code: {res.status_code}", 
                            media_type="text/plain", 
                            status_code=res.status_code)
    except requests.Timeout:
        return Response(content="Error: Request timed out", 
                        media_type="text/plain", 
                        status_code=504)