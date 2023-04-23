# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django import template

# Internal
from home.models import Media
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

register = template.Library()

@register.filter
def use_media(set, media_use):
    img_type, img_attr = media_use.split('.')
    try:
        if set.model_name() == 'promo':
            media = set.media
        else:
            media = set.media.filter(
                media_use=img_type
                ).first()
            
        if img_attr == 'src':
            return media.file.name
        elif img_attr == 'descr':
            return media.description
    except:
        media = Media.objects.get(
            slug=f'no-image-{img_type.lower()}'
            )

        if img_attr == 'src':
            return media.file.name
        elif img_attr == 'descr':
            return media.description
        return None