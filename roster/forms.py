from django import forms
from django.forms import ModelForm
from roster.models import ConsultantProfile


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
            "lien_cv",
            "lien_linkedin",
            "consentement_publication",
        ]

        widgets = {
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

        for name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "toggle toggle-success"
                continue

            if isinstance(widget, forms.Select):
                widget.attrs["class"] = "select select-bordered w-full"
                continue

            if isinstance(widget, forms.ClearableFileInput):
                widget.attrs["class"] = "file-input file-input-bordered w-full"
                continue

            if isinstance(widget, forms.Textarea):
                widget.attrs["class"] = "textarea textarea-bordered w-full"
                continue

            widget.attrs["class"] = "input input-bordered w-full"

    # ==================================================
    # VALIDATION METIER
    # ==================================================
 

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