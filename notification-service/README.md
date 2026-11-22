# NOTIFICATION — JobBoard (FastAPI + Eureka)

Microservice Python pour les ateliers JobBoard. Port par défaut : **8084** ; nom enregistré dans Eureka : **NOTIFICATION**.

## Démarrer sous PowerShell

Démarrer Eureka Server sur `http://localhost:8761` avant NOTIFICATION.

```powershell
cd .\notification-service
python -m pip install -r requirements.txt
python main.py
```

Le terminal doit afficher `Uvicorn running ... :8084` puis `[EUREKA] Registered ...notification:8084`.

## Endpoints

- `http://localhost:8084/health` → `{"status":"UP","service":"NOTIFICATION"}`
- `http://localhost:8084/info` → `{"name":"notification-service","version":"1.0.0"}`
- `http://localhost:8084/api/notifications/hello` → message de test.

Le registre `http://localhost:8761/eureka/apps/NOTIFICATION` contient les URLs `healthCheckUrl=/health` et `statusPageUrl=/info`. Eureka reçoit un enregistrement HTTP `POST`, des renouvellements `PUT` et une désinscription `DELETE` à l'arrêt normal.

## Configuration facultative

- `PORT` (défaut `8084`)
- `EUREKA_URL` (défaut `http://localhost:8761/eureka`)
- `SERVICE_HOST` (défaut nom de l'ordinateur)
- `SERVICE_IP` (défaut `127.0.0.1`, uniquement pour un atelier local sur la même machine)

Exemple de seconde instance dans un autre terminal :

```powershell
$env:PORT=8094
python main.py
```

## Remarque par rapport au PDF de l'atelier

Le sujet mentionne `py-eureka-client` et `eureka_client.init(...)`. Cette version conserve volontairement une implémentation directe **de l'API REST Eureka** avec la bibliothèque standard Python (`urllib`), qui a déjà fonctionné dans notre atelier. Les champs Eureka `healthCheckUrl` et `statusPageUrl`, le lifecycle FastAPI, les heartbeats et la désinscription sont présents. Si le professeur exige l'utilisation littérale de `py-eureka-client`, cette implémentation doit être adaptée.

## IntelliJ IDEA

Le ZIP ne configure pas automatiquement l'interpréteur dans IntelliJ. Pour faire disparaître les avertissements `No module named 'os'` ou `Unresolved reference 'int'`, associer au **module Python** le même interpréteur que celui de PowerShell : `C:\Python315\python.exe`. Ne pas remplacer le SDK Java des modules Spring Boot.
