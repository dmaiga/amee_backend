from django import forms
from memberships.models import MemberProfile


class MemberProfileForm(forms.ModelForm):

    class Meta:
        model = MemberProfile
        fields = [
            "photo",
            "telephone",
            "organisation",
            "fonction",
            "secteur",
            "bio",
        ]

        widgets = {
            "telephone": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "organisation": forms.TextInput(attrs={
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