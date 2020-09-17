from django.core.management.base import BaseCommand
from creation.models import FossCategory, TutorialDetail, TutorialResource, TutorialDuration, Language                       
import uuid
from django.conf import settings
from creation.views import get_video_info
from django.db.models import Q
import csv

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        meta_file_name = 'metadata_'+uuid.uuid4().hex+".csv"
        with open(settings.MEDIA_ROOT + meta_file_name, "w+", newline='') as metafile:
            metawriter = csv.writer(metafile)
            metawriter.writerow(["course_id","title","duration","deeplink_url","wikipage_url","description","keywords","language","video_count"])
            metadata = []
            foss = FossCategory.objects.all()
            for f in foss:
                course_duration = 0
                keywords = []
                tr_en= TutorialResource.objects.filter(Q(status=1) | Q(status=2),tutorial_detail__foss=f, language__name='English')
                for tr in tr_en:
                    #calculate course duration
                    video_path = settings.MEDIA_ROOT+'videos/'+str(tr.tutorial_detail.foss.pk)+'/'+str(tr.tutorial_detail.pk)+'/'+tr.video
                    video_info = get_video_info(video_path)
                    course_duration += video_info['total']
                    #keywords
                    try:
                        keywords += tr.tutorial_detail.tutorial_detail.keyword_as_list()
                    except:
                        pass
                deeplink_url="https://spoken-tutorial.org/tutorial-search/?search_foss={}&search_language={}".format(f.foss, 'English')
                wiki_url = "https://script.spoken-tutorial.org/index.php/{}".format(f.foss.replace(" ", "_"))
                metadata = [str(f.id), f.foss, self.convert(course_duration), deeplink_url, wiki_url, f.description, ", ".join(keywords), 'English', str(tr_en.count())]
                metawriter.writerow(metadata)
                
                languages = Language.objects.all().exclude(name='English')
                for l in languages:
                    tr = TutorialResource.objects.filter(Q(status=1) | Q(status=2),tutorial_detail__foss=f, language=l)
                    deeplink_url="https://spoken-tutorial.org/tutorial-search/?search_foss={}&search_language={}".format(f.foss, l.name)
                    if tr.count() == tr_en.count():
                        metadata = [str(f.id), f.foss, self.convert(course_duration), deeplink_url, wiki_url, f.description, ", ".join(keywords), l.name, str(tr.count())]
                        metawriter.writerow(metadata)
                    else:
                        for t in tr:
                            video_path = settings.MEDIA_ROOT+'videos/'+str(t.tutorial_detail.foss.pk)+'/'+str(t.tutorial_detail.pk)+'/'+t.video
                            video_info = get_video_info(video_path)
                            course_duration += video_info['total']
                        metadata = [str(f.id), f.foss, self.convert(course_duration), deeplink_url, wiki_url, f.description, ", ".join(keywords), l.name, str(tr_en.count())]
                        metawriter.writerow(metadata)

    def convert(self, seconds): 
        seconds = seconds % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%dhr%02dmins%02dseconds" % (hour, minutes, seconds) 

