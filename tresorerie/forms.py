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
