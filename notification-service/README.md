# NOTIFICATION Service (Python / FastAPI)

Microservice de démonstration pour l'atelier JobBoard/Eureka.

## Prérequis

- Python >= 3.10
- Eureka Server lancé sur `http://localhost:8761`

## Démarrage (PowerShell, terminal dans ce dossier)

```powershell
python -m pip install -r requirements.txt
python main.py
```

Par défaut : port `8084` et nom Eureka `NOTIFICATION`.

## Test

- http://localhost:8084/hello
- http://localhost:8084/docs
- http://localhost:8761 (dashboard Eureka : `NOTIFICATION UP (1)`)

## Deuxième instance

Dans un **autre** terminal PowerShell, depuis le même dossier :

```powershell
$env:PORT=8094; python main.py
```

Le dashboard Eureka devrait afficher `NOTIFICATION UP (2)`.

## Variables d'environnement facultatives

`PORT` (8084), `EUREKA_URL` (`http://localhost:8761/eureka`), `SERVICE_HOST` (nom de machine), `SERVICE_IP` (`127.0.0.1`).

**Note :** `127.0.0.1` convient à un atelier sur une même machine. Pour Docker ou plusieurs machines, utiliser une adresse `SERVICE_IP` accessible aux autres services.
