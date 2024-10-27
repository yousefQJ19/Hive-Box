import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app import app  

client = TestClient(app)

def test_version():
    """Test the /version endpoint."""
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == "v0.0.1"

@patch("app.requests.get") 
def test_temperature(mock_get):
    """Test the /temperature endpoint."""
   
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [
        {
            "sensors": [
                {
                    "unit": "°C",
                    "lastMeasurement": {"value": "20.0"}
                },
                {
                    "unit": "°C",
                    "lastMeasurement": {"value": "30.0"}
                }
            ]
        }
    ]
    
    response = client.get("/temperature")
    assert response.status_code == 200
    assert response.json()["average"] == 25.0  

@patch("app.requests.get") 
def test_readyz(mock_get):
    """Test the /readyz endpoint."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [
        {
            "sensors": [{}]  
        }
    ]

    response = client.get("/readyz")
    assert response.status_code == 200

@patch("app.requests.get")  
def test_metrics(mock_get):
    """Test the /metrics endpoint."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = '{"key": "value"}' 

    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {"key": "value"}  

@pytest.mark.parametrize("endpoint", ["/version", "/temperature", "/readyz", "/metrics"])
def test_all_endpoints(endpoint):
    """Test all defined endpoints for a successful response."""
    response = client.get(endpoint)
    assert response.status_code == 200
