#!/bin/bash

# -----------------------------------------------------------------------------
# Script to create 25-second sample clips from all `.webm` videos in a directory.
# 
# Usage:
#   ./script.sh /path/to/video-directory
#
# What it does:
#   - Accepts a single directory path as argument.
#   - Finds all `.webm` video files inside it (excluding those ending with -sample.webm).
#   - For each video, creates a 25-second sample clip from the start using ffmpeg.
#   - Sample clips are saved in the same directory with "-sample.webm" suffix.
#   - Skips videos that already have a valid sample.
#   - Tracks progress and shows [converted/total] status.
#   - Cleans up temporary file list on exit or interruption (Ctrl+C).
#
# Requirements:
#   - ffmpeg installed and available in PATH
# -----------------------------------------------------------------------------

FFMPEG_GLOBAL_OPTIONS="
-nostdin
-v 16
"

FFMPEG_OPTIONS="
-ss 00:00:00
-to 00:00:25
-c copy
"
oninterrupt(){
    rm -f "eachWebmFile"
    echo "[$successcount/$totalcount] converted"
    rm -f "$videosPathFile"
    exit 1
}

DIR="$1"

echo "Finding video files in : $DIR"

# Force user to enter only one arguement, i.e path of the video directory
if test "$#" -ne 1 -o ! -d "$DIR" ; then
    echo "Usage: $0 directory"
    echo 'Provide path of your media directory as argument to this script.'
    exit 0
fi


videosPathFile="${DIR}/videofile-paths.txt"
echo "videosPathFile : $videosPathFile"

# Create text file with original video paths
find "$DIR" -type f -iname "*.webm" ! -iname "*-sample.webm" | sort > "$videosPathFile"

totalcount=$( wc -l < "$videosPathFile")

count=0
successcount=0

echo "[$totalcount] files to be converted"

# Handle Ctrl-C
trap oninterrupt INT QUIT TERM

# Iterate over each line of the file and trim it to 25 seconds. Place the file
# in the same directory
while read originalVideoFile; do
    let count++

    # First construct the new file name with -sample suffix
    sampleVideoFile="$( echo "$originalVideoFile" | sed 's/\.webm$/-sample.webm/i')"

    # Check if the sample file already exists
    if test -f "$sampleVideoFile" && file -b "$sampleVideoFile" | grep -q "-sample.webm";then
        continue
    fi

    echo "[$count/$totalcount] converting $originalVideoFile"
    ffmpeg $FFMPEG_GLOBAL_OPTIONS -i "$originalVideoFile" $FFMPEG_OPTIONS "$sampleVideoFile" &&
        let ++successcount || rm -f "$sampleVideoFile"
    
    sampleVideoFile=
done < "$videosPathFile"

echo "[$successcount/$totalcount] converted"
rm -f "$videosPathFile"

exit 0
