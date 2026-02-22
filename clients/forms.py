from django import forms
from missions.models import Mission

from django import forms
from missions.models import Mission

class MissionCreateForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = [
            "titre", "description", "domaine", 
            "localisation", "duree_estimee_jours", "budget_estime",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On applique dynamiquement les classes DaisyUI à tous les champs
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"class": "textarea textarea-bordered w-full bg-base-100"})
            else:
                field.widget.attrs.update({"class": "input input-bordered w-full bg-base-100"})


from django import forms
from clients.models import ClientProfile


class ClientProfileForm(forms.ModelForm):

    class Meta:
        model = ClientProfile
        fields = [
            "nom_entreprise",
            "secteur_activite",
            "email_pro",
            "telephone_pro",
            "nom_contact",
            "fonction_contact",
        ]

        widgets = {
            "nom_entreprise": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
            "secteur_activite": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
            "email_pro": forms.EmailInput(
                attrs={"class": "input input-bordered w-full"}
            ),
            "telephone_pro": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
            "nom_contact": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
            "fonction_contact": forms.TextInput(
                attrs={"class": "input input-bordered w-full"}
            ),
        }             