"""Microservice NOTIFICATION pour l'atelier JobBoard / Eureka (Python FastAPI)."""

import asyncio
import json
import os
import socket
from contextlib import asynccontextmanager, suppress
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import FastAPI

PORT = int(os.getenv("PORT", "8084"))
SERVICE = "NOTIFICATION"
EUREKA_URL = os.getenv("EUREKA_URL", "http://localhost:8761/eureka").rstrip("/")
HOST_NAME = os.getenv("SERVICE_HOST", socket.gethostname())
SERVICE_IP = os.getenv("SERVICE_IP", "127.0.0.1")  # Atelier local, même machine
INSTANCE_ID = f"{HOST_NAME}:{SERVICE.lower()}:{PORT}"
SERVICE_ADDRESS = f"http://{SERVICE_IP}:{PORT}"
REGISTRATION_URL = f"{EUREKA_URL}/apps/{SERVICE}"
INSTANCE_URL = f"{REGISTRATION_URL}/{INSTANCE_ID}"

INSTANCE = {
    "instanceId": INSTANCE_ID,
    "app": SERVICE,
    "hostName": HOST_NAME,
    "ipAddr": SERVICE_IP,
    "vipAddress": SERVICE.lower(),
    "secureVipAddress": SERVICE.lower(),
    "status": "UP",
    "port": {"$": PORT, "@enabled": "true"},
    "securePort": {"$": 443, "@enabled": "false"},
    "homePageUrl": f"{SERVICE_ADDRESS}/",
    "statusPageUrl": f"{SERVICE_ADDRESS}/health",
    "healthCheckUrl": f"{SERVICE_ADDRESS}/health",
    "dataCenterInfo": {
        "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
        "name": "MyOwn",
    },
    "leaseInfo": {"renewalIntervalInSecs": 30, "durationInSecs": 90},
}


def eureka_request(method: str, url: str, payload: dict | None = None) -> int:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=5) as response:
        return response.status


async def register() -> bool:
    try:
        await asyncio.to_thread(eureka_request, "POST", REGISTRATION_URL, {"instance": INSTANCE})
        print(f"[EUREKA] Registered {INSTANCE_ID} on {EUREKA_URL}", flush=True)
        return True
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        print(f"[EUREKA] Registration failed: {error}", flush=True)
        return False


async def heartbeat_loop() -> None:
    registered = False
    while True:
        if not registered:
            registered = await register()
            await asyncio.sleep(30 if registered else 5)
            continue
        try:
            await asyncio.to_thread(eureka_request, "PUT", INSTANCE_URL)
            print(f"[EUREKA] Heartbeat sent: {INSTANCE_ID}", flush=True)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            print(f"[EUREKA] Heartbeat failed: {error}. Registering again...", flush=True)
            registered = False
        await asyncio.sleep(30 if registered else 5)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(heartbeat_loop())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        try:
            await asyncio.to_thread(eureka_request, "DELETE", INSTANCE_URL)
            print(f"[EUREKA] Deregistered {INSTANCE_ID}", flush=True)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            print(f"[EUREKA] Deregistration failed: {error}", flush=True)


app = FastAPI(title="JobBoard Notification Service", lifespan=lifespan)


@app.get("/")
def home():
    return {"service": SERVICE, "message": "Notification service is running"}


@app.get("/api/notifications/hello")
def hello():
    return {"message": "Hello from NOTIFICATION", "port": PORT}


@app.get("/health")
def health():
    return {"status": "UP", "service": SERVICE}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)


