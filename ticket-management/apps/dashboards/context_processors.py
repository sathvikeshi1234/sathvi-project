from .models import SiteSettings


def site_settings(request):
    try:
        s = SiteSettings.get_solo()
    except Exception:
        s = None
    return {"site_settings": s}
