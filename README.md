# Projet Amee

Bienvenue dans le projet Amee. Ce projet est une application Django qui fournit des fonctionnalités d'authentification et de gestion des utilisateurs.

## Fonctionnalités

- Authentification avec JWT (JSON Web Token)
- Enregistrement des utilisateurs
- Points de terminaison API pour récupérer les informations utilisateur

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone <url-du-repo>
   ```
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Appliquez les migrations :
   ```bash
   python manage.py migrate
   ```
4. Lancez le serveur de développement :
   ```bash
   python manage.py runserver
   ```

## Utilisation

- Accédez à l'interface d'administration : `/admin/`
- Points de terminaison API :
  - `/api/auth/login/` : Connexion utilisateur
  - `/api/auth/refresh/` : Rafraîchir le token JWT
  - `/api/me/` : Récupérer les informations de l'utilisateur connecté
  - `/api/register/` : Enregistrer un nouvel utilisateur