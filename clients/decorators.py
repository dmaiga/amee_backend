from django.shortcuts import redirect


def client_required(view_func):
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("bo_login")

        if request.user.role != "CLIENT":
            return redirect("bo_login")  # backoffice

        return view_func(request, *args, **kwargs)

    return wrapper