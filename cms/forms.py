from django import forms
from cms.models import Mandat, BoardRole, BoardMembership
from memberships.models import Membership
from django.core.exceptions import ValidationError

# ===============================
# Mandat Form
# ===============================
class MandatForm(forms.ModelForm):
    class Meta:
        model = Mandat
        fields = ["nom_fr","nom_en", "date_debut", "date_fin", "actif", "mot_president_fr", "mot_president_en"]
        widgets = {
            "nom_fr": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "nom_en": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "date_debut": forms.DateInput(attrs={
                "type": "date",
                "class": "input input-bordered w-full"
            }),
            "date_fin": forms.DateInput(attrs={
                "type": "date",
                "class": "input input-bordered w-full"
            }),
            "mot_president_fr": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 5
            }),
            "mot_president_en": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 5
            }),
            "actif": forms.CheckboxInput(attrs={
                "class": "checkbox checkbox-primary"
            }),
        }

# ===============================
# BoardRole Form
# ===============================
class BoardRoleForm(forms.ModelForm):
    class Meta:
        model = BoardRole
        fields = ["titre", "ordre", "actif"]
        widgets = {
            "titre": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "ordre": forms.NumberInput(attrs={
                "class": "input input-bordered w-full",
                "min": "0"
            }),
            "actif": forms.CheckboxInput(attrs={
                "class": "checkbox checkbox-primary"
            }),
        }


# ===============================
# BoardMembership Form
# ===============================
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils import timezone

from django.utils import timezone

class BoardMembershipForm(forms.ModelForm):

    class Meta:
        model = BoardMembership
        fields = ["membership", "role"]
        widgets = {
            "membership": forms.Select(attrs={
                "class": "select select-bordered w-full"
            }),
            "role": forms.Select(attrs={
                "class": "select select-bordered w-full"
            }),
        }

    def __init__(self, *args, **kwargs):
        self.mandat = kwargs.pop("mandat", None)
        super().__init__(*args, **kwargs)

        if not self.mandat and self.instance.pk:
            self.mandat = self.instance.mandat

        today = timezone.now().date()

        queryset = Membership.objects.select_related("user").filter(
            statut="VALIDE",
            date_expiration__gte=today
        )

        self.fields["membership"].queryset = queryset

        # 🔥 Personnalisation affichage
        self.fields["membership"].label_from_instance = self.membership_label


    def membership_label(self, obj):
        user = obj.user
        full_name = f"{user.last_name.upper()} {user.first_name}"
        phone = user.phone or ""
        return f"{full_name} — {phone}"


    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")

        if not self.mandat:
            return cleaned_data

        if role:
            exists = BoardMembership.objects.filter(
                mandat=self.mandat,
                role=role
            ).exclude(pk=self.instance.pk).exists()

            if exists:
                raise ValidationError(
                    "Ce poste est déjà occupé pour ce mandat."
                )

        return cleaned_data
    


from django import forms
from .models import Gallery, Photo

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = [
                    'title_fr', 'title_en', 
                    'description_fr', 'description_en', 
                    'cover_image', 'is_featured'
                ]
        
        widgets = {
            "title_fr": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
            "title_en": forms.TextInput(attrs={
                "class": "input input-bordered w-full"
            }),
           

            "description_fr": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 3
            }),
            "description_en": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 3
            }),
            "cover_image": forms.ClearableFileInput(attrs={
                "class": "file-input file-input-bordered w-full"
            }),
            "is_featured": forms.CheckboxInput(attrs={
                "class": "toggle toggle-success",
                
            }),

        }

  

import os

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PhotoForm(forms.ModelForm):
    images = MultipleFileField(
        required=True,
        label="Images",
        help_text="Sélectionnez une ou plusieurs images. Maintenez Ctrl/Cmd pour en sélectionner plusieurs."
    )

    class Meta:
        model = Photo
        fields = [ 'gallery', 'is_standalone']
        widgets = {
          
            'gallery': forms.Select(attrs={'class': 'form-control'}),
            'is_standalone': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        help_texts = {
            'title': 'Si vide, le nom du fichier sera utilisé comme titre',
            'is_standalone': 'Cocher si ces photos ne doivent pas être associées à une galerie'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les galeries disponibles
        self.fields['gallery'].queryset = Gallery.objects.all()
        self.fields['gallery'].required = False
        
        # Réorganiser l'ordre des champs
        self.order_fields(['images', 'gallery', 'is_standalone'])

    def clean(self):
        cleaned_data = super().clean()
        gallery = cleaned_data.get('gallery')
        is_standalone = cleaned_data.get('is_standalone')
        
        # Validation: une photo ne peut pas être à la fois dans une galerie et standalone
        if gallery and is_standalone:
            raise forms.ValidationError(
                "Une photo ne peut pas être à la fois dans une galerie et indépendante."
            )
        
        return cleaned_data