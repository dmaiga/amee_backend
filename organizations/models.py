from django.db import models


class Organization(models.Model):

    nom = models.CharField(max_length=255)
    sigle = models.CharField(max_length=50, blank=True)

    site_web = models.URLField(blank=True)
    email_contact = models.EmailField()
    telephone = models.CharField(max_length=50, blank=True)
    siege= models.CharField(max_length=255, blank=True)
    est_actif = models.BooleanField(default=True)

    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
