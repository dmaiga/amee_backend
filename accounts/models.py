from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid


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

    # ❌ suppression réelle du username Django
    username = None

    ROLE_CHOICES = (
        ('SUPERADMIN', 'Administrateur Système'),
        ('BUREAU', 'Membre du Bureau / Conseil'),
        ('COMPTA', 'Comptabilité'),
        ('SECRETARIAT', 'Secrétariat Administratif'),
        ('MEMBER', 'Membre Adhérent'),
        ('CONSULTANT', 'Expert Roster'),
        ('CLIENT', 'Institution / Recruteur'),
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

    def __str__(self):
        return f"{self.email} - {self.get_role_display()}"
