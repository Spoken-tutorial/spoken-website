#!/bin/bash

set -e

echo "================================="
echo "Starting HST → Spoken migration"
echo "================================="

# HST_ROOT="./test_hst/Media/Content/Tutorial"

HST_ROOT="./Media/Content/Tutorial"

SPOKEN_MEDIA="./media/videos"


if [ -f "venv/bin/activate" ]; then
source venv/bin/activate
fi

PYTHON_BIN=$(which python3)

mkdir -p "$SPOKEN_MEDIA"

copy_file () {

SRC="$1"
DST="$2"

if [ -f "$SRC" ]; then

mkdir -p "$(dirname "$DST")"

cp "$SRC" "$DST"

echo "✓ $(basename "$SRC")"

fi

}

echo "Generating tutorial mapping..."

"$PYTHON_BIN" manage.py shell <<'EOF' > /tmp/hst_mapping.txt

from creation.models import TutorialDetail

for obj in TutorialDetail.objects.all():

    print(
        f"{obj.id}\t{obj.id}\t{obj.foss_id}"
    )

EOF


while IFS=$'\t' read -r tutorial_id tutorial_detail_id foss_id
do

echo ""
echo "Tutorial: $tutorial_id"

SRC="$HST_ROOT/$tutorial_id"

DEST="$SPOKEN_MEDIA/$foss_id/$tutorial_detail_id"

mkdir -p "$DEST/resources"

if [ ! -d "$SRC" ]; then

echo "Skipping: $SRC not found"

continue

fi


find "$SRC" -type f | while read file
do

filename=$(basename "$file")

case "$file" in

*/Slide/*)

copy_file \
"$file" \
"$DEST/resources/$filename"

;;

*/Script/*)

copy_file \
"$file" \
"$DEST/$filename"

;;

*/TimeScript/*)

copy_file \
"$file" \
"$DEST/$filename"

;;

*/Video/*)

copy_file \
"$file" \
"$DEST/$filename"

;;

esac

done

done < /tmp/hst_mapping.txt


rm -f /tmp/hst_mapping.txt


echo ""
echo "================================="
echo "Migration completed"
echo "Output → media/videos"
echo "================================="

