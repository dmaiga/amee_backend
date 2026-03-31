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
            "titre_fr", "titre_en",
            "type",
            "contenu_fr", "contenu_en",
            "image",
            "publie",
            "date_publication",
            "lien_externe",
            "publie_manuellement",
        ]

        widgets = {

            "titre_fr": forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "Titre en français"}),
            "titre_en": forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "Title in English"}),
            
            # Contenus
            "contenu_fr": forms.Textarea(attrs={"rows": 8, "class": "textarea textarea-bordered w-full"}),
            "contenu_en": forms.Textarea(attrs={"rows": 8, "class": "textarea textarea-bordered w-full"}),
           
            "type": forms.Select(attrs={
                "class": "select select-bordered w-full"
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "file-input file-input-bordered w-full"
            }),

            "date_publication": forms.DateTimeInput(attrs={
                "type": "datetime-local",
                "class": "input input-bordered w-full"
            }),

            "lien_externe": forms.Textarea(attrs={
                "class": "input input-bordered w-full"
            }),

            "publie": forms.CheckboxInput(attrs={
                "class": "toggle toggle-success"
            }),

            "publie_manuellement": forms.CheckboxInput(attrs={
                "class": "toggle toggle-warning"
            }),
        }

class ResourceForm(forms.ModelForm):

    class Meta:
        model = Resource
        fields = [
            "titre_fr", "titre_en",
            "description_fr", "description_en",
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
            "titre_fr": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "titre_en": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
           

            "description_fr": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 8
            }),
            "description_en": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 8
            }),
            "categorie": forms.Select(attrs={
                "class": "select select-bordered w-full"
            }),

            "fichier": forms.ClearableFileInput(attrs={
                "class": "file-input file-input-bordered w-full"
            }),
            "reserve_aux_membres": forms.CheckboxInput(attrs={
                "class": "toggle toggle-success",
                
            }),

 
        }

    # ✅ EN DEHORS DE META
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
            "titre_fr", "titre_en",
            "description_fr", "description_en",
            "type",
            "date_limite",
            "lien_externe",
            "reserve_aux_membres",
            "fichier_joint",
            "publie",
        ]

        widgets = {
            "titre_fr": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "titre_en": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
           

            "description_fr": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 8
            }),
            "description_en": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 8
            }),

            "type": forms.Select(attrs={
                "class": "select select-bordered w-full"
            }),

            "date_limite": forms.DateInput(attrs={
                "type": "date",
                "class": "input input-bordered w-full"
            }),

            "fichier_joint": forms.ClearableFileInput(attrs={
                "class": "file-input file-input-bordered w-full"
            }),

            "lien_externe": forms.Textarea(attrs={
                "class": "input input-bordered w-full"
            }),
            "reserve_aux_membres": forms.CheckboxInput(attrs={
                "class": "toggle toggle-success",
                
            }),

            "publie": forms.CheckboxInput(attrs={
                "class": "toggle toggle-success"
            }),
        }

