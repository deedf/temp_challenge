"""Implement temperature API."""

from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PUSHGATEWAY_ENDPOINT = "http://localhost:9091/"
PROMQL_ENDPOINT = "http://localhost:9090/api/v1/query"

requests_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create and destroy an async http client across the app lifespan."""
    global requests_client  # pylint: disable=global-statement
    requests_client = httpx.AsyncClient()
    yield
    await requests_client.aclose()


app = FastAPI(lifespan=lifespan)

registry = CollectorRegistry()
g = Gauge(
    "temperature",
    "Measured temperature",
    ["building", "room"],
    registry=registry,
)


@app.get("/")
async def ui_redirect():
    """Redirect / to Swagger UI"""
    return RedirectResponse(url="/docs")


@app.get("/temperature")
async def read_temperature(building: str, room: str) -> float:
    """Read average temperature for building and room in the last 15 minutes."""
    assert requests_client
    response = await requests_client.get(
        url=PROMQL_ENDPOINT,
        params={
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
async def write_temperature(building: str, room: str, temp: float) -> None:
    """Write temperature for building and room"""
    g.labels(building=building, room=room).set(temp)
    push_to_gateway(PUSHGATEWAY_ENDPOINT, job="api", registry=registry)
