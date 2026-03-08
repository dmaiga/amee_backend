from django import forms
from django.forms import ModelForm
from roster.models import ConsultantProfile
from django.core.exceptions import ValidationError
from django.conf import settings

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 Mo

ALLOWED_EXTENSIONS = ["pdf", "doc", "docx", "jpg", "jpeg", "png"]

class ConsultantApplicationForm(ModelForm):

    class Meta:
        model = ConsultantProfile

        fields = [
            # ===== ELIGIBILITE =====
            "cv_document",
            "attestations",

            # ===== PROFIL CONSULTANT =====
            "titre_professionnel",
            "resume_public",
            "annees_experience_ees",
            "niveau_seniorite",
            "statut_professionnel",
            "domaines_expertise",
            "secteurs_experience",
            "experience_geographique",
            "langues",
            "certifications",

            "cv_public",
             
            "lien_linkedin",
            "consentement_publication",
        ]

        widgets = {
            "cv_document": forms.FileInput(), 
            "cv_public": forms.FileInput(),
            "resume_public": forms.Textarea(attrs={"rows": 4}),
            "secteurs_experience": forms.Textarea(attrs={"rows": 2}),
            "experience_geographique": forms.Textarea(attrs={"rows": 2}),
            "certifications": forms.Textarea(attrs={"rows": 2}),
            "attestations": forms.Textarea(attrs={"rows": 2}),
        }

    # ==================================================
    # DAISYUI AUTO STYLING
    # ==================================================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cv_document"].required = True
        
        self.fields["langues"].widget.attrs["placeholder"] = \
            "Ex : Français (maternelle), Anglais (intermédiaire)"
        
        self.fields["resume_public"].widget.attrs["placeholder"] = \
                    "Décrivez brièvement votre parcours et vos points forts en quelques lignes..."
        
        self.fields["domaines_expertise"].widget.attrs["placeholder"] = \
            "Ex : Évaluation de projets, Politiques publiques, Environnement"

        self.fields["secteurs_experience"].widget.attrs["placeholder"] = \
            "Ex : Industrie agroalimentaire, Secteur public, Bâtiments tertiaires"  
      
        self.fields["experience_geographique"].widget.attrs["placeholder"] = \
            "Ex : Mali, Sénégal, Côte d'Ivoire"
        
        self.fields["certifications"].widget.attrs["placeholder"] = \
            "Séparer chaque certification par une virgule."

        self.fields["attestations"].widget.attrs["placeholder"] = \
            "Séparer chaque élément par une virgule."
        
 
        for name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "toggle toggle-success"
                continue

            if isinstance(widget, forms.Select):
                widget.attrs["class"] = "select select-bordered w-full"
                continue

            if isinstance(widget, forms.FileInput):
                widget.attrs["class"] = "file-input file-input-bordered w-full"
                continue

            if isinstance(widget, forms.Textarea):
                widget.attrs["class"] = "textarea textarea-bordered w-full"
                continue

            widget.attrs["class"] = "input input-bordered w-full"

    # ==================================================
    # VALIDATION METIER
    # ==================================================
 
    def clean_cv_document(self):
        file = self.cleaned_data.get("cv_document")

        if not file:
            return file

        if file.size > MAX_FILE_SIZE:
            raise ValidationError("Le fichier dépasse 10 Mo.")

        ext = file.name.split(".")[-1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Format autorisé : PDF, Word ou image.")

        return file

    def clean_cv_public(self):
        file = self.cleaned_data.get("cv_public")

        if not file:
            return file

        if file.size > MAX_FILE_SIZE:
            raise ValidationError("Le fichier dépasse 10 Mo.")

        ext = file.name.split(".")[-1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Format autorisé : PDF, Word ou image.")

        return file
    
    # ==================================================
    # SAVE SIMPLE
    # ==================================================
    def save(self, user, commit=True):
        profil = super().save(commit=False)
        profil.user = user
        profil.statut = "SOUMIS"

        if commit:
            profil.full_clean()
            profil.save()

        return profil