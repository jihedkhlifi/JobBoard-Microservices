'use strict';

const express = require('express');
const os = require('os');
const packageInfo = require('./package.json');

const app = express();
const port = Number(process.env.PORT || 8083);
const eurekaUrl = (process.env.EUREKA_URL || 'http://localhost:8761/eureka').replace(/\/$/, '');
const serviceName = 'MEETING';
const hostName = process.env.SERVICE_HOST || os.hostname();
const ipAddress = process.env.SERVICE_IP || '127.0.0.1'; // Atelier local (Eureka et services sur le même PC)
const instanceId = `${hostName}:${serviceName.toLowerCase()}:${port}`;
const serviceAddress = `http://${ipAddress}:${port}`;
const registrationEndpoint = `${eurekaUrl}/apps/${serviceName}`;
const instanceEndpoint = `${registrationEndpoint}/${encodeURIComponent(instanceId)}`;

app.use(express.json());

app.get('/', (_req, res) =>
    res.json({ service: serviceName, message: 'Meeting service is running' })
);

app.get('/api/meetings/hello', (_req, res) =>
    res.json({ message: 'Hello from MEETING', port })
);

app.get('/health', (_req, res) =>
    res.json({ status: 'UP', service: serviceName })
);

app.get('/info', (_req, res) =>
    res.json({
        name: packageInfo.name,
        version: packageInfo.version
    })
);

const instance = {
  instanceId,
  app: serviceName,
  hostName,
  ipAddr: ipAddress,
  vipAddress: serviceName.toLowerCase(),
  secureVipAddress: serviceName.toLowerCase(),
  status: 'UP',
  port: { '$': port, '@enabled': 'true' },
  securePort: { '$': 443, '@enabled': 'false' },
  homePageUrl: `${serviceAddress}/`,
    statusPageUrl: `${serviceAddress}/info`,
    healthCheckUrl: `${serviceAddress}/health`,
  dataCenterInfo: {
    '@class': 'com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo',
    name: 'MyOwn'
  },
  leaseInfo: { renewalIntervalInSecs: 30, durationInSecs: 90 }
};

let registered = false;
let stopping = false;
let heartbeatTimer;
let retryTimer;

async function eurekaRequest(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { Accept: 'application/json', ...(options.headers || {}) },
    signal: AbortSignal.timeout(5000)
  });
  if (!response.ok) {
    throw new Error(`Eureka HTTP ${response.status}`);
  }
  return response;
}

async function register() {
  if (stopping) return;
  try {
    await eurekaRequest(registrationEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ instance })
    });
    registered = true;
    console.log(`[EUREKA] ${instanceId} registered at ${eurekaUrl}`);
  } catch (error) {
    registered = false;
    console.warn(`[EUREKA] Registration failed: ${error.message}. Retrying in 5 seconds...`);
    clearTimeout(retryTimer);
    retryTimer = setTimeout(register, 5000);
  }
}

async function heartbeat() {
  if (stopping || !registered) return;
  try {
    await eurekaRequest(instanceEndpoint, { method: 'PUT' });
    console.log(`[EUREKA] Heartbeat sent: ${instanceId}`);
  } catch (error) {
    console.warn(`[EUREKA] Heartbeat failed: ${error.message}; registering again...`);
    registered = false;
    await register();
  }
}

const server = app.listen(port, async () => {
  console.log(`[MEETING] Listening on ${serviceAddress}`);
  await register();
  heartbeatTimer = setInterval(heartbeat, 30000);
});

async function shutdown() {
  if (stopping) return;
  stopping = true;
  clearInterval(heartbeatTimer);
  clearTimeout(retryTimer);
  try {
    if (registered) {
      await eurekaRequest(instanceEndpoint, { method: 'DELETE' });
      console.log('[EUREKA] Deregistered');
    }
  } catch (error) {
    console.warn(`[EUREKA] Deregistration failed: ${error.message}`);
  }
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(0), 2000).unref();
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);





