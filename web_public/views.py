from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
import random


from cms.models import Gallery, Article, Opportunity, Mandat, BoardMembership
from memberships.models import Membership
from organizations.models import Organization
from portals.models import ClientProfile
from roster.models import ConsultantProfile
from accounts.models import User

def acceuil(request):
    # Stats pour le dashboard
    stats = {
            "membres_actifs": Membership.objects.filter(
                statut="VALIDE"
            ).count(),
            "consultants_actifs": ConsultantProfile.objects.filter(
                statut="VALIDE",
            ).count(),
            "organisations_actifs": Organization.objects.filter(
                est_actif=True,
            ).count(),
    }

    featured_galleries = Gallery.objects.filter(is_featured=True)[:3]
    latest_articles = Article.objects.filter(publie=True).order_by('-date_publication')[:3]
    active_opps = Opportunity.objects.filter(
        publie=True, 
        reserve_aux_membres=False, 
        date_limite__gte=timezone.now().date()
    ).order_by('date_limite')[:3]

    return render(request, 'web_public/home.html', {
        'stats': stats,
        'featured_galleries': featured_galleries,
        'latest_articles': latest_articles,
        'active_opps': active_opps,
    })


def gallery_list(request):
    galleries = Gallery.objects.all().order_by('-created_at')
    return render(request, 'web_public/gallery/list.html', {'galleries': galleries})

def gallery_detail(request, slug):
    gallery = get_object_or_404(Gallery, slug=slug)
    # On utilise le related_name 'photos' défini dans ton modèle
    photos = gallery.photos.all() 
    return render(request, 'web_public/gallery/detail.html', {
        'gallery': gallery,
        'photos': photos
    })





def about_association(request):

    mandat_actif = Mandat.objects.filter(actif=True).first()
    
    president = None
    membres_bureau = []

    if mandat_actif:
        # 1. queryset complet
        membres_qs = BoardMembership.objects.filter(
            mandat=mandat_actif
        ).select_related('membership__user', 'role')

        # 2. président AVANT slice
        president = membres_qs.filter(
            role__titre__icontains="Président"
        ).first()

        # 3. ensuite seulement slice
        membres_bureau = membres_qs.order_by('?')[:8]
        total_bureau = membres_qs.count()

    stats = {
        "membres_actifs": Membership.objects.filter(statut="VALIDE").count(),
        "consultants_actifs": ConsultantProfile.objects.filter(statut="VALIDE").count(),
        "organisations_actifs": Organization.objects.filter(est_actif=True).count(),
    }

    context = {
        'stats': stats,
        'total_bureau': total_bureau,
        'mandat': mandat_actif,
        'president': president,
        'membres_bureau': membres_bureau,
        'partenaires': Organization.objects.filter(est_affilie=True, est_actif=True),
        'clients': ClientProfile.objects.filter(statut_onboarding="VALIDE"),
        'date_creation': "12 Octobre 2016",
        'siege': "Hamdallaye ACI, Rue 390, Porte 388",
    }

    return render(request, 'web_public/about_association.html', context)



def organization_detail(request, pk):
    organization = get_object_or_404(Organization, pk=pk, est_affilie=True)
    return render(request, 'web_public/organization_detail.html', {'organization': organization})


def board_list(request):
    """Affiche le bureau exécutif en isolant le président."""
    mandat_actif = Mandat.objects.filter(actif=True).first()
    president = None
    autres_membres = []
    
    if mandat_actif:
        # Récupération de tous les membres ordonnés
        membres_qs = BoardMembership.objects.filter(
            mandat=mandat_actif
        ).select_related('membership__user', 'role').order_by('role__ordre')
        
        # Isolation du président (premier rôle contenant "Président")
        president = membres_qs.filter(role__titre__icontains="Président").first()
        
        # Liste des autres membres (exclure le président s'il existe)
        if president:
            autres_membres = membres_qs.exclude(pk=president.pk)
        else:
            autres_membres = membres_qs
    
    return render(request, 'web_public/bureau/board_list.html', {
        'mandat': mandat_actif,
        'president': president,
        'autres_membres': autres_membres
    })

def board_member_detail(request, pk):
    """Détail d'un membre du bureau avec son mot s'il est président."""
    member_link = get_object_or_404(
        BoardMembership.objects.select_related(
            'membership__user', 
            'membership__user__profil_roster',
            'role', 
            'mandat'
        ), 
        pk=pk
    )
    
    consultant_profile = getattr(member_link.membership.user, 'profil_roster', None)
    
    # Vérification si c'est le président pour afficher le mot du mandat
    is_president = "Président" in member_link.role.titre

    return render(request, 'web_public/bureau/board_member_detail.html', {
        'member': member_link,
        'profile': consultant_profile,
        'is_president': is_president,
    })

