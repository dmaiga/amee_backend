from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone

def portal_access_required(level):

    def decorator(view_func):

        def wrapper(request, *args, **kwargs):

            user = request.user

            # NON CONNECTÉ
            if not user.is_authenticated:
                return redirect("login")

            # COMPTE BLOQUÉ
            if not user.is_active_account:
                logout(request)
                return redirect("login")

            # MEMBER / CONSULTANT CHECK
            if level in ["member", "consultant"]:

                membership = getattr(user, "membership", None)

                if not membership:
                    messages.error(
                        request,
                        "Aucune adhésion trouvée."
                    )
                    return redirect("login")

                if not membership.est_actif:
                    messages.error(
                        request,
                        "Votre adhésion est expirée."
                    )
                    return redirect("login")



            # CLIENT CHECK
            if level == "client":
                if user.role != "CLIENT":
                    logout(request)
                    return redirect("login")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def bureau_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        user = request.user
        

        # Non connecté
        if not user.is_authenticated:
            return redirect("login")

        if user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Compte bloqué
        if not user.is_active_account:
            return redirect("login")

        # Vérification bureau actif
        if not user.est_membre_bureau_actif:
            messages.error(
                request,
                "Accès réservé au bureau exécutif."
            )
            return redirect("portal_dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper