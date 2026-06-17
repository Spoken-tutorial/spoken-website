import os
from django.core.management.base import BaseCommand
from django.db import connections, transaction

# Import configuration from the project root
try:
    from config import TOPICS_BY_FOSS, FOSS_FOLDER
except ImportError:
    raise ImportError("Could not import 'config' module. Make sure config.py is in the Python path.")


class Command(BaseCommand):
    help = "Migrate Health tutorial resources to Spoken platform"

    def handle(self, *args, **kwargs):
        source = connections["healthdb"]
        target = connections["default"]

        self.stdout.write("Starting migration using topic_name mapping...")

        # ------------------------------------------------------------------
        # Build lookup structures from TOPICS_BY_FOSS
        # ------------------------------------------------------------------
        topic_to_foss = {}          # normalized topic -> foss_id
        order_counter = {}          # foss_id -> next order number
        topic_order_map = {}        # (foss_id, normalized topic) -> order

        for foss_id, topics in TOPICS_BY_FOSS.items():
            order_counter[foss_id] = 0
            for topic in topics:
                normalized = topic.strip().lower()
                topic_to_foss[normalized] = foss_id
                order_counter[foss_id] += 1
                order_num = order_counter[foss_id]
                topic_order_map[(foss_id, normalized)] = order_num

        # ------------------------------------------------------------------
        # Ensure the user 'hst@gmail.com' exists and get its ID
        # ------------------------------------------------------------------
        user_email = "hst@gmail.com"
        user_id = None
        with target.cursor() as dst:
            dst.execute("SELECT id FROM auth_user WHERE email = %s", [user_email])
            row = dst.fetchone()
            if row:
                user_id = row[0]
                self.stdout.write(f"Found existing user '{user_email}' with id={user_id}")
            else:
                dst.execute("""
                    INSERT INTO auth_user (password, is_superuser, username, first_name, last_name,
                                           email, is_staff, is_active, date_joined)
                    VALUES ('', 0, 'hst', '', '', %s, 0, 1, NOW())
                """, [user_email])
                dst.execute("SELECT LAST_INSERT_ID()")
                user_id = dst.fetchone()[0]
                self.stdout.write(f"Created new user '{user_email}' with id={user_id}")

        # ------------------------------------------------------------------
        # Fetch distinct topic names from source (ignore NULL)
        # ------------------------------------------------------------------
        with source.cursor() as src:
            src.execute("SELECT DISTINCT topic_name FROM tutorial_resource WHERE topic_name IS NOT NULL")
            distinct_topics = [row[0] for row in src.fetchall()]

        # Cache for (foss_id, topic_name) -> tutorial_detail_id
        topic_detail_cache = {}

        with target.cursor() as dst:
            for raw_topic in distinct_topics:
                if not raw_topic:
                    continue
                normalized = raw_topic.strip().lower()
                foss_id = topic_to_foss.get(normalized)
                if foss_id is None:
                    self.stdout.write(self.style.WARNING(
                        f"No FOSS mapping for topic: '{raw_topic}' – will be skipped"
                    ))
                    continue

                order_num = topic_order_map.get((foss_id, normalized), 0)
                if order_num == 0:
                    self.stdout.write(self.style.WARNING(
                        f"Topic '{raw_topic}' has a foss_id {foss_id} but no order defined – using order=0"
                    ))

                dst.execute("""
                    SELECT id FROM creation_tutorialdetail
                    WHERE foss_id = %s AND tutorial = %s
                """, [foss_id, raw_topic])
                existing = dst.fetchone()
                if existing:
                    topic_detail_cache[(foss_id, raw_topic)] = existing[0]
                else:
                    dst.execute("""
                        INSERT INTO creation_tutorialdetail
                        (foss_id, tutorial, level_id, `order`, user_id, created, updated)
                        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                    """, [foss_id, raw_topic, 1, order_num, user_id])
                    dst.execute("SELECT LAST_INSERT_ID()")
                    new_id = dst.fetchone()[0]
                    topic_detail_cache[(foss_id, raw_topic)] = new_id
                    self.stdout.write(f"Created tutorial_detail id={new_id} for '{raw_topic}' (foss={foss_id}, order={order_num})")

        # ------------------------------------------------------------------
        # Migrate all tutorial_resource rows
        # ------------------------------------------------------------------
        inserted = 0
        failed = 0

        with source.cursor() as src:
            src.execute("""
                SELECT
                    tutorial_id,
                    date_added,
                    keyword,
                    keyword_status,
                    outline,
                    outline_status,
                    script,
                    script_status,
                    slide,
                    slide_status,
                    enabled,
                    timescript,
                    video,
                    video_status,
                    user_keyword,
                    user_outline,
                    user_script,
                    user_slide,
                    user_video,
                    topic_name,
                    outline_path,
                    citation
                FROM tutorial_resource
            """)
            rows = src.fetchall()

        with target.cursor() as dst:
            for row in rows:
                try:
                    (tutorial_id, date_added, keyword, keyword_status, outline, outline_status,
                     script, script_status, slide, slide_status, enabled, timescript, video,
                     video_status, user_keyword, user_outline, user_script, user_slide,
                     user_video, topic_name, outline_path, citation) = row

                    if not topic_name:
                        self.stdout.write(self.style.WARNING(f"Skipping tutorial_id={tutorial_id}: no topic_name"))
                        failed += 1
                        continue

                    normalized = topic_name.strip().lower()
                    foss_id = topic_to_foss.get(normalized)
                    if not foss_id:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping tutorial_id={tutorial_id}: unknown topic '{topic_name}'"
                        ))
                        failed += 1
                        continue

                    cache_key = (foss_id, topic_name)
                    tutorial_detail_id = topic_detail_cache.get(cache_key)
                    if not tutorial_detail_id:
                        self.stdout.write(self.style.ERROR(f"No tutorial_detail_id for '{topic_name}'"))
                        failed += 1
                        continue

                    if not slide:
                        self.stdout.write(self.style.WARNING(f"Skipping tutorial_id={tutorial_id}: slide path is empty or NULL"))
                        failed += 1
                        continue
                    slide_filename = os.path.basename(slide)

                    foss_folder = FOSS_FOLDER.get(foss_id, "Unknown")
                    topic_slug = topic_name.replace(' ', '-')
                    script_path = f"{foss_folder}/C2/{topic_slug}/English"
                    timed_script_path = f"{foss_folder}/C2/{topic_slug}/English-timed"
                    video_filename = f"{topic_slug}-English.webm"

                    enabled_int = 1 if enabled and enabled != b'\x00' else 0

                    with transaction.atomic():
                        dst.execute("""
                            INSERT INTO creation_tutorialcommoncontent
                            (tutorial_detail_id,
                             slide, slide_user_id, slide_status,
                             code, code_user_id, code_status,
                             assignment, assignment_user_id, assignment_status,
                             prerequisite_id, prerequisite_user_id, prerequisite_status,
                             keyword, keyword_user_id, keyword_status,
                             additional_material, additional_material_status, additional_material_user_id,
                             created, updated)
                            VALUES (%s,
                                    %s, %s, %s,
                                    %s, %s, 0,
                                    '', %s, 0,
                                    NULL, %s, 0,
                                    %s, %s, %s,
                                    NULL, 0, NULL,
                                    NOW(), NOW())
                        """, [
                            tutorial_detail_id,
                            slide_filename, user_id, slide_status,
                            slide_filename, user_id,
                            user_id,
                            user_id,
                            keyword, user_id, keyword_status
                        ])

                        dst.execute("SELECT LAST_INSERT_ID()")
                        common_content_id = dst.fetchone()[0]

                        dst.execute("""
                            INSERT INTO creation_tutorialresource
                            (tutorial_detail_id, common_content_id, language_id,
                             outline, outline_user_id, outline_status,
                             script, script_user_id, script_status,
                             timed_script,
                             video, video_user_id, video_status,
                             video_id, playlist_item_id, video_thumbnail_time,
                             status, version, hit_count,
                             created, updated, publish_at,
                             assignment_status, extension_status, submissiondate,
                             is_unrestricted, is_on_youtube)
                            VALUES (%s, %s, 22,
                                    %s, %s, %s,
                                    %s, %s, %s,
                                    %s,
                                    %s, %s, %s,
                                    '', '', '00:00:00',
                                    %s, 1, 0,
                                    %s, NOW(), NOW(),
                                    0, 0, NOW(),
                                    0, 0)
                        """, [
                            tutorial_detail_id, common_content_id,
                            outline, user_id, outline_status,
                            script_path, user_id, script_status,
                            timed_script_path,
                            video_filename, user_id, video_status,
                            enabled_int, date_added
                        ])

                        inserted += 1

                except Exception as e:
                    failed += 1
                    self.stdout.write(self.style.ERROR(
                        f"Row with tutorial_id={row[0] if row else 'unknown'} failed: {e}"
                    ))

        self.stdout.write(self.style.SUCCESS(
            f"Migration completed. Inserted={inserted}, Failed={failed}"
        ))