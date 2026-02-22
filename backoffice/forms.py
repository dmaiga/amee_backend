from django import forms
from cms.models import Article,Resource,Opportunity
from organizations.models import Organization
from django.utils import timezone
from accounts.models import User
from quality_control.models import IncidentReview
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

from django import forms
from organizations.models import Organization


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
        ]  # ❌ est_actif retiré

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # DaisyUI inputs
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "input input-bordered w-full"
            })

        # placeholders UX
        self.fields["nom"].widget.attrs["placeholder"] = "Nom officiel du bureau"
        self.fields["sigle"].widget.attrs["placeholder"] = "Sigle (optionnel)"
        self.fields["email_contact"].widget.attrs["placeholder"] = "contact@organisation.org"

class AffecterIncidentForm(forms.ModelForm):

    class Meta:
        model = IncidentReview
        fields = ["enqueteur"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        enqueteurs = User.objects.filter(
            role__in=["BUREAU", "SUPERADMIN", "SECRETARIAT"],

        ).select_related("adhesion")

        self.fields["enqueteur"].queryset = enqueteurs

        # UX nom / fallback email
        self.fields["enqueteur"].label_from_instance = (
            lambda u: (
                f"{u.first_name} {u.last_name}".strip()
                if u.first_name or u.last_name
                else u.email
            )
        )

        self.fields["enqueteur"].empty_label = "— Sélectionner un enquêteur —"

class StatuerIncidentForm(forms.ModelForm):

    DECISIONS = [
        ("NON_LIEU", "Non lieu"),
        ("AVERTISSEMENT", "Avertissement"),
        ("SUSPENSION", "Suspension"),
    ]

    decision = forms.ChoiceField(choices=DECISIONS)
    niveau = forms.IntegerField(required=False, min_value=1, max_value=3)

    class Meta:
        model = IncidentReview
        fields = ["rapport_enquete", "decision"]
        widgets = {
            "rapport_enquete": forms.Textarea(
                attrs={"rows": 6, "class": "form-control"}
            )
        }

    # -----------------------------
    # VALIDATION MÉTIER
    # -----------------------------
    def clean(self):
        cleaned = super().clean()

        decision = cleaned.get("decision")
        niveau = cleaned.get("niveau")

        # si sanction → niveau obligatoire
        if decision != "NON_LIEU" and not niveau:
            raise forms.ValidationError(
                "Un niveau de sanction est requis."
            )

        return cleaned
    

class EnrolementPaiementForm(forms.Form):

    OPERATION_CHOICES = [
        ("FULL", "Adhésion + Cotisation"),
        ("ADHESION", "Adhésion seule"),
        ("COTISATION", "Cotisation seule"),
    ]

    # --- identité ---
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    phone = forms.CharField(required=False, label="Téléphone")

    # --- organisation ---
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.filter(est_actif=True),
        required=False,
        empty_label="Aucune organisation affiliée"
    )

    # --- paiement ---
    operation = forms.ChoiceField(choices=OPERATION_CHOICES)
    montant = forms.IntegerField(min_value=1000)
    description = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # inputs texte / email / number
        for name in ["email", "first_name", "last_name", "phone", "montant"]:
            self.fields[name].widget.attrs.update({
                "class": "input input-bordered w-full",
            })

        # textarea
        self.fields["description"].widget.attrs.update({
            "class": "textarea textarea-bordered w-full",
            "rows": 3
        })

        # selects
        self.fields["operation"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })

        self.fields["organization"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })