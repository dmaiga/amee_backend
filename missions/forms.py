
from django import forms
from missions.models import Mission,MissionApplication


class MissionCreateForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = [
            "titre",
            "description",
            "objectifs",
            "domaine",
            "livrables_attendus",
            "localisation",
            "duree_estimee_jours",
            "budget_estime",
            "type_publication",
            "date_fin",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "objectifs": forms.Textarea(attrs={"rows": 4}),
            "livrables_attendus": forms.Textarea(attrs={"rows": 4}),            
            "date_fin": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Appliquer classes DaisyUI
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    "class": "textarea textarea-bordered w-full bg-base-100"
                })
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({
                    "class": "input input-bordered w-full bg-base-100"
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    "class": "select select-bordered w-full bg-base-100"
                })
            else:
                field.widget.attrs.update({
                    "class": "input input-bordered w-full bg-base-100"
                })

    def clean(self):
        cleaned_data = super().clean()
        type_publication = cleaned_data.get("type_publication")
        date_fin = cleaned_data.get("date_fin")

        # Si mission publique → date_fin obligatoire
        if type_publication == "PUBLIQUE" and not date_fin:
            self.add_error(
                "date_fin",
                "Une mission publique doit avoir une date de fin."
            )

        return cleaned_data
    

class MissionApplicationForm(forms.ModelForm):

    class Meta:
        model = MissionApplication
        fields = [
            "message",
            "proposition_technique",
            "proposition_financiere",
        ]

        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": (
                        "Expliquez brièvement pourquoi votre profil "
                        "correspond à cette mission (expérience, "
                        "approche méthodologique, disponibilité)."
                    ),
                    "class": "textarea textarea-bordered w-full"
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["message"].help_text = (
            "Note de motivation (30 à 500 mots)."
        )

        for name, field in self.fields.items():

            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({
                    "class": "file-input file-input-bordered w-full"
                })

    # ----------------------------
    # VALIDATION MESSAGE
    # ----------------------------

    def clean_message(self):

        message = self.cleaned_data.get("message", "").strip()

        if message:

            words = message.split()

            if len(words) < 50:
                raise forms.ValidationError(
                    "Votre note de motivation doit contenir "
                    "au moins 50 mots."
                )

            if len(words) > 500:
                raise forms.ValidationError(
                    "Votre message ne doit pas dépasser 500 mots."
                )

        return message

    # ----------------------------
    # VALIDATION FICHIERS
    # ----------------------------

    def validate_file(self, file):

        allowed = ["pdf", "doc", "docx"]

        ext = file.name.split(".")[-1].lower()

        if ext not in allowed:
            raise forms.ValidationError(
                "Format non supporté. Utilisez PDF, DOC ou DOCX."
            )

        if file.size > 10 * 1024 * 1024:
            raise forms.ValidationError(
                "Le fichier ne doit pas dépasser 10MB."
            )

    def clean_proposition_technique(self):

        file = self.cleaned_data.get("proposition_technique")

        if file:
            self.validate_file(file)

        return file

    def clean_proposition_financiere(self):

        file = self.cleaned_data.get("proposition_financiere")

        if file:
            self.validate_file(file)

        return file

    # ----------------------------
    # VALIDATION GLOBALE
    # ----------------------------

    def clean(self):

        cleaned = super().clean()

        technique = cleaned.get("proposition_technique")
        financiere = cleaned.get("proposition_financiere")

        if not technique and not financiere:
            raise forms.ValidationError(
                "Veuillez joindre au moins un document "
                "(proposition technique ou financière)."
            )

        return cleaned