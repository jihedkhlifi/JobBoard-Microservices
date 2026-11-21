# MEETING Service (Node.js / Express)

Microservice de démonstration pour l'atelier JobBoard/Eureka.

## Prérequis

- Node.js >= 18, npm
- Eureka Server lancé sur `http://localhost:8761`

## Démarrage (terminal dans ce dossier)

```bash
npm install
npm start
```

Par défaut : port `8083` et nom Eureka `MEETING`.

## Test

- http://localhost:8083/hello
- http://localhost:8083/health
- http://localhost:8761 (dashboard Eureka : `MEETING UP (1)`)

## Deuxième instance

Dans un **autre** terminal PowerShell, depuis le même dossier :

```powershell
$env:PORT=8093; npm start
```

On devrait observer `MEETING UP (2)` dans Eureka, avec les ports 8083 et 8093.

## Variables d'environnement facultatives

`PORT` (8083), `EUREKA_URL` (`http://localhost:8761/eureka`), `SERVICE_HOST` (nom de machine), `SERVICE_IP` (`127.0.0.1`).

**Note :** le mode `127.0.0.1` est adapté à un atelier où Eureka et les services tournent sur le même ordinateur. Pour des conteneurs ou machines différentes, définir `SERVICE_IP` avec une adresse joignable depuis les autres services.
