def can_manage_roster(user):
    """
    Admission consultant autorisée
    pour SECRETARIAT et BUREAU uniquement.
    """

    if not user.is_authenticated:
        return False

    return user.role in ["SECRETARIAT", "BUREAU", "SUPERADMIN"]
