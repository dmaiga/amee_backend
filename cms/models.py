# cms/models.py
from django.db import models
from django.utils.text import slugify

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

from django.db import models
from accounts.models import User
from memberships.models import Membership
from django.utils.translation import gettext_lazy as _
 
    

class Article(models.Model):
    TYPE_CHOICES = (
        ("ACTUALITE", _("Actualité")),
        ("EVENEMENT", _("Événement")),
        ("COMMUNIQUE", _("Communiqué officiel")),
        ("OPPORTUNITE", _("Opportunité")),
        ("FORMATION", _("Formation / Atelier")),
        ("PARTENARIAT", _("Partenariat")),
        ("APPEL", _("Appel à participation")),
        ("AUTRE", _("Autre")),
    )
    


    titre = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    contenu = models.TextField()
    image = models.ImageField(upload_to="cms/articles/", null=True, blank=True)
    lectures = models.PositiveIntegerField(default=0)    
    publie = models.BooleanField(default=False)
    
    date_publication = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Laisser vide pour publier immédiatement"
    )
    
    lien_externe = models.CharField(
        blank=True,
        null=True,
        max_length=500,
        help_text="Lien externe (inscription, document officiel, partenaire...)"
    )
    
    publie_manuellement = models.BooleanField(
        default=False,
        help_text="Forcer la publication indépendamment de la date"
    )
    
    publie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )



    def save(self, *args, **kwargs):
        MAX_SLUG_LENGTH = 255

        # Fonction interne pour générer un slug unique par langue
        def generate_unique_slug(title_field, slug_field_name):
            title_value = getattr(self, title_field)
            if title_value and not getattr(self, slug_field_name):
                base_slug = slugify(title_value)[:MAX_SLUG_LENGTH]
                slug = base_slug
                counter = 1

                # On vérifie l'unicité sur le champ spécifique (ex: slug_fr)
                filter_kwargs = {f"{slug_field_name}": slug}
                while Article.objects.filter(**filter_kwargs).exclude(pk=self.pk).exists():
                    suffix = f"-{counter}"
                    slug = f"{base_slug[:MAX_SLUG_LENGTH - len(suffix)]}{suffix}"
                    filter_kwargs[slug_field_name] = slug
                    counter += 1

                setattr(self, slug_field_name, slug)

        # ---------- GÉNÉRATION DES SLUGS ----------
        # On génère les slugs pour chaque langue définie dans modeltranslation
        generate_unique_slug('titre_fr', 'slug_fr')
        generate_unique_slug('titre_en', 'slug_en')

        # ---------- LOGIQUE PUBLICATION ----------
        now = timezone.now()

        if self.publie:
            if not self.date_publication:
                self.date_publication = now
        elif self.date_publication:
            if self.date_publication <= now:
                self.publie = True
            else:
                self.publie = False

        super().save(*args, **kwargs)



    def __str__(self):
        return self.titre

class Resource(models.Model):
    CATEGORIE_CHOICES = (
        ("GUIDE", "Guide technique"),
        ("RAPPORT", "Rapport d'évaluation"),
        ("REGLEMENT", "Texte réglementaire"),
        ("ETUDE_CAS", "Étude de cas"),
    )
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to="cms/resources/")
    categorie = models.CharField(max_length=30, choices=CATEGORIE_CHOICES)
    reserve_aux_membres = models.BooleanField(default=True)
    telechargements = models.PositiveIntegerField(default=0)
    cree_le = models.DateTimeField(auto_now_add=True)
    publie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"[{self.get_categorie_display()}] {self.titre}"

class Opportunity(models.Model):
    TYPE_CHOICES = (
        ("EMPLOI", "Offre d'emploi"),
        ("STAGE", "Stage"),
        ("APPEL_OFFRE", "Appel d'offre"),
        ("PARTENARIAT", "Collaboration"),
    )

    titre = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_limite = models.DateField(null=True, blank=True)
    reserve_aux_membres = models.BooleanField(default=True)
    fichier_joint = models.FileField(upload_to="cms/opportunites/", null=True, blank=True)
    publie = models.BooleanField(default=True)
    lien_externe = models.CharField(
        blank=True,
        null=True,
        help_text="Lien externe"
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    publie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    @property
    def est_expire(self):
        if not self.date_limite:
            return False
        return self.date_limite < timezone.now().date()

    @property
    def jours_restants(self):
        if not self.date_limite:
            return None
        return (self.date_limite - timezone.now().date()).days


class Mandat(models.Model):
    nom = models.CharField(max_length=100)
    date_debut = models.DateField()
    date_fin = models.DateField()
    actif = models.BooleanField(default=True)

    mot_president = models.TextField(
        blank=True,
        help_text="Message officiel du président pour ce mandat"
    )

    def clean(self):
        if self.actif:
            qs = Mandat.objects.filter(actif=True).exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("Un autre mandat est déjà actif.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
class BoardRole(models.Model):
    titre = models.CharField(max_length=150, unique=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordre"]

    def __str__(self):
        return self.titre
    
class BoardMembership(models.Model):
    membership = models.ForeignKey("memberships.Membership", on_delete=models.CASCADE)
    mandat = models.ForeignKey(Mandat, on_delete=models.CASCADE)
    role = models.ForeignKey(BoardRole, on_delete=models.PROTECT)

    date_nomination = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("mandat", "role")