from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages


class PortalAccessMixin:

    access_level = None  # "client" | "member" | "consultant"

    def dispatch(self, request, *args, **kwargs):

        user = request.user

        # -------------------
        # NON CONNECTÉ
        # -------------------
        if not user.is_authenticated:
            return redirect("login")

        # -------------------
        # COMPTE BLOQUÉ
        # -------------------
        if not user.is_active_account:
            logout(request)
            return redirect("login")

        # -------------------
        # CLIENT
        # -------------------
        if self.access_level == "client":
            if user.role != "CLIENT":
                logout(request)
                return redirect("login")

        # -------------------
        # MEMBER
        # -------------------
        if self.access_level in ["member", "consultant"]:

            adhesion = getattr(user, "adhesion", None)

            if not adhesion or not adhesion.est_actif:
                messages.error(
                    request,
                    "Votre adhésion n'est pas active."
                )
                return redirect("portal-dashboard")

        # -------------------
        # CONSULTANT
        # -------------------
        if self.access_level == "consultant":

            profil = getattr(user, "profil_roster", None)

            if not profil or not profil.est_actif_roster:
                messages.error(
                    request,
                    "Accès réservé aux consultants validés."
                )
                return redirect("portal-dashboard")

        return super().dispatch(request, *args, **kwargs)