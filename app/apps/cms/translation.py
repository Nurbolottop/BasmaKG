from modeltranslation.translator import TranslationOptions, register

from apps.cms.models import FAQ, Advantage, Page, Review, Service, Step


@register(Service)
class ServiceTR(TranslationOptions):
    fields = ('name', 'short_description', 'description', 'features', 'price_text', 'term_text',
              'meta_title', 'meta_description')


@register(Advantage)
class AdvantageTR(TranslationOptions):
    fields = ('title', 'text')


@register(Step)
class StepTR(TranslationOptions):
    fields = ('title', 'text')


@register(FAQ)
class FAQTR(TranslationOptions):
    fields = ('question', 'answer')


@register(Review)
class ReviewTR(TranslationOptions):
    fields = ('company', 'text')


@register(Page)
class PageTR(TranslationOptions):
    fields = ('title', 'lead', 'content', 'meta_title', 'meta_description')
