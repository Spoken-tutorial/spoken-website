from django.contrib.sitemaps import Sitemap
from creation.models import TutorialResource
 
 
class TutorialSitemap(Sitemap):    
    changefreq = "weekly"
    priority = 0.9
 
    def items(self):
        return TutorialResource.objects.filter(status__gt=0)
 
    def lastmod(self, obj):
        return obj.updated