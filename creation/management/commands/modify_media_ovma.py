# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py modify_media_ovma"

from __future__ import absolute_import, print_function, unicode_literals
import os

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.conf import settings

# Input Path - Use absolute Path & put `/` after the Path
# Example - "/home/atb00ker/videos/"
PATH = settings.MEDIA_ROOT + 'videos/'
# Output Path - Use absolute Path & put `/` after the Path
# Example - "/home/atb00ker/videos/"
DESIRED_PATH = settings.MEDIA_ROOT + 'videos/'

class Command(BaseCommand):


    def MakeModedFiles(self, object, innerObject, videoObject):
        '''
        Arguements:
            object: Course Code
            innerObject: Video Code
            VideoObject: Video Object to Convert
        This function makes the directories required and converts a file.
        '''
        
        fileToConvert = os.path.join(os.getcwd(), videoObject)
        # Input File
        FILE = PATH + object + "/" + \
            innerObject + "/" + videoObject[:-4]
        # Output File
        DESIRED_FILE = DESIRED_PATH + object + "/" + \
            innerObject + "/" + videoObject[:-4]

        # Make required Directories
        bashCommand = "mkdir -p " + DESIRED_PATH + object + "/" + innerObject + "/"
        # Make the file
        
        if videoObject[-11:] == "English.mp4":
            # Save audio and video seperately for English Version
            bashCommand = bashCommand + ";\nffmpeg -y -i " + fileToConvert + \
                " -vcodec libvpx -af 'volume=0.0' -max_muxing_queue_size 1024 -f webm " \
                + DESIRED_FILE[:-8] + "-Video.webm\nffmpeg -y -i " + fileToConvert + \
                " -vn -acodec libvorbis " + DESIRED_FILE + ".ogg"
        else:
            # Save audio for Non-English Version
            bashCommand = bashCommand + ";\nffmpeg -y -i " + fileToConvert + \
                " -vn -acodec libvorbis " + DESIRED_FILE + ".ogg"
        print (bashCommand)
        os.system(bashCommand)


    def handle(self, *args, **options):
        '''
        Batch MP4 to Silent videos & OGG converter
        > MP4 to WEBM -af
        > MP4 to OGG -vn
        '''
        os.chdir(PATH)
        list = os.listdir('.')
        for object in list:
            if object.isdigit():
                os.chdir(object)
                innerList = os.listdir('.')
                for innerObject in innerList:
                    if innerObject.isdigit():
                        os.chdir(innerObject)
                        videoList = os.listdir('.')
                        for videoObject in videoList:
                            if videoObject.endswith(".mp4"):
                                self.MakeModedFiles(object, innerObject, videoObject)
                        os.chdir("..")
                os.chdir("..")        
