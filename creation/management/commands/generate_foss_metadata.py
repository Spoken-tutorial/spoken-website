from django.core.management.base import BaseCommand
from creation.models import FossCategory, TutorialDetail, TutorialResource, TutorialDuration, Language                       
import uuid
from django.conf import settings
from creation.views import get_video_info
from django.db.models import Q
import csv
from spoken.config import SPOKEN_BASE_URL, SCRIPT_URL


class Command(BaseCommand):
        
    def handle(self, *args, **options):
        print("Generating Foss Metadata. Please wait...")
        meta_file_name = 'metadata_'+uuid.uuid4().hex+".csv"
        with open(settings.MEDIA_ROOT + meta_file_name, "w+", newline='') as metafile:
            metawriter = csv.writer(metafile)
            metawriter.writerow(["course_id","title","duration","deeplink_url","wikipage_url","description","keywords","language","video_count"])
            metadata = []
            foss = FossCategory.objects.all()
            for f in foss:
                course_duration_en = 0
                keywords = []
                tr_en= TutorialResource.objects.filter(Q(status=1) | Q(status=2),tutorial_detail__foss=f, language__name='English')
                for tr in tr_en:
                    #calculate course duration
                    video_path = settings.MEDIA_ROOT+'videos/'+str(tr.tutorial_detail.foss.pk)+'/'+str(tr.tutorial_detail.pk)+'/'+tr.video
                    video_info = get_video_info(video_path)
                    course_duration_en += video_info['total']
                    #keywords
                    try:
                        keywords += tr.tutorial_detail.tutorial_detail.keyword_as_list()
                    except:
                        pass
                deeplink_url = (f"{SPOKEN_BASE_URL}/tutorial-search/"f"?search_foss={f.foss}&search_language=English")
                wiki_url = (f"{SCRIPT_URL}{f.foss.replace(' ', '_')}")
                if tr_en.count() >= 1:
                    metadata = [str(f.id), f.foss, self.convert(course_duration_en), deeplink_url, wiki_url, f.description, ", ".join(keywords), 'English', str(tr_en.count())]
                    metawriter.writerow(metadata)
                
                languages = Language.objects.all().exclude(name='English')
                for l in languages:
                    tr = TutorialResource.objects.filter(Q(status=1) | Q(status=2),tutorial_detail__foss=f, language=l)
                    deeplink_url = (f"{SPOKEN_BASE_URL}/tutorial-search/"f"?search_foss={f.foss}&search_language={l.name}")
                    if tr.count() == tr_en.count() and tr.count() >=1:
                        metadata = [str(f.id), f.foss, self.convert(course_duration_en), deeplink_url, wiki_url, f.description, ", ".join(keywords), l.name, str(tr.count())]
                        metawriter.writerow(metadata)
                    else:
                        course_duration = 0
                        for t in tr:
                            video_path = settings.MEDIA_ROOT+'videos/'+str(t.tutorial_detail.foss.pk)+'/'+str(t.tutorial_detail.pk)+'/'+t.video
                            video_info = get_video_info(video_path)
                            course_duration += video_info['total']
                        if tr.count() >= 1:
                            metadata = [str(f.id), f.foss, self.convert(course_duration), deeplink_url, wiki_url, f.description, ", ".join(keywords), l.name, str(tr.count())]
                            metawriter.writerow(metadata)
            print("Metadata File Generated. Please find the file at location given below.")
            print(metafile.name)

    def convert(self, seconds): 
        seconds = seconds % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%dhr%02dmins%02dseconds" % (hour, minutes, seconds) 

