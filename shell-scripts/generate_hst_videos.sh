#!/bin/bash
set -e

echo "================================="
echo "Starting HST → Spoken migration"
echo "================================="

# ==================== SERVER CONFIG (COMMENTED OUT) ====================
HST_SERVER="Ayisha@beta.spoken-tutorial.org"
HST_ROOT="/beta_st/tomcat.new/health_data/Media/Content/Tutorial"
SPOKEN_MEDIA="/beta_st/django_spoken.test/spoken-website/media/videos"
VENV_PATH="/beta_st/django_spoken.test/env_py3"
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
fi
PYTHON_BIN="$VENV_PATH/bin/python"

# ==================== LOCAL CONFIG ====================
# HST_ROOT="./test_hst/Media/Content/Tutorial"
# SPOKEN_MEDIA="./media/videos"

# source /mnt/d/EDUPYRAMIDS/spoken-website/Python-3.6.15/venv36/bin/activate
# PYTHON_BIN=$(which python)

mkdir -p "$SPOKEN_MEDIA"

echo ""
echo -e "\033[1;34m[STEP 1]\033[0m Generating tutorial mapping..."
echo -e "\033[1;33mPython:\033[0m $PYTHON_BIN"
echo -e "\033[1;33mPWD:\033[0m $(pwd)"

# Run Python: stdout → mapping file, stderr → debug log
"$PYTHON_BIN" manage.py shell <<'PYEOF' 2>/tmp/hst_debug.log > /tmp/hst_mapping.txt
import sys
import re
import os

print("\033[92m[PYTHON STARTED]\033[0m", file=sys.stderr)

from django.db import connections

print("\033[92m[Django imports OK]\033[0m", file=sys.stderr)

from creation.management.hst import FOSS_FOLDER

print("\033[92m[FOSS_FOLDER imported]\033[0m", file=sys.stderr)

source = connections["healthdb"]
target = connections["default"]

print("\033[92m[DB connections created]\033[0m", file=sys.stderr)

VALID_FOSS = tuple(FOSS_FOLDER.keys())
topic_map = {}

print("\033[92m[Loading Spoken tutorials]\033[0m", file=sys.stderr)

# Load Spoken tutorials
with target.cursor() as cur:

    print("\033[93m[DEBUG 1] Running Spoken query\033[0m", file=sys.stderr)

    cur.execute("""
        SELECT
            id,
            tutorial,
            foss_id
        FROM creation_tutorialdetail
        WHERE foss_id IN %s
    """, [VALID_FOSS])

    spoken_rows = cur.fetchall()

    print("\033[92m[DEBUG 2] Spoken rows={}\033[0m".format(len(spoken_rows)),file=sys.stderr)

    for tutorial_detail_id, tutorial, foss_id in spoken_rows:

        if tutorial:
            topic_map[
                tutorial.strip().lower()
            ] = (
                tutorial_detail_id,
                foss_id
            )

print("\033[92m[DEBUG 3] Topic map={}\033[0m".format(len(topic_map)),file=sys.stderr)

print("\033[92m[DEBUG 7] Loading healthdb\033[0m", file=sys.stderr)

# Load HST tutorial_resource rows with video column
with source.cursor() as cur:
    cur.execute("""
        SELECT tutorial_id, topic_name, video
        FROM tutorial_resource
        WHERE topic_name IS NOT NULL
    """)
    rows = cur.fetchall()

print("\033[92m[DEBUG 8] healthdb rows = {}\033[0m".format(len(rows)), file=sys.stderr)

matched = 0
skipped = 0

print("\033[92m[DEBUG 9] Starting matching\033[0m", file=sys.stderr)

