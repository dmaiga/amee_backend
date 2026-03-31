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
# gallery/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid

User = get_user_model()

def generate_unique_slug(instance, title_field, slug_field):
    MAX_SLUG_LENGTH = 255

    title = getattr(instance, title_field)
    if title and not getattr(instance, slug_field):

        base_slug = slugify(title)[:MAX_SLUG_LENGTH]
        slug = base_slug
        counter = 1

        ModelClass = instance.__class__

        filter_kwargs = {slug_field: slug}

        while ModelClass.objects.filter(**filter_kwargs).exclude(pk=instance.pk).exists():
            suffix = f"-{counter}"
            slug = f"{base_slug[:MAX_SLUG_LENGTH - len(suffix)]}{suffix}"
            filter_kwargs[slug_field] = slug
            counter += 1

        setattr(instance, slug_field, slug)

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
    slug = models.SlugField(max_length=255, blank=True)
    date_limite = models.DateField(null=True, blank=True)
    reserve_aux_membres = models.BooleanField(default=True)
    fichier_joint = models.FileField(upload_to="cms/opportunites/", null=True, blank=True)
    publie = models.BooleanField(default=True)
    lien_externe = models.CharField(
        blank=True,
        null=True,
        max_length=500,
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
    
    def save(self, *args, **kwargs):
        generate_unique_slug(self, 'titre_fr', 'slug_fr')
        generate_unique_slug(self, 'titre_en', 'slug_en')
        super().save(*args, **kwargs)

class Resource(models.Model):
    CATEGORIE_CHOICES = (
        ("GUIDE", "Guide technique"),
        ("RAPPORT", "Rapport d'évaluation"),
        ("REGLEMENT", "Texte réglementaire"),
        ("ETUDE_CAS", "Étude de cas"),
    )
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, blank=True)
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
    
    def save(self, *args, **kwargs):
        generate_unique_slug(self, 'titre_fr', 'slug_fr')
        generate_unique_slug(self, 'titre_en', 'slug_en')
        super().save(*args, **kwargs)


class Mandat(models.Model):
    nom = models.CharField(max_length=100)
    date_debut = models.DateField()
    date_fin = models.DateField()
    actif = models.BooleanField(default=True)

    mot_president = models.TextField(
        blank=True,
        help_text="Message officiel du président pour ce mandat"
    )

    def save(self, *args, **kwargs):
        if self.actif:
                    # On désactive tous les autres mandats actifs
            Mandat.objects.filter(actif=True).exclude(pk=self.pk).update(actif=False)
            super().save(*args, **kwargs)

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

class Gallery(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(
        default=False, 
        verbose_name="À la une",
        help_text="Mettre en avant cette galerie sur la page d'accueil"
    )
    cover_image = models.ImageField(
        upload_to='galleries/covers/', 
        blank=True, 
        null=True,
        verbose_name="Image de couverture",
        help_text="Image représentative de la galerie"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Créé par",
        related_name='created_galleries'
    )

    class Meta:
        verbose_name = "Galerie"
        verbose_name_plural = "Galeries"
        ordering = ['-created_at']
        permissions = [
            ("can_manage_all_galleries", "Peut gérer toutes les galeries"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Génération automatique du slug si vide
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            num = 1
            while Gallery.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
                num += 1
            self.slug = unique_slug
        
        # Si nouvelle galerie et created_by non défini
        if not self.pk and not self.created_by and hasattr(self, 'request_user'):
            self.created_by = self.request_user
        
        super().save(*args, **kwargs)

    @property
    def photo_count(self):
        """Retourne le nombre de photos dans la galerie"""
        return self.photos.count()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('gallery_detail', kwargs={'slug': self.slug})

class Photo(models.Model):
    gallery = models.ForeignKey(
        Gallery, 
        on_delete=models.CASCADE, 
        related_name='photos',
        blank=True,
        null=True,
        verbose_name="Galerie associée"
    )
    title = models.CharField(
        max_length=200, 
        verbose_name="Titre",
        help_text="Titre descriptif de la photo"
    )
    image = models.ImageField(
        upload_to='galleries/photos/%Y/%m/%d/',
        verbose_name="Fichier image"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Uploadé par",
        related_name='uploaded_photos'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_standalone = models.BooleanField(
        default=False,
        verbose_name="Photo indépendante",
        help_text="Cocher si cette photo n'appartient à aucune galerie"
    )
    tags = models.ManyToManyField(
        'PhotoTag',
        blank=True,
        verbose_name="Mots-clés"
    )

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"
        ordering = ['-uploaded_at']
        permissions = [
            ("can_manage_all_photos", "Peut gérer toutes les photos"),
        ]

    def __str__(self):
        return self.title or f"Photo #{self.id}"

    def save(self, *args, **kwargs):
        # Si nouvelle photo et uploaded_by non défini
        if not self.pk and not self.uploaded_by and hasattr(self, 'request_user'):
            self.uploaded_by = self.request_user
        
        # Vérification cohérence galerie/standalone
        if not self.gallery and not self.is_standalone:
            self.is_standalone = True
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('photo_detail', kwargs={'pk': self.pk})

class PhotoTag(models.Model):
    """Modèle pour les tags/catégories de photos"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tag photo"
        verbose_name_plural = "Tags photos"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)