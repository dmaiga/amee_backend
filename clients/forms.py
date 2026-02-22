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