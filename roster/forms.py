# roste/froms.py
from django import forms
from roster.models import ConsultantProfile
from roster.models import ConsultantPublicProfile
from django import forms
from roster.models import ConsultantProfile, ConsultantPublicProfile


class ConsultantApplicationForm(forms.Form):

    # =====================
    # DOSSIER AMEE
    # =====================

    domaine_expertise = forms.CharField(
        label="Domaine principal d’expertise",
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full"
        })
    )

    annees_experience = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "input input-bordered w-full"
        })
    )

    eligibilite_option = forms.ChoiceField(
        choices=ConsultantProfile._meta.get_field(
            "eligibilite_option"
        ).choices,
        widget=forms.Select(attrs={
            "class": "select select-bordered w-full"
        })
    )

    cv_document = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": "file-input file-input-bordered w-full"
        })
    )

    # =====================
    # INFOS EXPERT (pré-remplissage profil public)
    # =====================

    titre_professionnel = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full"
        })
    )

    resume_public = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "textarea textarea-bordered w-full",
            "rows": 4
        })
    )

    domaines_expertise = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full"
        })
    )

    langues = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full"
        })
    )
    def save(self, user):

        profil, _ = ConsultantProfile.objects.get_or_create(user=user)

        profil.domaine_expertise = self.cleaned_data["domaine_expertise"]
        profil.annees_experience = self.cleaned_data["annees_experience"]
        profil.eligibilite_option = self.cleaned_data["eligibilite_option"]
        profil.cv_document = self.cleaned_data.get("cv_document")
        profil.statut = "SOUMIS"
        profil.save()

        public, _ = ConsultantPublicProfile.objects.get_or_create(
            consultant=profil
        )

        public.titre_professionnel = self.cleaned_data["titre_professionnel"]
        public.resume_public = self.cleaned_data["resume_public"]
        public.domaines_expertise = self.cleaned_data["domaines_expertise"]
        public.langues = self.cleaned_data["langues"]
        public.save()

        return profil


from django.forms import ModelForm
from roster.models import ConsultantPublicProfile

from django import forms
from django.forms import ModelForm
from roster.models import ConsultantPublicProfile


class ConsultantPublicProfileForm(ModelForm):

    class Meta:
        model = ConsultantPublicProfile

        fields = [
            "titre_professionnel",
            "resume_public",
            "niveau_seniorite",
            "statut_professionnel",
            "domaines_expertise",
            "secteurs_experience",
            "experience_geographique",
            "langues",
            "nationalite",
            "pays_residence",
            "certifications",
            "cv_public",
            "lien_cv",
            "lien_linkedin",
            "statut_disponibilite",
            "consentement_publication",
        ]

        widgets = {

            "titre_professionnel":
                forms.TextInput(attrs={"class": "input input-bordered w-full"}),

            "resume_public":
                forms.Textarea(attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 4
                }),

            "niveau_seniorite":
                forms.Select(attrs={"class": "select select-bordered w-full"}),

            "statut_professionnel":
                forms.Select(attrs={"class": "select select-bordered w-full"}),

            "domaines_expertise":
                forms.TextInput(attrs={"class": "input input-bordered w-full"}),

            "secteurs_experience":
                forms.Textarea(attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 2
                }),

            "experience_geographique":
                forms.Textarea(attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 2
                }),

            "langues":
                forms.TextInput(attrs={"class": "input input-bordered w-full"}),

            "nationalite":
                forms.TextInput(attrs={"class": "input input-bordered w-full"}),

            "pays_residence":
                forms.TextInput(attrs={"class": "input input-bordered w-full"}),

            "certifications":
                forms.Textarea(attrs={
                    "class": "textarea textarea-bordered w-full"
                }),

            "cv_public":
                forms.ClearableFileInput(attrs={
                    "class": "file-input file-input-bordered w-full"
                }),

            "lien_cv":
                forms.URLInput(attrs={"class": "input input-bordered w-full"}),

            "lien_linkedin":
                forms.URLInput(attrs={"class": "input input-bordered w-full"}),

            "statut_disponibilite":
                forms.Select(attrs={"class": "select select-bordered w-full"}),

            "consentement_publication":
                forms.CheckboxInput(attrs={
                    "class": "toggle toggle-success"
                }),
        }