from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10  # Taille par défaut
    page_size_query_param = 'page_size'  # Le nom du paramètre dans l'URL
    max_page_size = 100  # Sécurité : on empêche de demander 10 000 items d'un coup