def publications(request):
    """Liste avec pagination pour les articles."""
    articles_list = Article.objects.filter(publie=True).order_by('-date_publication')
    
    # Pagination : 9 articles par page
    paginator = Paginator(articles_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Opportunités (généralement moins nombreuses, pas de pagination ici sauf besoin)
    opportunities = Opportunity.objects.filter(
        publie=True, 
        reserve_aux_membres=False,
        date_limite__gte=timezone.now().date()
    ).order_by('date_limite')

    return render(request, 'web_public/publications/publications.html', {
        'articles': page_obj, 
        'opportunities': opportunities,
    })

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, publie=True)
    # Incrémenter le compteur de lecture
    article.lectures += 1
    article.save(update_fields=['lectures'])
    
    return render(request, 'web_public/publications/article_detail.html', {'article': article})

def opportunity_detail(request, pk):
    # On vérifie que l'opportunité est bien publique
    opportunity = get_object_or_404(Opportunity, pk=pk, publie=True, reserve_aux_membres=False)
    return render(request, 'web_public/publications/opportunity_detail.html', {'opp': opportunity})


from django.shortcuts import render
from cms.models import Mandat, BoardMembership

def adhesion_info_view(request):
    # 1. On récupère le mandat actif via ton modèle Mandat
    mandat_actif = Mandat.objects.filter(actif=True).first()
    
    tresorier_nom = None
    tresorier_phone = None

    if mandat_actif:
        # 2. On cherche le membre du bureau avec le rôle Trésorier
        # Note : On utilise 'titre__icontains' pour être sûr de capter "Trésorier" ou "Trésorière"
        be_tresorier = BoardMembership.objects.filter(
            mandat=mandat_actif,
            role__titre__icontains="Trésorier"
        ).select_related('membership__user').first()

        if be_tresorier:
            user_obj = be_tresorier.membership.user
            tresorier_nom = f"{user_obj.first_name} {user_obj.last_name}"
            
            # 3. Récupération du téléphone sur ton modèle User
            # On vérifie d'abord 'phone', sinon 'secondary_phone'
            tresorier_phone = user_obj.phone  or "Numéro non renseigné"
            tresorier_phone_sec = user_obj.secondary_phone  or "Numéro non renseigné"

    context = {
        'frais_adhesion': 5000,
        'cotisation_annuelle': 10000,
        'tresorier_nom': tresorier_nom,
        'tresorier_phone': tresorier_phone,
        'tresorier_phone_sec': tresorier_phone_sec,
        'mandat_nom': mandat_actif.nom if mandat_actif else "Mandat en cours"
    }
    return render(request, 'web_public/adhesion/adhesion_info.html', context)


from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from organizations.models import Organization

def contact_view(request):
    if request.method == "POST":
        nom = request.POST.get('name')
        email = request.POST.get('email')
        sujet = request.POST.get('subject')
        message_content = request.POST.get('message')
        
        corps_email = f"De: {nom} <{email}>\nObjet: {sujet}\n\nMessage:\n{message_content}"
        
        try:
            send_mail(
                f"[Contact Site AMEE] {sujet}",
                corps_email,
                email,
                ['contact@amee-ml.com'],
                fail_silently=False,
            )
            messages.success(request, "Votre message a été transmis avec succès.")
        except Exception:
            messages.error(request, "Échec de l'envoi. Vérifiez votre connexion ou réessayez.")
        
        return redirect('contact')

    partenaires = Organization.objects.filter(est_actif=True)
    
    # Données statiques pour la FAQ
    faq_items = [
        {
            "q": "Quelles sont les conditions d'adhésion pour un consultant ?",
            "a": "Le réseau est réservé aux professionnels justifiant soit de 2 ans d'expérience spécifique en Évaluation Environnementale et Sociale (EES), soit de 5 ans d'expérience dans un domaine connexe."
        },
        {
            "q": "Quels sont les tarifs pour les membres individuels ?",
            "a": "Les frais d'inscription s'élèvent à 5 000 FCFA, suivis d'une cotisation annuelle obligatoire de 10 000 FCFA."
        },
        {
            "q": "Un Bureau d'Étude peut-il intégrer le réseau ?",
            "a": "Oui, les personnes morales peuvent devenir membres de l'AMEE moyennant une cotisation annuelle de 100 000 FCFA."
        },
        {
            "q": "Être membre donne-t-il accès au Roster des consultants ?",
            "a": "L'adhésion donne accès aux ressources internes et opportunités réservées. Cependant, l'inscription au Roster des consultants est un processus distinct soumis à la validation rigoureuse du Secrétaire après examen du Bureau."
        }
    ]

    return render(request, 'web_public/contact.html', {
        'partenaires': partenaires,
        'faq_items': faq_items
    })