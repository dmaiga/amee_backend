from django import forms
from django.forms import ModelForm
from roster.models import ConsultantProfile


class ConsultantApplicationForm(ModelForm):

    class Meta:
        model = ConsultantProfile

        fields = [
            # ===== ELIGIBILITE =====
            "eligibilite_option",
            "diplome_principal_domaine",
            "annee_diplome_principal",
            "autre_diplome_pertinent",
            "annee_autre_diplome",
            "annees_experience_ees",
            "attestations",
            "cv_document",

            # ===== PROFIL CONSULTANT =====
            "titre_professionnel",
            "resume_public",
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
    def clean(self):
        cleaned = super().clean()

        option = cleaned.get("eligibilite_option")

        if option == "OPTION1" and not cleaned.get("diplome_principal_domaine"):
            self.add_error(
                "diplome_principal_domaine",
                "Diplôme requis pour l’option 1."
            )

        if option == "OPTION2" and not cleaned.get("autre_diplome_pertinent"):
            self.add_error(
                "autre_diplome_pertinent",
                "Diplôme requis pour l’option 2."
            )

        return cleaned

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