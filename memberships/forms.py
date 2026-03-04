from django import forms

from django import forms
from accounts.models import User


class MemberEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "secondary_phone",
            "photo",
            "nationalite",
            "pays_residence"
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "nationalite": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "pays_residence": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "phone": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "secondary_phone": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
        }