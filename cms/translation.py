from modeltranslation.translator import register, TranslationOptions
from .models import Article, Gallery,Resource,Opportunity,Mandat

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('titre', 'contenu', 'slug')

@register(Opportunity)
class OpportunityTranslationOptions(TranslationOptions):
    fields = ('titre', 'description', 'slug')


@register(Resource)
class ResourceTranslationOptions(TranslationOptions):
    fields = ('titre', 'description', 'slug')

@register(Mandat)
class MandatTranslationOptions(TranslationOptions):
    fields = ('nom','mot_president',)

@register(Gallery)
class GalleryTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'slug')