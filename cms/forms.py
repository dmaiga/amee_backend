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
        fields = ["nom", "date_debut", "date_fin", "actif", "mot_president"]
        widgets = {
            "nom": forms.TextInput(attrs={
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
            "mot_president": forms.Textarea(attrs={
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