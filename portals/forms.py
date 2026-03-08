from django import forms
from missions.models import Mission
from portals.models import ClientProfile


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


from django import forms
from portals.models import ClientProfile

from django import forms
from portals.models import ClientProfile


class ClientRegistrationForm(forms.ModelForm):

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
            "nom_entreprise": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Nom officiel de l’entreprise"
            }),
            "secteur_activite": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Ex: Environnement, Audit, BTP..."
            }),
            "email_pro": forms.EmailInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "contact@entreprise.com"
            }),
            "telephone_pro": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "+223..."
            }),
            "nom_contact": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Nom du responsable"
            }),
            "fonction_contact": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Directeur, RH..."
            }),
        }

from django import forms
from memberships.models import Membership
from django import forms
from memberships.models import Membership


class MembershipRegistrationForm(forms.ModelForm):

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Votre email"
        })
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Prénom"
        })
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Nom"
        })
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "+223..."
        })
    )

    class Meta:
        model = Membership
        fields = [
            "eligibilite_option",
            "diplome_niveau",
            "diplome_intitule",
            "annee_diplome",
            "cv_document",
            "diplome_document",
        ]

        widgets = {
            "eligibilite_option": forms.Select(attrs={
                "class": "select select-bordered w-full"
            }),
            "diplome_niveau": forms.Select(attrs={
                "class": "select select-bordered w-full"
            }),
            "diplome_intitule": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Intitulé du diplôme"
            }),
            "annee_diplome": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Année d’obtention"
            }),
            "cv_document": forms.FileInput(attrs={
                "class": "file-input file-input-bordered w-full",
                
            }),
            "diplome_document": forms.FileInput(attrs={
                "class": "file-input file-input-bordered w-full"
            }),
        }