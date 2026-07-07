# NOTE : After running  bash shell-scripts/generate_hst_videos.sh this file should run

#!/bin/bash

set -e


# Folder downloaded from Google Drive
SRC_ROOT="/beta_st/hst_thumbnails"

# Spoken media folder
DEST_ROOT="/beta_st/django_spoken.test/spoken-website/media/videos"

# Activate virtualenv
source /beta_st/django_spoken.test/env_py3/bin/activate

PYTHON_BIN=$(which python)

TMPFILE="/tmp/hst_thumbnail_mapping.txt"

echo "=========================================="
echo "Generating thumbnail mapping..."
echo "=========================================="

"$PYTHON_BIN" manage.py shell <<'PYEOF' > "$TMPFILE"

from creation.management.hst import FOSS_FOLDER
from creation.models import TutorialResource

# Google Drive folder names for each FOSS
THUMBNAIL_FOLDER = {
    183: "Pregnancy, Breastfeeding and Growth Monitoring",
    184: "6 to 24 Months Complementary Feeding",
    185: "Teens to Adults Nutrients, Insulin and Recipes",
}

resources = (
    TutorialResource.objects
    .filter(
        tutorial_detail__foss_id__in=list(FOSS_FOLDER.keys()),
        language_id=22,
        is_hst=True
    )
    .select_related("tutorial_detail")
)

for r in resources:

    if not r.video:
        continue

    print(
        "{}\t{}\t{}\t{}".format(
            r.tutorial_detail.foss_id,
            THUMBNAIL_FOLDER[r.tutorial_detail.foss_id],
            r.tutorial_detail_id,
            r.video
        )
    )

PYEOF


echo ""
echo "Copying thumbnails..."
echo ""

while IFS=$'\t' read -r FOSS_ID THUMB_FOLDER TUTORIAL_DETAIL_ID VIDEO
do

    [ -z "$VIDEO" ] && continue

    SEARCH_DIR="$SRC_ROOT/$THUMB_FOLDER"

    DEST="$DEST_ROOT/$FOSS_ID/$TUTORIAL_DETAIL_ID"

    mkdir -p "$DEST"

    BASENAME=$(basename "$VIDEO")
    BASENAME="${BASENAME%.*}"

    NAME="$BASENAME"

    NAME="${NAME%-English}"
    NAME="${NAME%- English}"
    NAME="${NAME% English}"
    NAME="${NAME%-English}"

    FOUND=""

    while read FILE
    do

        FILEBASE=$(basename "$FILE")
        FILEBASE="${FILEBASE%.*}"

        if [[ "${FILEBASE,,}" == "${NAME,,}" ]]; then
            FOUND="$FILE"
            break
        fi

    done < <(find "$SEARCH_DIR" -type f)

    if [ -n "$FOUND" ]; then

        cp -f "$FOUND" "$DEST/"

        echo "✓ $(basename "$FOUND")"
        echo "  -> $DEST"

    else

        echo "✗ Thumbnail not found:"
        echo "  Folder : $THUMB_FOLDER"
        echo "  Name   : $NAME"

    fi

done < "$TMPFILE"

rm -f "$TMPFILE"

echo ""
echo "=========================================="
echo "Thumbnail migration completed."
echo "=========================================="