"""JobBoard NOTIFICATION: FastAPI service registered with Eureka via REST API."""

import asyncio
import json
import os
import socket
from contextlib import asynccontextmanager, suppress
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from fastapi import FastAPI

SERVICE_NAME = "NOTIFICATION"
VERSION = "1.0.0"
PORT = int(os.getenv("PORT", "8084"))
EUREKA_URL = os.getenv("EUREKA_URL", "http://localhost:8761/eureka").rstrip("/")
HOST_NAME = os.getenv("SERVICE_HOST", socket.gethostname())
SERVICE_IP = os.getenv("SERVICE_IP", "127.0.0.1")
INSTANCE_ID = f"{HOST_NAME}:{SERVICE_NAME.lower()}:{PORT}"
BASE_URL = f"http://{SERVICE_IP}:{PORT}"
REGISTRATION_URL = f"{EUREKA_URL}/apps/{SERVICE_NAME}"
INSTANCE_URL = f"{REGISTRATION_URL}/{quote(INSTANCE_ID, safe='')}"

INSTANCE = {
    "instanceId": INSTANCE_ID,
    "app": SERVICE_NAME,
    "hostName": HOST_NAME,
    "ipAddr": SERVICE_IP,
    "vipAddress": SERVICE_NAME.lower(),
    "secureVipAddress": SERVICE_NAME.lower(),
    "status": "UP",
    "port": {"$": PORT, "@enabled": "true"},
    "securePort": {"$": 443, "@enabled": "false"},
    "homePageUrl": f"{BASE_URL}/",
    "statusPageUrl": f"{BASE_URL}/info",
    "healthCheckUrl": f"{BASE_URL}/health",
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


async def eureka_register() -> bool:
    try:
        await asyncio.to_thread(
            eureka_request, "POST", REGISTRATION_URL, {"instance": INSTANCE}
        )
        print(f"[EUREKA] Registered {INSTANCE_ID} at {EUREKA_URL}", flush=True)
        return True
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        print(f"[EUREKA] Registration failed: {error}", flush=True)
        return False


async def eureka_heartbeat_loop() -> None:
    registered = False
    while True:
        if not registered:
            registered = await eureka_register()
            await asyncio.sleep(30 if registered else 5)
            continue
        try:
            await asyncio.to_thread(eureka_request, "PUT", INSTANCE_URL)
            print(f"[EUREKA] Heartbeat sent: {INSTANCE_ID}", flush=True)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            print(f"[EUREKA] Heartbeat failed: {error}; retrying registration", flush=True)
            registered = False
        await asyncio.sleep(30 if registered else 5)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(eureka_heartbeat_loop())
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


app = FastAPI(title="JobBoard Notification Service", version=VERSION, lifespan=lifespan)


@app.get("/")
def root():
    return {"service": SERVICE_NAME, "message": "Notification service is running"}


@app.get("/api/notifications/hello")
def hello():
    return {"message": "Hello from NOTIFICATION", "port": PORT}


@app.get("/health")
def health():
    return {"status": "UP", "service": SERVICE_NAME}


@app.get("/info")
def info():
    return {"name": "notification-service", "version": VERSION}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
