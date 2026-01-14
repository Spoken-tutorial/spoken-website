from django.core.management.base import BaseCommand, CommandError

from pathlib import Path
import re
import json
import requests
from creation.models import *


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--ids",
            type=str,
            required=True,
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
            ids = [int(x.strip()) for x in raw.split(",") if x.strip() != ""]
            for course_id in ids:

                try:
                    foss = FossCategory.objects.using('stats').get(id=course_id, show_on_homepage=1)
                    foss_format = foss.foss.strip().replace(' ','+')
                    qs = TutorialResource.objects.using('stats').filter(tutorial_detail__foss_id=foss.id, status = 1)
                    languages = list(qs.distinct().order_by('language__name').values_list('language__name', flat=True))
                    categories = list(foss.category.all().values_list('name', flat=True))
                    course_data = {
                        "course_id": foss.id,
                        "course": foss.foss,
                        "course_url": f"https://spoken-tutorial.org/tutorial-search/?search_foss={foss_format}&search_language=",
                        "categories": categories,
                        "languages": languages
                    }
                    course_data['tutorials'] = []
                    tutorial_resources = qs.select_related('tutorial_detail', 'language', 'tutorial_detail__foss', 'common_content')
                    for tr in tutorial_resources:
                        
                        title_formatted = tr.tutorial_detail.tutorial.strip().replace(' ', '+')
                        title_formatted_srt = tr.tutorial_detail.tutorial.strip().replace(' ', '-')
                        language = tr.language.name
                        try:
                            duration = TutorialDuration.objects.using('stats').get(tresource=tr).duration
                        except:
                            duration = None
                        tutorial_script = self.extract_text_one_paragraph(foss.id, tr.tutorial_detail.id, title_formatted_srt, language)
                        tutorial_data = {
                            "tutorial_resource_id": tr.id,
                            "tutorial_detail_id": tr.tutorial_detail.id,
                            "title": tr.tutorial_detail.tutorial.strip(),
                            "url": f"https://spoken-tutorial.org/watch/{foss_format}/{title_formatted}/{language}/",
                            "keywords": tr.common_content.keyword,
                            "outline": tr.outline,
                            "language": language,
                            "script url": f"https://script.spoken-tutorial.org/index.php/{tr.script}",
                            "tutorial_script": tutorial_script,
                            "duration": duration,
                            "level": tr.tutorial_detail.level.level

                        }
                        course_data['tutorials'].append(tutorial_data)
                        self.stdout.write(self.style.SUCCESS(f"Added to tutorials: {tr.tutorial_detail.tutorial} - {language}"))
                except FossCategory.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"No foss found with id: {course_id}. show_on_homepage = 1"))

            # Ensure parent folder exists
            out_path.parent.mkdir(parents=True, exist_ok=True)

            # Write JSON
            with out_path.open("w", encoding="utf-8") as f:
                if course_data:
                    json.dump(course_data, f, ensure_ascii=False, indent=2)
                else:
                    self.stderr.write(self.style.ERROR(f"No data found"))
            self.stdout.write(self.style.SUCCESS(f"Wrote JSON to: {out_path.resolve()}"))
        except ValueError:
            raise CommandError(f"--ids must be comma-separated integers. Got: {raw}")

        if not ids:
            raise CommandError("--ids is empty")

        self.stdout.write(f"IDs: {ids}")


    def extract_text_one_paragraph(self, course_id, tr_id,title,lang):
        srt_path = "/Users/ankita/workspace/projects/spoken/project/spoken-website/media/videos/48/478/Introduction-to-BASH-Shell-Scripting-English.srt"
        url = f"https://spoken-tutorial.org/media/videos/{course_id}/{tr_id}/{title}-{lang}.srt"
        try:
            res = requests.get(url, timeout=30)
            res.raise_for_status() # raises error for 4xx/5xx
            srt_text = res.text
        except: 
            self.stderr.write(self.style.ERROR(f"Error for srt file: {url}"))
            srt_text = ""
        TAG_RE = re.compile(r"<[^>]+>")
        TIME_RE = re.compile(r"^\d{2}:\d{2}:\d{2}\s*-->\s*\d{2}:\d{2}:\d{2}")
        # lines = Path(srt_path).read_text(encoding="utf-8", errors="ignore").splitlines()
        lines = srt_text.splitlines()

        out = []
        for line in lines:
            s = line.strip()
            if not s or s.isdigit() or TIME_RE.match(s):
                continue
            s = TAG_RE.sub("", s)
            s = re.sub(r"\s+", " ", s).strip()
            if s:
                out.append(s)
        data = " ".join(out)
        return data