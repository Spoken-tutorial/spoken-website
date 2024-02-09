#!/bin/bash

# https://github.com/srikantpatnaik/shell-scripts/blob/main/convert-spoken-ogv2webm.sh
# Modified from conversion script provided by Srikant Patnaik

#######################################################################

# License GNU GPLv3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

########################################################################

# A sample 'ffmpeg' command

# ffmpeg \
# -nostdin -v 16 -y \
# -i video.ogv \
# -ac 1 -b:v 100k -c:a libvorbis -c:v libvpx -crf 5 -q:a 1 -qmax 45 -qmin 5 -r 2 -threads 4 \
# video.webm

# 'qmin'   : the minimum quantization parameter (default 4)
# 'qmax'   : the maximum quantization parameter (default 63)
# 'b:v'    : the target bit rate setting
# 'crf'    : the overall quality setting. If not set, VBR (default 10)
# 'r'      : frame rate
# 'threads': For quad core its safe to use 4 threads

########################################################################

# MUST READ

# What this script for?
# This will find the 'ogv' videos in directories recursively and convert
# them into 'webm'.

# How it does?
# It uses 'find' command to list all ogv file paths and store it in a text
# file. It then reads each line from the text file and executes 'ffmpeg'
# command to convert the file into 'webm'. Simple.
#
# To resume you must run the file from the same location.

########################################################################

FFMPEG_GLOBAL_OPTIONS="
-nostdin
-v 16
-y
"

FFMPEG_OPTIONS="
-ac 1
-b:v 100k
-c:a libvorbis
-c:v libvpx
-crf 5
-q:a 1
-qmax 45
-qmin 5
-r 2
-threads 4
"

oninterrupt() {
    rm -f "$eachWebmFile"
    echo "[$successcount/$totalcount] converted"
    rm -f "$ogvfile"
    exit 1
}

# Force user to enter only one arguement, i.e path of the video directory
DIR="$1"
if test "$#" -ne 1 -o ! -d "$DIR"; then
    echo "Usage: $0 directory"
    echo 'Provide path of your media directory as argument to this script.'
    exit 0
fi

ogvfile="$DIR/source-ogvfile-paths.txt"

# Create text file with ogv file paths
find "$DIR" -iname \*.ogv | sort > "$ogvfile"

totalcount=$( wc -l < "$ogvfile" )
count=0
successcount=0
echo "[$totalcount] files to be converted"

# Handle Ctrl-C
trap oninterrupt INT QUIT TERM

# Iterate over each line of the file and convert it to webm. Place the file
# in the same directory
while read eachOgvFile; do
    let count++

    # First construct the new file name with webm extension using ogv path
    # Handling both OGV/ogv extensions
    eachWebmFile="$( echo "$eachOgvFile" | sed 's/\.ogv$/.webm/i' )"

    # Check whether the ogv file was already converted.
    # This is useful if we rerun the script. It shouldn't start from beginning.
    if test -f "$eachWebmFile" && file -b "$eachWebmFile" | grep -q WebM; then
        continue
    fi

    # Execute CPU hungry ffmpeg command only if the video was not dealt earlier
    echo "[$count/$totalcount] converting $eachOgvFile"
    ffmpeg $FFMPEG_GLOBAL_OPTIONS -i "$eachOgvFile" $FFMPEG_OPTIONS "$eachWebmFile" &&
        let ++successcount || rm -f "$eachWebmFile"

    eachWebmFile=
done < "$ogvfile"

echo "[$successcount/$totalcount] converted"
rm -f "$ogvfile"
exit 0
