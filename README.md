# JobBoard — Architecture Microservices avec Eureka

## 1. Présentation du projet

JobBoard est une plateforme de recrutement organisée selon une architecture microservices.

Ce projet a été réalisé dans le cadre de l'atelier **Implémentation Eureka Server** du module Architecture Web Distribuée.

L'objectif est de mettre en place un serveur Eureka permettant l'enregistrement et la découverte de microservices développés avec différentes technologies.

## 2. Architecture des microservices

| Microservice | Technologie | Port | Rôle |
|---|---|---|---|
| Discovery Server | Java / Spring Boot | 8761 | Registre Eureka |
| API Gateway | Java / Spring Cloud Gateway | 8080 | Point d'entrée et routage |
| CANDIDAT | Java / Spring Boot | 8081 | Gestion des candidats |
| JOB | Java / Spring Boot | 8082 | Gestion des offres d'emploi |
| CANDIDATURE | Java / Spring Boot | 8085 | Gestion des candidatures |
| MEETING | JavaScript / Node.js / Express | 8083 | Gestion des entretiens |
| NOTIFICATION | Python / FastAPI | 8084 | Gestion des notifications |

Les fonctionnalités métier complètes ne sont pas encore implémentées. Cet atelier se concentre sur le démarrage des services, leur enregistrement et leur découverte via Eureka.

## 3. Structure du projet

```text
jobboard-microservices-starter/
├── discovery-server/
├── api-gateway/
├── candidate-service/
├── job-service/
├── candidature-service/
├── meeting-service/
├── notification-service/
├── database/
├── screenshots/
├── pom.xml
├── .gitignore
└── README.md
```

Les services Java font partie du projet Maven. MEETING et NOTIFICATION utilisent leurs propres outils de gestion des dépendances.

## 4. Enregistrement auprès d'Eureka

Chaque microservice s'enregistre auprès du serveur Eureka accessible à l'adresse :

http://localhost:8761

L'enregistrement permet à Eureka de connaître le nom logique de chaque service, son adresse, son port et son état.

Les services envoient régulièrement des heartbeats afin de renouveler leur enregistrement.

Pour Spring Boot, nous utilisons Spring Cloud Eureka Client.

Pour Node.js et Python, l'enregistrement est effectué par le code des services via le protocole HTTP d'Eureka.

## 5. Démarrage des microservices

### Services Spring Boot

Dans IntelliJ IDEA, lancer :

1. `DiscoveryServerApplication`
2. `CandidateServiceApplication`
3. `JobServiceApplication`
4. `CandidatureServiceApplication`

L'API Gateway est également disponible dans le projet ; son routage métier sera étudié dans les ateliers suivants.

### MEETING — Node.js

Depuis le dossier `meeting-service` :

```powershell
npm install
npm start
```

MEETING démarre sur le port 8083.

### NOTIFICATION — Python

Depuis le dossier `notification-service` :

```powershell
python -m pip install -r requirements.txt
python main.py
```

NOTIFICATION démarre sur le port 8084.

## 6. Test de plusieurs instances

Pour démontrer la scalabilité horizontale, nous avons lancé deux instances du microservice CANDIDAT :

- Instance 1 : port 8081
- Instance 2 : port 8091

Nous avons également lancé deux instances de MEETING.

Pour lancer la deuxième instance de MEETING dans un nouveau terminal PowerShell :

```powershell
$env:PORT=8093
npm start
```

Les deux instances MEETING sont alors visibles dans Eureka sous le même nom logique.

## 7. Tests des endpoints REST

Les endpoints suivants ont été testés :

| Microservice | Endpoint | Résultat |
|---|---|---|
| MEETING instance 1 | `GET http://localhost:8083/api/meetings/hello` | Réponse JSON |
| MEETING instance 2 | `GET http://localhost:8093/api/meetings/hello` | Réponse JSON |
| NOTIFICATION | `GET http://localhost:8084/api/notifications/hello` | Réponse JSON |

Les deux instances de MEETING renvoient une réponse contenant leur port respectif, ce qui permet de vérifier leur fonctionnement indépendant.

## 8. Tableau de bord Eureka

Les services enregistrés lors de notre atelier sont :

| Service | Instances | Ports |
|---|---|---|
| CANDIDAT | 2 | 8081, 8091 |
| JOB | 1 | 8082 |
| CANDIDATURE | 1 | 8085 |
| MEETING | 2 | 8083, 8093 |
| NOTIFICATION | 1 | 8084 |

### Capture d'écran

![Dashboard Eureka](screenshots/eureka-dashboard.png)

Cette capture présente les instances enregistrées et leur état dans Eureka Server.

## 9. Concepts étudiés

- Architecture microservices
- Service Registry
- Service Registration
- Service Discovery
- Eureka Server et Eureka Client
- Heartbeat
- Scalabilité horizontale
- Instances multiples
- Interopérabilité entre Java, JavaScript et Python
- API REST

## 10. Limites et prochaines étapes

Le projet constitue une base pédagogique. Les fonctionnalités métier, les communications REST interservices, le Load Balancing et la persistance des données seront approfondis dans les ateliers suivants.

Le fait qu'un service apparaisse dans Eureka ne signifie pas encore qu'une communication métier complète entre les services a été implémentée.

## 11. Membres de l'équipe

Jihed Khlifi Ahmed Ayedi Insaf Makhloufi Ferdaous weslati

**Année universitaire :** 2026–2027  
**Module :** Architecture Web Distribuée  
**Atelier :** Implémentation Eureka Server