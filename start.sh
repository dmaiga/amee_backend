#!/bin/bash
set -e

echo "🚀 Initialisation AMEE Backend..."

# ==============================
# MIGRATIONS
# ==============================
echo "🧱 Reset migration state (mode MVP)..."

# supprimer anciennes migrations générées dynamiquement
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete || true
find . -path "*/migrations/*.pyc" -delete || true


echo "🧱 Génération des migrations..."

python manage.py makemigrations --noinput || true

echo "📦 Application des migrations..."
python manage.py migrate --noinput

# ==============================
# SUPERUSER AUTO (si absent)
# ==============================
echo "👤 Vérification du superuser..."

python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(email="mdmaiga01@gmail.com").exists():
    print("Création du superuser...")
    User.objects.create_superuser(
        email="mdmaiga01@gmail.com",
        password="dadi123!",
        first_name="Dadi",
        last_name="Maiga",
        role="SUPERADMIN"
    )
    print("✅ Superuser créé")
else:
    print("ℹ️ Superuser déjà existant")
END

# ==============================
# STATIC FILES
# ==============================
echo "📂 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# ==============================
# LANCEMENT SERVEUR
# ==============================
echo "🚀 Lancement Gunicorn..."

exec python manage.py runserver 0.0.0.0:8000