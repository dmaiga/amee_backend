from django import forms
from memberships.models import MemberProfile


class MemberProfileForm(forms.ModelForm):

    class Meta:
        model = MemberProfile
        fields = [
            "photo",
            "telephone",
          
            "fonction",
            "secteur",
            "bio",
        ]

        widgets = {
            "telephone": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),

            "fonction": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "secteur": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "bio": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 4
            }),
            "photo": forms.ClearableFileInput(attrs={
                "class": "file-input file-input-bordered w-full"
            }),
        }

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
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "phone": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "secondary_phone": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
        }