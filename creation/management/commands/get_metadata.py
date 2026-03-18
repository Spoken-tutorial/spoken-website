from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from creation.models import *

from pathlib import Path
import re
import json
import requests
import os




class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--ids",
            type=str,
            required=False,
            help="Comma-separated integers, e.g. 1,2,3",
        )
        parser.add_argument(
            "--out",
            type=str,
            default="output.json",
            help="Output JSON file path (default: output.json)",
        )

    def handle(self, *args, **options):
        # python manage.py my_command --ids 1,2,3,10
        raw = options["ids"]
        out_path = Path(options["out"])
        try:
            if raw: 
                ids = [int(x.strip()) for x in raw.split(",") if x.strip() != ""]
            else:
                ids = [x.id for x in FossCategory.objects.using('stats').filter(show_on_homepage=1).only('id')]
            courses = FossCategory.objects.using('stats').filter(id__in=ids).order_by('foss')
            # define final data schema
            data = {}
            course_details = []
            total_size = 0.0
            total_video_size = 0.0
            total_srt_size = 0.0
            total_courses = 0
            total_tutorials = 0

            for course in courses:
                qs = TutorialResource.objects.using('stats').filter(status=1, tutorial_detail__foss_id=course.id)
                languages = qs.order_by('language__name').values_list('language__name', flat=True).distinct()
                
                # define individual course schema
                course_data = {
                    'course_id': course.id,
                    'course': course.foss,
                    'total_tutorials': qs.count(),
                    'total_languages': languages.count(),
                    'languages': list(languages)
                }
                course_total_size = 0.0
                course_video_size = 0.0
                course_srt_size = 0.0
                lang_based_details = []
                
                for lang in languages:
                    tr_recs = qs.filter(language__name=lang)
                    fsize = 0.0
                    vsize = 0.0
                    ssize = 0.0
                    for rec in tr_recs:
                        # calculate video size
                        filepath = 'videos/{}/{}/{}'.format(course.id, rec.tutorial_detail_id, rec.video)
                        if os.path.isfile(settings.MEDIA_ROOT + filepath):
                            #language based
                            fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            vsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            #course based
                            course_video_size += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            course_total_size += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            #total
                            total_video_size += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            total_size += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            

                            
                        # calculate str file size
                        ptr = filepath.rfind(".")
                        filepath = filepath[:ptr] + '.srt'
                        if os.path.isfile(settings.MEDIA_ROOT + filepath):
                            #language based
                            fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            ssize += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            #course based
                            course_srt_size += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            course_total_size += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            #total
                            total_srt_size += os.path.getsize(settings.MEDIA_ROOT + filepath)
                            total_size += os.path.getsize(settings.MEDIA_ROOT + filepath)
                    
                    # define individual lang-course schema
                    lang_data = {
                        "lang": lang,
                        'total_tutorials': tr_recs.count(),
                        'size': f"{fsize / (1024*1024):.2f} MiB",
                        'videos_size': f"{vsize / (1024*1024):.2f} MiB",
                        'srt_size': f"{ssize / (1024*1024):.2f} MiB"
                    }
                    lang_based_details.append(lang_data)
                
                course_data['course_total_size'] = f"{course_total_size / (1024*1024):.2f} MiB"
                course_data['course_video_size'] = f"{course_video_size / (1024*1024):.2f} MiB"
                course_data['course_srt_size'] = f"{course_srt_size / (1024*1024):.2f} MiB"
                course_data['details'] = lang_based_details
                course_details.append(course_data)

            
            data['total_size'] = f"{total_size / (1024*1024*1024):.2f} GB"
            data['total_video_size'] = f"{total_video_size / (1024*1024*1024):.2f} GB"
            data['total_srt_size'] = f"{total_srt_size / (1024*1024*1024):.2f} GB"
            data['courses'] = course_details
            
                
            # Ensure parent folder exists
            out_path.parent.mkdir(parents=True, exist_ok=True)

            # Write JSON
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS(f"Wrote JSON to: {out_path.resolve()}"))
        except ValueError:
            raise CommandError(f"--ids must be comma-separated integers. Got: {raw}")

        self.stdout.write(f"IDs: {ids}")