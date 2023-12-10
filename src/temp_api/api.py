"""Implement temperature API"""

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PUSHGATEWAY_ENDPOINT = "http://localhost:9091/"
PROMQL_ENDPOINT = "http://localhost:9090/api/v1/query"

registry = CollectorRegistry()
g = Gauge(
    "temperature",
    "Measured temperature",
    ["building", "room"],
    registry=registry,
)

app = FastAPI()


@app.get("/")
def ui_redirect():
    """Redirect / to Swagger UI"""
    return RedirectResponse(url="/docs")


@app.get("/temperature")
def read_temperature(building: str, room: str) -> float:
    """Read average temperature for building and room in the last 15 minutes."""
    response = requests.get(
        PROMQL_ENDPOINT,
        {
            "query": "avg_over_time(temperature{building='"
            + building
            + "',room='"
            + room
            + "'}[15m])"
        },
        timeout=30,
    )
    data = response.json()["data"]["result"]
    if data:
        return data[0]["value"][-1]
    raise HTTPException(status_code=404, detail="No data")


@app.post("/temperature")
def write_temperature(building: str, room: str, temp: float):
    """Write temperature for building and room"""
    g.labels(building=building, room=room).set(temp)
    push_to_gateway(PUSHGATEWAY_ENDPOINT, job="api", registry=registry)
