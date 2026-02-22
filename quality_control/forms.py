from django import forms
from quality_control.models import Feedback


class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = [
            "note",
            "commentaire",
            "incident_signale",
            "description_incident",
        ]

        widgets = {
            "note": forms.Select(
                choices=[(i, f"{i}/5") for i in range(1, 6)],
                attrs={"class": "select select-bordered w-full"},
            ),
            "commentaire": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 4,
                }
            ),
            "description_incident": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 3,
                }
            ),
        }