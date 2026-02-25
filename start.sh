#!/bin/bash
set -e

echo "🚀 Initialisation AMEE Backend..."

# ==============================
# MIGRATIONS
# ==============================

# Vérifier si des migrations manquent
echo "🔍 Vérification des migrations manquantes..."
if ! uv run  manage.py makemigrations --check --dry-run; then
    echo "⚠️ Aucune migration trouvée, génération en cours..."
    uv run manage.py makemigrations --noinput
fi

# Appliquer les migrations
echo "📦 Application des migrations..."
uv run manage.py migrate --noinput

# ==============================
# SUPERUSER AUTO (si absent)
# ==============================
echo "👤 Vérification du superuser..."

uv run manage.py shell << END
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
uv run manage.py collectstatic --noinput

# ==============================
# LANCEMENT SERVEUR
# ==============================
echo "🚀 Lancement Gunicorn..."

exec uv run manage.py runserver 0.0.0.0:8000