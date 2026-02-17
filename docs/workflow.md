# Workflow Fonctionnel - Plateforme AMEE

Ce document décrit le fonctionnement métier principal de la plateforme AMEE.

L'objectif de la plateforme est de faciliter la mise en relation entre
des institutions (clients) et des experts validés du réseau AMEE,
sans intervenir dans l'exécution contractuelle des missions.

---

## 1. Inscription utilisateur

Un utilisateur crée un compte sur la plateforme.

Selon son usage, il devient :
- `CLIENT` (institution / recruteur)
- `MEMBER` (adhérent AMEE)
- `CONSULTANT` (expert validé)

---

## 2. Adhésion (pilotée par la trésorerie)

L'adhésion est un événement comptable porté par une `Transaction` :
- `type_transaction=ENTREE`
- `categorie=ADHESION`
- `statut=BROUILLON` puis validation en `VALIDEE`

Au passage `BROUILLON -> VALIDEE`, le moteur métier :
- crée (ou retrouve) l'utilisateur via `email_payeur`
- crée la fiche `Membership` si elle n'existe pas
- génère un identifiant membre `MEM-YYYY-XXX`
- rattache la transaction au membre

---

## 3. Cotisation (activation / renouvellement)

La cotisation est également une `Transaction` (`categorie=COTISATION`).

Au passage `BROUILLON -> VALIDEE` :
- l'adhésion est activée si elle était inactive
- la date d'expiration est prolongée de 365 jours
- si une adhésion est déjà active, le renouvellement part de la date d'expiration courante

Cas couvert par le moteur :
- une cotisation peut être validée avant l'adhésion
- lors de la validation de l'adhésion, la cotisation déjà validée est appliquée

---

## 4. Enrôlement Roster (Consultant)

Le membre soumet son profil expert.

Le Bureau AMEE :
- valide ou refuse la candidature

Si validé :
- l'utilisateur devient `CONSULTANT` visible publiquement

---

## 5. Création d'une Mission (Client)

Un client crée un besoin :
- titre
- description
- domaine
- localisation
- durée estimée

La mission représente un besoin,
pas un contrat.

---

## 6. Mise en relation

Le client sélectionne un consultant disponible.

La plateforme :
- enregistre une `ContactRequest`
- partage les coordonnées entre les parties
- démarre le suivi automatique

AMEE agit uniquement comme facilitateur.

---

## 7. Réponse du Consultant

Depuis son espace personnel, le consultant indique :
- Mission confirmée
- Refus
- Sans suite

Une mission confirmée devient une collaboration validée.

---

## 8. Suivi et Feedback

Après confirmation :
- le système envoie une demande d'évaluation au client
- les feedbacks alimentent la qualité du réseau

---

## 9. Contrôle Qualité

Après la fin d'une mission, un client peut fournir un feedback :
- Note (1 à 5)
- Commentaire
- Signalement d'incident (optionnel)

Si un incident est signalé :
- un `IncidentReview` est créé pour analyse
- un signalement peut être généré avec des niveaux de gravité

Effets possibles :
- consultant sous surveillance
- suspension temporaire
- examen par le conseil AMEE

---

## 10. Gestion de Contenu (CMS)

La plateforme permet de publier :
- articles (actualités, événements, opportunités, etc.)
- ressources (guides, rapports, études de cas)
- opportunités (emplois, appels d'offres, partenariats)

Chaque contenu peut être :
- publié immédiatement ou programmé
- réservé aux membres AMEE
- accompagné de fichiers joints ou liens externes

---

## Principe Fondamental

AMEE :
- facilite la mise en relation
- assure la crédibilité du réseau
- ne gère pas les contrats ni l'exécution des missions
