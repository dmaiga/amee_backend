from django import forms
from missions.models import Mission


class MissionCreateForm(forms.ModelForm):

    class Meta:
        model = Mission
        fields = [
            "titre",
            "description",
            "objectifs",
            "livrables_attendus",
            "domaine",
            "localisation",
            "duree_estimee_jours",
            "budget_estime",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows":4}),
            "objectifs": forms.Textarea(attrs={"rows":3}),
            "livrables_attendus": forms.Textarea(attrs={"rows":3}),
        }