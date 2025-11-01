from django.core.management.base import BaseCommand
from creation.models import FossCategory, TutorialDetail, TutorialResource, TutorialDuration, Language                       
import uuid
from django.conf import settings
from creation.views import get_video_info
from django.db.models import Q
import csv

class Command(BaseCommand):
        
    def handle(self, *args, **options):
        print("Generating Foss Metadata. Please wait...")
        meta_file_name = 'tutorial_metadata_'+uuid.uuid4().hex+".csv"
        with open(settings.MEDIA_ROOT + meta_file_name, "w+", newline='') as metafile:
            metawriter = csv.writer(metafile)
            
            metawriter.writerow(["Fosstitle","TutorialTitle","VideoURL", "OriginalScript","TimedScript","language",])

            metadata = []
            foss = FossCategory.objects.filter(Q(available_for_jio=True) | Q(available_for_nasscom=True)).order_by('foss')
            for f in foss:
                
                tut_detail = TutorialDetail.objects.filter(foss=f).order_by('tutorial')
                
                for td in tut_detail:
                    tut_langs = Language.objects.filter(name__in=TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail=td).values_list('language__name'))
                    
                    
                    for l in tut_langs:

                        VideoURL="https://spoken-tutorial.org/watch/{}/{}/{}".format(f.foss, td.tutorial,l)

                        tr_en= TutorialResource.objects.get(Q(status=1) | Q(status=2),tutorial_detail=td, language__name=l)
                        
                        OriginalScript = "https://script.spoken-tutorial.org/index.php/{}".format(tr_en.script)
                        # https://script.spoken-tutorial.org/index.php/Advance-C/C2/Command-line-arguments-in-C/English

                        if l.name == "English":
                            TimedScript = "https://script.spoken-tutorial.org/index.php/{}".format(tr_en.timed_script)
                            # https://script.spoken-tutorial.org/index.php/Advance-C/C2/Command-line-arguments-in-C/English-timed
                        else:
                            TimedScript = ""

                        metadata = [f.foss, td.tutorial, VideoURL, OriginalScript, TimedScript, l]
                        metawriter.writerow(metadata)
                    
            print("Metadata File Generated. Please find the file at location given below.")
            print(metafile.name)
