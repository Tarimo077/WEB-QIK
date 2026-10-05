from .models import SiteSetting

def site_settings(request):
    """
    Exposes site_settings dictionary to all templates.
    Provides robust fallback defaults matching qiksearch.co.ke.
    """
    defaults = {
        "site_name": "Qiksearch Kenya",
        "announcement_text": "Welcome to Qiksearch",
        "phone_number": "+254 700 007 552",
        "phone_raw": "0700007552",
        "whatsapp_number": "254700007552",
        "email_address": "info@qiksearch.co.ke",
        "physical_address": "Opposite City stadium along Lusaka road Industrial area, Nairobi, Kenya",
        "business_hours": "Monday to Saturday, 8:00 AM – 6:00 PM",
        "hero_badge": "ROOTED IN KENYA · GROWING TOGETHER",
        "hero_title": "Practical farm tools that get the work done.",
        "hero_description": "Browse silage choppers, hay balers, animal feed processing machinery and pasture seeds with direct delivery across Kenya.",
        "about_story_short": "Qiksearch is a Kenyan social enterprise contributing towards improving agricultural communities’ livelihoods and resilience by enhancing farming productivity, minimizing pre and post-harvest losses, and curbing climate change effects in arid and semi-arid lands.",
    }
    try:
        settings_qs = SiteSetting.objects.all()
        for s in settings_qs:
            if s.value:
                defaults[s.key] = s.value
    except Exception:
        pass
    return {"site_settings": defaults}
