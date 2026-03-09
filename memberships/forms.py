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
                "class": "input input-bordered w-full",
                "placeholder": "+223 XX XX XX XX"
            }),
            "secondary_phone": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "+223 XX XX XX XX"
            }),
            "photo": forms.FileInput(attrs={
                "class": "file-input file-input-bordered w-full",
                "accept": "image/*",
                "id": "photoInput"
            }),
        }

        help_texts = {
            "photo": "Image carrée recommandée (JPG ou PNG). Max 5MB."
        }

    def clean_phone(self):

        phone = self.cleaned_data.get("phone")
        secondary_phone = self.cleaned_data.get("secondary_phone")

        if phone and len(phone) < 7:
            raise forms.ValidationError("Numéro invalide")

        if secondary_phone and len(secondary_phone) < 7:
            raise forms.ValidationError("Numéro invalide")

        return phone