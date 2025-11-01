from django.contrib import sitemaps
from django.urls import reverse

class SpokenStaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
                'home', 
                'tutorial-search', 
                'keyword-search',
                'nmeict_intro',
                'series',
                'what_is_spoken_tutorial',
                'testimonials',
                'view_brochures',
                'cms:login', 
                'cms:register', 
                'statistics:maphome', 
                'statistics:motion_chart', 
                'statistics:statistics_training', 
                'statistics:statistics_online_test',
                'statistics:statistics_content',
                'statistics:acdemic_center',
                'statistics:learners'
            ]

    def location(self, item):
        return reverse(item)