def get_option( key, type = int ):
    from .models import SiteOption
    obj = SiteOption()
    return obj.get_option( key )
