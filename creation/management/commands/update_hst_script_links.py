import os
import re

from django.core.management.base import BaseCommand
from django.db import connections

from creation.management.hst import TOPICS_BY_FOSS
from creation.models import TutorialDetail, TutorialResource


SCRIPT_BASE = "http://health.spoken-tutorial.org/OriginalScript"

def normalize(text):
    if not text:
        return ""

    text = text.lower()

    text = text.replace("&", "and")

    text = re.sub(r"[-_]", " ", text)

    text = re.sub(r"\bnon[- ]?veg\b", "non vegetarian", text)
    text = re.sub(r"\bveg\b", "vegetarian", text)

    text = re.sub(r"\bwoman\b", "women", text)
    text = re.sub(r"\bfoods\b", "food", text)

    text = text.replace("12-18", "12 to 18")
    text = text.replace("19-24", "19 to 24")
    text = text.replace("8-11", "8 to 11")

    text = text.replace("1st", "first")

    text = re.sub(r"[^\w\s]", " ", text)
    text = text.replace("mothers milk", "mother s milk")
    text = text.replace("other milk substitutes", "other substitutes")

    text = re.sub(r"\s+", " ", text)

    return text.strip()

class Command(BaseCommand):
    help = "Update Spoken TutorialResource script URLs for migrated HST tutorials"

    def handle(self, *args, **kwargs):

        source = connections["healthdb"]

        self.stdout.write("Updating HST script URLs...")

        topic_to_foss = {}

        for foss_id, topics in TOPICS_BY_FOSS.items():
            for topic in topics:
                topic_to_foss[normalize(topic)] = foss_id

        tutorial_lookup = {}

        for td in TutorialDetail.objects.all():
            tutorial_lookup[
                (td.foss_id, normalize(td.tutorial))
            ] = td

        with source.cursor() as cur:

            cur.execute("""
                SELECT
                    tr.tutorial_id,
                    t.topic_name,
                    tr.video

                FROM tutorial_resource tr

                JOIN contributor_role cr
                    ON cr.id = tr.con_assigned_tutorial

                JOIN topic_category tc
                    ON tc.topic_category_id = cr.topic_cat_id

                JOIN topic t
                    ON t.topic_id = tc.topic_id

                JOIN language l
                    ON l.lan_id = cr.language_id

                WHERE tr.enabled = b'1'
                AND tr.added_queue = b'1'
                AND l.lan_id = 22
                AND tr.video IS NOT NULL

                ORDER BY tr.tutorial_id DESC
            """)

            rows = cur.fetchall()

        updated = 0
        skipped = 0

        for tutorial_id, topic_name, video_path in rows:

            if not topic_name:
                skipped += 1
                continue

            normalized_topic = normalize(topic_name)

            foss_id = topic_to_foss.get(normalized_topic)

            if foss_id is None:
                for topic, mapped_foss in topic_to_foss.items():
                    if normalized_topic in topic or topic in normalized_topic:
                        foss_id = mapped_foss
                        break

            if foss_id is None:
                self.stdout.write(
                    self.style.WARNING(
                        "No FOSS mapping for '{}'".format(topic_name)
                    )
                )
                skipped += 1
                continue

            tutorial_name = topic_name

            if video_path:

                filename = os.path.basename(video_path)

                filename = os.path.splitext(filename)[0]

                # Remove "- English", "- English (1)" etc.
                filename = re.sub(
                    r"\s*[-–]\s*English(\s*\(\d+\))?$",
                    "",
                    filename,
                    flags=re.IGNORECASE
                ).strip()

                tutorial_name = filename

            tutorial_detail = tutorial_lookup.get(
                (foss_id, normalize(tutorial_name))
            )

            if tutorial_detail is None:
                tutorial_detail = tutorial_lookup.get(
                    (foss_id, normalize(topic_name))
                )

            if tutorial_detail is None:

                wanted = normalize(tutorial_name)

                for (fid, tut_name), td in tutorial_lookup.items():
                    if fid != foss_id:
                        continue

                    if wanted in tut_name or tut_name in wanted:
                        tutorial_detail = td
                        break

            if tutorial_detail is None:
                self.stdout.write(
                    self.style.WARNING(
                        "TutorialDetail not found: '{}' (video title='{}')".format(
                            topic_name,
                            tutorial_name
                        )
                    )
                )

                skipped += 1
                continue

            script_url = "{}/{}".format(
                SCRIPT_BASE,
                tutorial_id
            )

            count = TutorialResource.objects.filter(
                tutorial_detail=tutorial_detail,
                language_id=22,
                is_hst=True 
            ).update(
                script=script_url
            )

            if count:

                updated += count

                self.stdout.write(
                    self.style.SUCCESS(
                        "{} -> {}".format(
                            tutorial_name,
                            script_url
                        )
                    )
                )

            else:

                skipped += 1

                self.stdout.write(
                    self.style.WARNING(
                        "TutorialResource not found for '{}'".format(
                            tutorial_name
                        )
                    )
                )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS( "=======================================" ))
        self.stdout.write(self.style.SUCCESS("Updated : {}".format(updated)))
        self.stdout.write(self.style.WARNING("Skipped : {}".format(skipped)))
        self.stdout.write(self.style.SUCCESS("======================================="))