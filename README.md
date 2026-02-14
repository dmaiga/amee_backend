# AMEE Platform

Plateforme backend de gestion du réseau d’experts AMEE.

L’application permet de gérer :

- les adhésions membres
- la validation des experts (Roster)
- la publication de besoins clients
- la mise en relation client–consultant
- le suivi des collaborations

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

- **accounts** : utilisateurs, rôles et authentification
- **memberships** : gestion des adhésions AMEE
- **roster** : validation des consultants
- **missions** : besoins exprimés par les clients
- **interactions** : mise en relation et suivi

---

## Workflow

Client → Mission → ContactRequest → Consultant  
→ Collaboration confirmée → Feedback (v0.0.2)

Voir : `docs/workflow.md`

---

## Installation

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver


## Documentation API

Swagger :
/api/docs/

Schema OpenAPI :
/api/schema/