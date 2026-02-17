# AMEE Platform

Plateforme backend de gestion du réseau d'experts AMEE.

L'application permet de gérer :

- les adhésions membres
- la validation des experts (Roster)
- la publication de besoins clients
- la mise en relation client-consultant
- le suivi des collaborations
- la trésorerie (adhésions, cotisations, dons et charges)

AMEE agit comme un tiers de confiance facilitant les mises en relation
sans intervenir dans la gestion contractuelle des missions.

---

## Stack Technique

- Django
- Django REST Framework
- JWT Authentication
- PostgreSQL / SQLite (dev)
- drf-spectacular (API Docs)
- pytest (tests)

---

## Architecture

### Apps principales

- `accounts` : utilisateurs, rôles et authentification
- `memberships` : état d'adhésion (activation, expiration, actif/inactif)
- `tresorerie` : transactions comptables et moteur d'adhésion/cotisation
- `roster` : validation des consultants
- `missions` : besoins exprimés par les clients
- `interactions` : mise en relation et suivi
- `quality_control` : gestion des feedbacks et incidents
- `cms` : gestion des contenus (articles, ressources, opportunités)

---

## Workflow

`Transaction ADHESION (VALIDEE)` -> création/liaison membre + ID `MEM-YYYY-XXX`  
`Transaction COTISATION (VALIDEE)` -> activation ou renouvellement adhésion (+365 jours)

Voir : `docs/workflow.md`

---

## Installation

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Tests :

```bash
uv run pytest
```

## Documentation API

Swagger : `/api/docs/`

Schema OpenAPI : `/api/schema/`
