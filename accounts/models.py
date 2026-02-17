# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
from django.utils.text import slugify

from quality_control.models import Feedback



# =====================================================
# Custom User Manager (LOGIN PAR EMAIL)
# =====================================================

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Un email est obligatoire.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# =====================================================
# Custom User Model
# =====================================================

class User(AbstractUser):


    ROLE_CHOICES = (
        
        ('SUPERADMIN', 'Administrateur Système'),
        ('BUREAU', 'Membre du Bureau / Conseil'),
        ('COMPTA', 'Comptabilité'),

        ('SECRETARIAT', 'Secrétariat Administratif'),
        ('MEMBER', 'Membre Adhérent'),
        ('CONSULTANT', 'Expert Roster'),
        ('CLIENT', 'Institution / Recruteur'),
    )

    STATUT_QUALITE = (
        ("NORMAL", "Normal"),
        ("SURVEILLANCE", "Sous surveillance"),
        ("SUSPENDU", "Suspendu"),
        ("BANNI", "Banni"),
    )
    
    statut_qualite = models.CharField(
        max_length=20,
        choices=STATUT_QUALITE,
        default="NORMAL"
    )
    
    # username conservé mais auto-généré
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True
    )

    email = models.EmailField(unique=True, max_length=255)

    id_membre_association = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

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

    # LOGIN PAR EMAIL
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    # ============================
    # AUTO USERNAME GENERATION
    # ============================
    def generate_username(self):
        base_username = slugify(f"{self.first_name}{self.last_name}") or "user"
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exclude(pk=self.pk).exists():
            username = f"{base_username}{counter}"
            counter += 1

        return username

    def save(self, *args, **kwargs):
        # Génère username seulement s'il est vide
        if not self.username:
            self.username = self.generate_username()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} - {self.get_role_display()}"

    @property
    def est_recommande_amee(self):
    
        if self.role != "CONSULTANT":
            return False
    
        feedbacks = Feedback.objects.filter(
            contact_request__consultant=self,
            note__gte=4
        )
    
        return feedbacks.count() >= 5
    