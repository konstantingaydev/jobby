from django import template
register = template.Library()

@register.filter
def has_profile(user):
    try:
        return hasattr(user, 'profile') and user.profile is not None
    except Exception:
        return False
