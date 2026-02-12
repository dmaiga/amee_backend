from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        # --- Rôles Internes (Staff) ---
        ('SUPERADMIN', 'Administrateur Système'), # Developpeur & Admin technique
        ('BUREAU', 'Membre du Bureau / Conseil'), # Validation technique du Roster
        ('COMPTA', 'Comptabilité / Trésorerie'),  # Validation des paiements uniquement
        ('SECRETARIAT', 'Secrétariat Administratif'), # Gestion des dossiers courants

        # --- Rôles Externes (Membres & Clients) ---
        ('MEMBER', 'Membre Adhérent'),            # Statut par défaut après inscription
        ('CONSULTANT', 'Expert Roster'),          # Membre dont le profil Roster est validé
        ('CLIENT', 'Institution / Recruteur'),    # Public cible (ONG, État, etc.)
    )
    # Identifiant unique du membre tel que spécifié : MEM-2024-056 
    id_membre_association = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )
    # Utilisation d'UUID pour les URLs afin d'éviter les vulnérabilités IDOR
    external_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CLIENT'
    )
    is_active_account = models.BooleanField(default=True)
    
    email = models.EmailField(unique=True, max_length=255)
    
    # On rend l'username optionnel ou on le supprime
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    # CONFIGURATION CRUCIALE
    USERNAME_FIELD = 'email'  # L'email devient l'identifiant de connexion
    REQUIRED_FIELDS = ['first_name', 'last_name'] # Plus besoin d'username ici


    def __str__(self):
        return f"{self.username} ({self.id_membre_association}) - {self.get_role_display()}"