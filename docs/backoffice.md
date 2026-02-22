# Documentation Backoffice AMEE

Ce document couvre l'interface web backoffice (templates Django) exposee sous `/backoffice/`.

## 1. Acces et securite

- Prefixe global: `/backoffice/` (configure dans `amee/urls.py`).
- Ecran de connexion: `/backoffice/login/`.
- La majorite des vues sont protegees par `@login_required`.
- Regle metier specifique roster:
  - la decision de validation/refus est reservee aux roles `SECRETARIAT`, `BUREAU`, `SUPERADMIN` (voir `backoffice/permissions/roster.py`).
- API tresorerie backoffice:
  - endpoint: `/backoffice/tresorerie/enregistrer-paiement/`
  - permissions: utilisateur authentifie + role `COMPTA` (voir `backoffice/permissions/roles.py`).

## 2. Tableau de bord

- `/backoffice/dashboard/`
- KPIs exposes:
  - membres actifs
  - consultants valides
  - dossiers roster en attente
  - taux de conversion membre -> consultant
  - solde de tresorerie
  - entrees des 30 derniers jours
  - missions ouvertes
  - nombre total de mises en relation
  - incidents a traiter

## 3. Tresorerie et enrolement

- `/backoffice/tresorerie/dashboard/`
  - suivi des individus et bureaux a jour / a relancer.
- `/backoffice/tresorerie/paiement/`
  - saisie paiement individuel (`FULL`, `ADHESION`, `COTISATION`).
- `/backoffice/tresorerie/transactions/`
  - liste des transactions + filtres + soldes.
- `/backoffice/tresorerie/transactions/<transaction_id>/`
  - detail transaction.
- `/backoffice/tresorerie/depense/`
  - saisie d'une depense (`SORTIE`).

Routes complementaires de paiement bureau (attention au chemin effectif):
- `/backoffice/backoffice/tresorerie/paiement-bureau/`
- `/backoffice/backoffice/tresorerie/paiement-bureau/<organisation_id>/`

Note: ces deux routes contiennent un double segment `backoffice/` car elles sont deja inclues sous le prefixe `/backoffice/`.

## 4. Espace membres

- `/backoffice/membres/`
  - liste reseau AMEE + clients externes
  - filtre optionnel par role.
- `/backoffice/membres/<user_id>/`
  - detail membre, adhesion, derniere transaction, statut roster.

## 5. Espace roster

- `/backoffice/roster/`
  - liste des profils consultants, filtre par statut.
- `/backoffice/roster/<profil_id>/`
  - detail d'un profil.
- `/backoffice/roster/<profil_id>/decision/` (`POST`)
  - action `valider` ou `refuser` (motif requis en cas de refus).

## 6. Missions et suivi

- `/backoffice/missions/`
  - liste missions avec compteur d'incidents signales.
- `/backoffice/missions/<mission_id>/`
  - detail mission + contacts associes + feedback/incidents.
- `/backoffice/contacts/<contact_id>/demander-feedback/`
  - declenche l'email de demande de feedback si mission terminee.

## 7. Qualite et incidents

- `/backoffice/qualite/incidents/`
  - liste des incidents.
- `/backoffice/qualite/feedback/<feedback_id>/`
  - detail feedback client.
- `/backoffice/qualite/incidents/<incident_id>/affecter/`
  - affectation de l'enqueteur.
- `/backoffice/qualite/incidents/<incident_id>/statuer/`
  - cloture incident et creation eventuelle d'un signalement.

## 8. CMS interne

- Dashboard:
  - `/backoffice/cms/`
- Articles:
  - `/backoffice/cms/articles/`
  - `/backoffice/cms/articles/create/`
  - `/backoffice/cms/articles/<article_id>/`
  - `/backoffice/cms/articles/<article_id>/edit/`
- Ressources:
  - `/backoffice/cms/ressources/`
  - `/backoffice/cms/ressources/create/`
  - `/backoffice/cms/ressources/<ressource_id>/`
  - `/backoffice/cms/ressources/<ressource_id>/edit/`
- Opportunities:
  - `/backoffice/cms/opportunities/`
  - `/backoffice/cms/opportunities/create/`
  - `/backoffice/cms/opportunities/<opportunity_id>/`
  - `/backoffice/cms/opportunities/<opportunity_id>/edit/`

## 9. Organisations

- `/backoffice/organisations/`
  - liste avec derniere cotisation calculee.
- `/backoffice/organisations/create/`
  - creation organisation.
- `/backoffice/organisations/<organisation_id>/`
  - detail + dernieres transactions.
- `/backoffice/organisations/<organisation_id>/edit/`
  - edition organisation, puis redirection vers paiement bureau.

## 10. Fichiers de reference

- Routes web: `backoffice/urls.py`
- Vues web: `backoffice/web_views.py`
- API tresorerie backoffice: `backoffice/api/tresorerie/views.py`
- Permissions:
  - `backoffice/permissions/roster.py`
  - `backoffice/permissions/roles.py`
