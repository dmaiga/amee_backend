# roste/froms.py
from django import forms
from roster.models import ConsultantProfile


class ConsultantProfileForm(forms.ModelForm):

    class Meta:
        model = ConsultantProfile
        fields = [
            "domaine_expertise",
            "annees_experience",
            "eligibilite_option",
            "cv_document",
            "est_disponible",
        ]

        widgets = {

            "domaine_expertise": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Ex: Data Engineering, Audit IT, Finance..."
                }
            ),

            "annees_experience": forms.NumberInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "min": 0
                }
            ),

            "eligibilite_option": forms.Select(
                attrs={
                    "class": "select select-bordered w-full"
                }
            ),

            "cv_document": forms.ClearableFileInput(
                attrs={
                    "class": "file-input file-input-bordered w-full"
                }
            ),

            "est_disponible": forms.CheckboxInput(
                attrs={
                    "class": "toggle toggle-success"
                }
            ),
        }

    # ✅ labels propres pour DaisyUI
    labels = {
        "domaine_expertise": "Domaine d’expertise",
        "annees_experience": "Années d'expérience",
        "eligibilite_option": "Type d’intervention",
        "cv_document": "CV (PDF recommandé)",
        "est_disponible": "Disponible pour missions",
    }