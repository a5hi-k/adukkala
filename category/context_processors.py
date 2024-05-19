# used to make things available in every page
# go to settings and add context processors there

from . models import Category

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)