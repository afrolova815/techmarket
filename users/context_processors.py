from catalog.mixins import menu


def get_catalog_context(request):
    return {'mainmenu': menu}