for tutorial_id, topic_name, video_path in rows:
    if not topic_name:
        skipped += 1
        continue

    # Extract full name from video path
    # e.g., "Media/Content/Tutorial/1/Video/Cross Cradle Hold for Breastfeeding - English.mp4"
    full_name = None
    
    if video_path:
        # Get filename from path
        filename = os.path.basename(video_path)  # "Cross Cradle Hold for Breastfeeding - English.mp4"
        # Remove extension
        name_no_ext = os.path.splitext(filename)[0]  # "Cross Cradle Hold for Breastfeeding - English"
        # Remove language suffix
        full_name = re.sub(r'\s*[-–]\s*English\s*$', '', name_no_ext, flags=re.IGNORECASE).strip()
    
    # Try full name from video first
    if full_name:
        match_key = full_name.lower()
        if match_key in topic_map:
            td_id, foss_id = topic_map[match_key]
            print("\033[92mMATCH {}\033[0m".format(tutorial_id),file=sys.stderr)
            print(f"{tutorial_id}\t{td_id}\t{foss_id}")
            matched += 1
            continue
    
    # Fallback: try topic_name
    key = topic_name.strip().lower()
    if key in topic_map:
        td_id, foss_id = topic_map[key]
        print(f"{tutorial_id}\t{td_id}\t{foss_id}")
        matched += 1
        continue

    skipped += 1

print(f"Matched: {matched}, Skipped: {skipped}", file=sys.stderr)
PYEOF

echo ""
echo "=== MAPPING FILE ==="
cat /tmp/hst_mapping.txt
echo ""
echo "=== LINE COUNT ==="
wc -l /tmp/hst_mapping.txt
echo ""
echo -e "\033[1;35m=== DEBUG LOG ===\033[0m"
cat /tmp/hst_debug.log

# Check if mapping file has content
if [ ! -s /tmp/hst_mapping.txt ]; then
    echo ""
    echo "ERROR: Mapping file is empty! Nothing to copy."
    rm -f /tmp/hst_mapping.txt /tmp/hst_debug.log
    exit 1
fi

echo ""
echo "Copying files..."

while IFS=$'\t' read -r tutorial_id tutorial_detail_id foss_id
do
    # Skip empty lines
    [ -z "$tutorial_id" ] && continue

    echo ""
    echo "HST Tutorial → $tutorial_id"
    echo "Tutorial Detail → $tutorial_detail_id"
    echo "FOSS → $foss_id"

    SRC="$HST_ROOT/$tutorial_id"
    DEST="$SPOKEN_MEDIA/$foss_id/$tutorial_detail_id"

    if [ ! -d "$SRC" ]; then
        echo "Skipping: $SRC not found"
        continue
    fi

    mkdir -p "$DEST"
    mkdir -p "$DEST/resources"

find "$SRC" -type f | while read file
do

filename=$(basename "$file")
case "$file" in

*/Slide/*)
cp -f "$file" "$DEST/resources/"
echo -e "\033[92m✓ Slide:\033[0m $filename"
;;

*/Script/*|*/TimeScript/*|*/Video/*)

if [[ "$filename" =~ ([-[:space:]]English)\.(mp4|pdf|odt|webm|ogv)$ ]]
then

db_filename=$(
"$PYTHON_BIN" manage.py shell -c "
from creation.models import TutorialResource

r = TutorialResource.objects.filter(
tutorial_detail_id=$tutorial_detail_id
).exclude(video='').first()

print(r.video if r else '$filename')
" 2>/dev/null | tail -1
)

if [ -z "$db_filename" ]; then
    db_filename="$filename"
fi

cp -f \
"$file" \
"$DEST/$db_filename"

echo -e "\033[92m✓ COPIED:\033[0m"

echo "SOURCE → $filename"
echo "DB NAME → $db_filename"

else

echo -e "\033[31mSKIPPED:\033[0m $filename"

fi

;;

esac

done

done < /tmp/hst_mapping.txt

rm -f /tmp/hst_mapping.txt /tmp/hst_debug.log

echo ""
echo "================================="
echo "Migration completed"
echo "Stored under media/videos/"
echo "================================="