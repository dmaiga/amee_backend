from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages


def portal_access_required(level):

    def decorator(view_func):

        def wrapper(request, *args, **kwargs):

            user = request.user

            # -----------------------
            # NON CONNECTÉ
            # -----------------------
            if not user.is_authenticated:
                return redirect("login")

            # -----------------------
            # COMPTE BLOQUÉ
            # -----------------------
            if not user.is_active_account:
                logout(request)
                return redirect("login")

            # -----------------------
            # MEMBER CHECK
            # -----------------------
            if level in ["member", "consultant"]:

                adhesion = getattr(user, "membership", None)

                if not adhesion or not adhesion.est_actif:
                    messages.error(
                        request,
                        "Votre adhésion n'est pas active."
                    )
                    return redirect("login")


            # -----------------------
            # CLIENT CHECK
            # -----------------------
            if level == "client":
                if user.role != "CLIENT":
                    logout(request)
                    return redirect("login")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator