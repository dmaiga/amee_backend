# Workflow Fonctionnel - Plateforme AMEE

Ce document decrit le fonctionnement metier principal de la plateforme AMEE.

Objectif: faciliter la mise en relation entre institutions (clients) et experts valides du reseau AMEE, sans intervenir dans l'execution contractuelle des missions.

---

## 1. Inscription utilisateur

Un utilisateur cree un compte sur la plateforme.

Selon son usage, il devient:
- `CLIENT` (institution / recruteur)
- `MEMBER` (adherent AMEE)
- `CONSULTANT` (expert valide)

---

## 2. Adhesion (pilotee par la tresorerie)

L'adhesion est un evenement comptable porte par une `Transaction`:
- `type_transaction=ENTREE`
- `categorie=ADHESION`
- `statut=BROUILLON` puis validation en `VALIDEE`

Au passage `BROUILLON -> VALIDEE`, le moteur metier:
- cree (ou retrouve) l'utilisateur via `email_payeur`
- cree la fiche `Membership` si elle n'existe pas
- genere un identifiant membre `MEM-YYYY-XXX`
- rattache la transaction au membre

---

## 3. Cotisation (activation / renouvellement)

La cotisation est egalement une `Transaction` (`categorie=COTISATION`).

Au passage `BROUILLON -> VALIDEE`:
- l'adhesion est activee si elle etait inactive
- la date d'expiration est prolongee de 365 jours
- si une adhesion est deja active, le renouvellement part de la date d'expiration courante

Cas couvert par le moteur:
- une cotisation peut etre validee avant l'adhesion
- lors de la validation de l'adhesion, la cotisation deja validee est appliquee

---

## 4. Enrolement roster (consultant)

Le membre soumet son profil expert.

Le Bureau AMEE:
- valide ou refuse la candidature

Si valide:
- l'utilisateur devient `CONSULTANT` visible publiquement

---

## 5. Creation d'une mission (client)

Un client cree un besoin:
- titre
- description
- domaine
- localisation
- duree estimee

La mission represente un besoin, pas un contrat.

---

## 6. Mise en relation

Le client selectionne un consultant disponible.

La plateforme:
- enregistre une `ContactRequest`
- partage les coordonnees entre les parties
- demarre le suivi automatique

AMEE agit uniquement comme facilitateur.

---

## 7. Reponse du consultant

Depuis son espace personnel, le consultant indique:
- mission confirmee
- refus
- sans suite

Une mission confirmee devient une collaboration validee.

---

## 8. Suivi et feedback

Apres confirmation:
- le systeme envoie une demande d'evaluation au client
- les feedbacks alimentent la qualite du reseau

---

## 9. Controle qualite

Apres la fin d'une mission, un client peut fournir un feedback:
- note (1 a 5)
- commentaire
- signalement d'incident (optionnel)

Si un incident est signale:
- un `IncidentReview` est cree pour analyse
- un signalement peut etre genere avec des niveaux de gravite

Effets possibles:
- consultant sous surveillance
- suspension temporaire
- examen par le conseil AMEE

---

## 10. Gestion de contenu (CMS)

La plateforme permet de publier:
- articles (actualites, evenements, opportunites, etc.)
- ressources (guides, rapports, etudes de cas)
- opportunites (emplois, appels d'offres, partenariats)

Chaque contenu peut etre:
- publie immediatement ou programme
- reserve aux membres AMEE
- accompagne de fichiers joints ou liens externes

---

## 11. Pilotage backoffice (web)

Le workflow metier est pilote dans l'interface web backoffice:

- authentification: `/backoffice/login/`
- suivi global: `/backoffice/dashboard/`
- enrolement et paiements: `/backoffice/tresorerie/dashboard/`
- gestion membres: `/backoffice/membres/`
- validation roster: `/backoffice/roster/`
- suivi missions et feedbacks: `/backoffice/missions/`
- qualite et incidents: `/backoffice/qualite/incidents/`
- CMS interne: `/backoffice/cms/`
- organisations: `/backoffice/organisations/`

Reference detaillee des ecrans et routes:
- `docs/backoffice.md`

---

## Principe fondamental

AMEE:
- facilite la mise en relation
- assure la credibilite du reseau
- ne gere pas les contrats ni l'execution des missions
