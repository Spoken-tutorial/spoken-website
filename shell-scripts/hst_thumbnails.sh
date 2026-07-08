# NOTE : After running  bash shell-scripts/generate_hst_videos.sh this file should run

#!/bin/bash

set -e

# # Local Set Up

# SRC_ROOT="./hst_thumbnails"

# DEST_ROOT="./media/videos"

# source /mnt/d/EDUPYRAMIDS/spoken-website/Python-3.6.15/venv36/bin/activate

# Folder downloaded from Google Drive
SRC_ROOT="/beta_st/django_spoken.test/spoken-website/media/videos"

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

# Google Drive folder names for each FOSS in local SRC_ROOT
THUMBNAIL_FOLDER = {
    170: "Pregnancy, Breastfeeding and Growth Monitoring",
    171: "6 to 24 Months Complementary Feeding",
    172: "Teens to Adults Nutrients, Insulin and Recipes",
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

    #for local

    #SEARCH_DIR="$SRC_ROOT/$THUMB_FOLDER"

    #for server s

    SEARCH_DIR="$SRC_ROOT/$THUMB_FOLDER/$THUMB_FOLDER/thumbs"

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

    # Desired thumbnail name
    NEWNAME="$BASENAME"
    NEWNAME=$(echo "$NEWNAME" | sed -E 's/[[:space:]]*-[[:space:]]*English$//I')
    NEWNAME=$(echo "$NEWNAME" | sed -E 's/[[:space:]]+English$//I')

    # Check if destination already contains a thumbnail
    EXISTING=$(find "$DEST" -maxdepth 1 -type f \
        \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.webp" \) | head -1)

    if [ -n "$EXISTING" ]; then

        EXT="${EXISTING##*.}"
        TARGET="$DEST/${NEWNAME}.${EXT}"

        EXISTING_FILE=$(basename "$EXISTING")
        TARGET_FILE=$(basename "$TARGET")

        EXISTING_LOWER=$(echo "$EXISTING_FILE" | tr '[:upper:]' '[:lower:]')
        TARGET_LOWER=$(echo "$TARGET_FILE" | tr '[:upper:]' '[:lower:]')

        if [ "$EXISTING_LOWER" != "$TARGET_LOWER" ]; then

            # Completely different filename
            TMP="$DEST/.tmp_thumbnail_${RANDOM}.${EXT}"

            mv -f "$EXISTING" "$TMP"
            mv -f "$TMP" "$TARGET"

            echo "✓ Renamed thumbnail"
            echo "  $EXISTING_FILE"
            echo "  -> $TARGET_FILE"

        elif [ "$EXISTING_FILE" != "$TARGET_FILE" ]; then

            # Only case differs (needed on Windows/WSL)
            TMP="$DEST/.tmp_thumbnail_${RANDOM}.${EXT}"

            mv -f "$EXISTING" "$TMP"
            mv -f "$TMP" "$TARGET"

            echo "✓ Corrected filename case"
            echo "  $EXISTING_FILE"
            echo "  -> $TARGET_FILE"

        else

            echo "✓ Thumbnail already correctly named"
            echo "  $TARGET_FILE"

        fi

    elif [ -n "$FOUND" ]; then

        EXT="${FOUND##*.}"

        cp -f "$FOUND" "$DEST/${NEWNAME}.${EXT}"

        echo "✓ Copied thumbnail"
        echo "  $(basename "$FOUND")"
        echo "  -> ${NEWNAME}.${EXT}"

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