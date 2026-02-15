from django.db import models
from django.utils.text import slugify
from django.utils import timezone

class Article(models.Model):
    TYPE_CHOICES = (
        ("ACTUALITE", "Actualité"),
        ("EVENEMENT", "Événement"),
        ("COMMUNIQUE", "Communiqué officiel"),
        ("OPPORTUNITE", "Opportunité"),
        ("FORMATION", "Formation / Atelier"),
        ("PARTENARIAT", "Partenariat"),
        ("APPEL", "Appel à participation"),
        ("AUTRE", "Autre"),
    )

    titre = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    contenu = models.TextField()
    image = models.ImageField(upload_to="cms/articles/", null=True, blank=True)
    publie = models.BooleanField(default=False)
    date_publication = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Laisser vide pour publier immédiatement"
    )
    
    lien_externe = models.URLField(
        blank=True,
        null=True,
        help_text="Lien externe (inscription, document officiel, partenaire...)"
    )
    
    publie_manuellement = models.BooleanField(
        default=False,
        help_text="Forcer la publication indépendamment de la date"
    )


    def save(self, *args, **kwargs):
    
        # ---------- SLUG ----------
        if not self.slug:
            base_slug = slugify(self.titre)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
    
        now = timezone.now()
    
        # ---------- LOGIQUE PUBLICATION ----------
        # 1️⃣ publication forcée depuis admin
        if self.publie:
            if not self.date_publication:
                self.date_publication = now
    
        # 2️⃣ publication programmée
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

    def __str__(self):
        return f"[{self.get_categorie_display()}] {self.titre}"


from django.utils import timezone

class Opportunity(models.Model):
    TYPE_CHOICES = (
        ("EMPLOI", "Offre d'emploi"),
        ("STAGE", "Stage"),
        ("APPEL_OFFRE", "Appel d'offre"),
        ("PARTENARIAT", "Coopération"),
    )

    titre = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_limite = models.DateField(null=True, blank=True)
    fichier_joint = models.FileField(upload_to="cms/opportunites/", null=True, blank=True)
    publie = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    @property
    def est_expire(self):
        if not self.date_limite:
            return False
        return self.date_limite < timezone.now().date()
