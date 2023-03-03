from django import template

register = template.Library()

@register.filter
def use_media(set, media_use):
    try:
        # Change file.name to URL after implementing S3
        media = set.media.filter(media_use=media_use).first().file.name
    except:
        return None
    return media
