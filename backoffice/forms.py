from django import forms
from cms.models import Article,Resource,Opportunity
from organizations.models import Organization


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = [
            "titre",
            "type",
            "contenu",
            "image",
            "publie",
            "date_publication",
            "lien_externe",
            "publie_manuellement",
        ]

        widgets = {
            "contenu": forms.Textarea(attrs={
                "rows": 8,
                "class": "form-control"
            }),
            "date_publication": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
        }

class ResourceForm(forms.ModelForm):

    class Meta:
        model = Resource
        fields = [
            "titre",
            "description",
            "fichier",
            "categorie",
            "reserve_aux_membres",
        ]

        labels = {
            "titre": "Titre",
            "description": "Description",
            "fichier": "Fichier à télécharger",
            "categorie": "Catégorie",
            "reserve_aux_membres": "Réservé aux membres",
        }

        widgets = {
            "titre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Titre de la ressource"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Description courte..."
            }),

            "categorie": forms.Select(attrs={
                "class": "form-select"
            }),

            "reserve_aux_membres": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }
        def clean_fichier(self):
            fichier = self.cleaned_data.get("fichier")

            if fichier and fichier.size > 10 * 1024 * 1024:
                raise forms.ValidationError(
                    "Le fichier ne doit pas dépasser 10MB."
                )

            return fichier

class OpportunityForm(forms.ModelForm):

    class Meta:
        model = Opportunity
        fields = [
            "titre",
            "description",
            "type",
            "date_limite",
            "reserve_aux_membres",
            "fichier_joint",
            "publie",
        ]

        widgets = {
            "titre": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6
            }),

            "type": forms.Select(attrs={
                "class": "form-select"
            }),

            "date_limite": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),

            "reserve_aux_membres": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }


class OrganizationForm(forms.ModelForm):

    class Meta:
        model = Organization
        fields = [
            "nom",
            "sigle",
            "email_contact",
            "telephone",
            "siege",
            "site_web",
            "est_actif",
        ]

        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "sigle": forms.TextInput(attrs={"class": "form-control"}),
            "email_contact": forms.EmailInput(attrs={"class": "form-control"}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
            "siege": forms.TextInput(attrs={"class": "form-control"}),
            "site_web": forms.URLInput(attrs={"class": "form-control"}),
        }