class AffecterIncidentForm(forms.ModelForm):

    class Meta:
        model = IncidentReview
        fields = ["enqueteur"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        enqueteurs = User.objects.all()

        self.fields["enqueteur"].queryset = enqueteurs

        self.fields["enqueteur"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })

        # UX affichage humain
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
    niveau = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=3
    )

    class Meta:
        model = IncidentReview
        fields = ["rapport_enquete", "decision"]

        widgets = {
            "rapport_enquete": forms.Textarea(attrs={
                "rows": 6,
                "class": "textarea textarea-bordered w-full"
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["decision"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })

        self.fields["niveau"].widget.attrs.update({
            "class": "input input-bordered w-full",
            "placeholder": "Niveau de sanction (1 à 3)"
        })
        self.fields["niveau"].help_text = (
            "Obligatoire pour avertissement ou suspension."
        )

    # -----------------------------
    # VALIDATION MÉTIER
    # -----------------------------
    def clean(self):
        cleaned = super().clean()

        decision = cleaned.get("decision")
        niveau = cleaned.get("niveau")

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
    ELIGIBILITE = [
        ("OPTION1", "Env/Social + 2 ans"),
        ("OPTION2", "Autre domaine + 5 ans"),
    ]
    DIPLOME_NIVEAU = [
        ("LICENCE", "Licence"),
        ("MASTER", "Master"),
        ("DOCTORAT", "Doctorat"),
        ("AUTRE", "Autre"),
    ]
    

    eligibilite_option = forms.ChoiceField(choices=ELIGIBILITE)
    cv_document = forms.FileField(required=False)

    diplome_niveau = forms.ChoiceField(
        choices=DIPLOME_NIVEAU,
        label="Niveau du diplôme"
    )

    diplome_intitule = forms.CharField(
        label="Intitulé du diplôme"
    )
    annee_diplome = forms.CharField(
        label="Année d'obtention"
    )


    diplome_document = forms.FileField(
        required=False,
        label="Diplôme (scan ou PDF)"
    )

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
        self.fields["eligibilite_option"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })
        self.fields["cv_document"].widget.attrs.update({
            "class": "file-input file-input-bordered w-full"
        })
        self.fields["diplome_niveau"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })
        
        self.fields["diplome_intitule"].widget.attrs.update({
            "class": "input input-bordered w-full"
        })
        
        self.fields["annee_diplome"].widget.attrs.update({
            "class": "input input-bordered w-full"
        })
        
        self.fields["diplome_document"].widget.attrs.update({
            "class": "file-input file-input-bordered w-full"
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


from django import forms

INPUT = "input input-bordered w-full"
SELECT = "select select-bordered w-full"
TEXTAREA = "textarea textarea-bordered w-full"


class PaiementCreationOrganisationForm(forms.Form):

    OPERATION_CHOICES = [
        ("FULL", "Adhésion + Cotisation"),
        ("ADHESION", "Adhésion seule"),
    ]

    operation = forms.ChoiceField(
        choices=OPERATION_CHOICES,
        label="Type d’opération",
        widget=forms.Select(attrs={"class": SELECT})
    )

    montant_adhesion = forms.IntegerField(
        min_value=1000,
        label="Montant adhésion",
        widget=forms.NumberInput(attrs={"class": INPUT})
    )

    montant_cotisation = forms.IntegerField(
        required=False,
        min_value=1000,
        label="Montant cotisation (si FULL)",
        widget=forms.NumberInput(attrs={"class": INPUT})
    )

    description = forms.CharField(
        required=False,
        label="Description",
        widget=forms.Textarea(attrs={
            "class": TEXTAREA,
            "rows": 3
        })
    )

    def clean(self):
        cleaned = super().clean()

        operation = cleaned.get("operation")
        cotisation = cleaned.get("montant_cotisation")

        if operation == "FULL" and not cotisation:
            raise forms.ValidationError(
                "Montant cotisation requis pour une opération FULL."
            )

        return cleaned
    

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

            # 🔹 nouvelles infos bureau
            "representant_nom",
            "representant_fonction",
            "representant_email",
            "logo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Style DaisyUI uniforme
        for name, field in self.fields.items():

            # file input différent
            if name == "logo":
                field.widget.attrs.update({
                    "class": "file-input file-input-bordered w-full"
                })
            else:
                field.widget.attrs.update({
                    "class": "input input-bordered w-full"
                })

        # ✅ Placeholders UX
        self.fields["nom"].widget.attrs["placeholder"] = "Nom officiel du bureau"
        self.fields["sigle"].widget.attrs["placeholder"] = "Sigle (optionnel)"
        self.fields["email_contact"].widget.attrs["placeholder"] = "contact@organisation.org"
        self.fields["telephone"].widget.attrs["placeholder"] = "+223 XX XX XX XX"
        self.fields["siege"].widget.attrs["placeholder"] = "Ville / Adresse du siège"
        self.fields["site_web"].widget.attrs["placeholder"] = "https://..."

        # 🔹 Représentant
        self.fields["representant_nom"].widget.attrs["placeholder"] = "Nom du représentant"
        self.fields["representant_fonction"].widget.attrs["placeholder"] = "Président, Secrétaire général..."
        self.fields["representant_email"].widget.attrs["placeholder"] = "email du représentant"


# Deprecier a utilise now cotisationOrganisationForm
class EnrolementOrganisationForm(forms.Form):

    OPERATION_CHOICES = [
        ("FULL", "Adhésion + Cotisation"),
        ("ADHESION", "Adhésion seule"),
        ("COTISATION", "Cotisation seule"),
    ]

    organization = forms.ModelChoiceField(
        queryset=Organization.objects.filter(est_actif=True),
        label="Organisation",
        empty_label="Choisir une organisation"
    )

    operation = forms.ChoiceField(choices=OPERATION_CHOICES)

    montant_adhesion = forms.IntegerField(
        required=False,
        min_value=1000,
        label="Frais d’adhésion"
    )

    montant_cotisation = forms.IntegerField(
        required=False,
        min_value=1000,
        label="Cotisation annuelle"
    )

    description = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # inputs
        for name in [
            "montant_adhesion",
            "montant_cotisation",
        ]:
            self.fields[name].widget.attrs.update({
                "class": "input input-bordered w-full"
            })

        self.fields["description"].widget.attrs.update({
            "class": "textarea textarea-bordered w-full",
            "rows": 3,
        })

        self.fields["operation"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })

        self.fields["organization"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })

    # ✅ validation intelligente
    def clean(self):
        cleaned = super().clean()

        op = cleaned.get("operation")
        adh = cleaned.get("montant_adhesion")
        cot = cleaned.get("montant_cotisation")

        if op == "ADHESION" and not adh:
            raise forms.ValidationError(
                "Montant adhésion requis."
            )

        if op == "COTISATION" and not cot:
            raise forms.ValidationError(
                "Montant cotisation requis."
            )

        if op == "FULL" and (not adh or not cot):
            raise forms.ValidationError(
                "Adhésion et cotisation requises."
            )

        return cleaned


class CotisationOrganisationForm(forms.Form):

    organization = forms.ModelChoiceField(
        queryset=Organization.objects.filter(est_affilie=True),
        empty_label="Organisation affiliée",
        label="Organisation"
    )

    montant = forms.IntegerField(
        min_value=1000,
        label="Montant cotisation"
    )

    description = forms.CharField(
        required=False,
        label="Description"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["organization"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })

        self.fields["montant"].widget.attrs.update({
            "class": "input input-bordered w-full"
        })

        self.fields["description"].widget.attrs.update({
            "class": "textarea textarea-bordered w-full",
            "rows": 3
        })

    def clean(self):
        cleaned = super().clean()
        org = cleaned.get("organization")

        if org and not org.est_affilie:
            raise forms.ValidationError(
                "Cette organisation n'est pas encore affiliée."
            )

        return cleaned


