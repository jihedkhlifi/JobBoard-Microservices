# Database-per-Service (à implémenter ensemble)

- candidate-service -> candidate_db : candidate, address
- job-service -> job_db : job, category
- application-service -> application_db : application (candidateId et jobId, sans FK interservices)

Le ZIP initial `awd-monolith/database/awd_db.sql` reste la source de référence métier. Aucun schéma ni enregistrement de données n'a été migré dans ce starter. La connexion MySQL et les entités JPA seront ajoutées avec leur microservice pendant les ateliers.
