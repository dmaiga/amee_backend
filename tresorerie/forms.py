from django import forms
from django.contrib.auth import get_user_model
from organizations.models import Organization
User = get_user_model()
from django import forms

INPUT = "input input-bordered w-full"
SELECT = "select select-bordered w-full"
TEXTAREA = "textarea textarea-bordered w-full"


class EnrolementPaiementForm(forms.Form):

    OPERATION_CHOICES = (
        ("FULL", "Adhésion + Cotisation"),
        ("ADHESION", "Adhésion seule"),
        ("COTISATION", "Cotisation seule"),
    )
    ELIGIBILITE = [
        ("OPTION1", "Env/Social + 2 ans"),
        ("OPTION2", "Autre domaine + 5 ans"),
    ]
    DIPLOME_NIVEAU = [
        ("LICENCE", "Licence"),
        ("MASTER", "Master"),
        ("DOCTORAT", "Doctorat"),
        ("AUTRE", "Autre"),
    ]
    

    eligibilite_option = forms.ChoiceField(choices=ELIGIBILITE)
    cv_document = forms.FileField(required=False)

    diplome_niveau = forms.ChoiceField(
        choices=DIPLOME_NIVEAU,
        label="Niveau du diplôme"
    )

    diplome_intitule = forms.CharField(
        label="Intitulé du diplôme"
    )

    diplome_document = forms.FileField(
        required=False,
        label="Diplôme (scan ou PDF)"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": INPUT})
    )

    first_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"class": INPUT})
    )

    last_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"class": INPUT})
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": INPUT})
    )

    organization = forms.ModelChoiceField(
        queryset=Organization.objects.filter(est_actif=True),
        required=False,
        empty_label="--- Membre individuel ---",
        widget=forms.Select(attrs={
            "class": "select select-bordered w-full"
        })
    )

    operation = forms.ChoiceField(
        choices=OPERATION_CHOICES,
        widget=forms.Select(attrs={"class": SELECT})
    )

    montant_adhesion = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": INPUT})
    )

    montant_cotisation = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": INPUT})
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": TEXTAREA, "rows": 3})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["eligibilite_option"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })
        self.fields["cv_document"].widget.attrs.update({
            "class": "file-input file-input-bordered w-full"
        })
        self.fields["diplome_niveau"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })
        
        self.fields["diplome_intitule"].widget.attrs.update({
            "class": "input input-bordered w-full"
        })
        
        self.fields["diplome_document"].widget.attrs.update({
            "class": "file-input file-input-bordered w-full"
        })



class PaiementSimpleForm(forms.Form):

    email = forms.EmailField(label="Email du membre")

    montant = forms.IntegerField(min_value=1000)

    description = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update({
            "class": "input input-bordered w-full"
        })

        self.fields["montant"].widget.attrs.update({
            "class": "input input-bordered w-full"
        })

        self.fields["description"].widget.attrs.update({
            "class": "textarea textarea-bordered w-full",
            "rows": 3
        })

class ActivationDigitaleForm(forms.Form):

    montant_adhesion = forms.DecimalField(
        min_value=0,
        label="Montant adhésion",
        widget=forms.NumberInput(attrs={
            "class": "input input-bordered w-full"
        })
    )

    montant_cotisation = forms.DecimalField(
        min_value=0,
        label="Montant cotisation",
        widget=forms.NumberInput(attrs={
            "class": "input input-bordered w-full"
        })
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "textarea textarea-bordered w-full",
            "rows": 3
        })
    )