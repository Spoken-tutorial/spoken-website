# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py modify_media_ovma"

from __future__ import absolute_import, print_function, unicode_literals
import os
import datetime

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
            if not os.path.isfile(DESIRED_FILE[:-8].replace("\(", "(").replace("\)", ")") + "-Video.webm") or not os.path.isfile(DESIRED_FILE.replace("\(", "(").replace("\)", ")") + ".ogg"):
                # Save audio and video seperately for English Version
                bashCommand = bashCommand + ";\n" + settings.FFMPEG_VP8_PATH + " -y -i " \
                + fileToConvert + " -vcodec libvpx -af 'volume=0.0' -max_muxing_queue_size 1024 -f webm " \
                + DESIRED_FILE[:-8] + "-Video.webm\n" + settings.FFMPEG_VP8_PATH + " -y -i " + fileToConvert + \
                " -vn -acodec libvorbis " + DESIRED_FILE + ".ogg"
        else:
            if not os.path.isfile(DESIRED_FILE.replace("\(", "(").replace("\)", ")") + ".ogg"):
                # Save audio for Non-English Version
                bashCommand = bashCommand + ";\n" + settings.FFMPEG_VP8_PATH + " -y -i " \
                + fileToConvert + " -vn -acodec libvorbis " + DESIRED_FILE + ".ogg"
        os.system(bashCommand)

    def createLogFiles(self, log_file_path, original, converted):
        '''
        Creates log files for the script.
        Arguements:
            log_file_path: path to the log file in which content needs to be saved
            original: original file format
            converted: converted file format
        '''
        current_time = datetime.datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
        os.system('echo "________________LOG: ' + current_time + '________________" 2>&1 | tee -a ' + log_file_path)
        # Statistics
        os.system("echo -n 'Number of " + original + " files: ' \
        2>&1 | tee -a '" + log_file_path + "'; \
        find $src -name '*" + original + "' | wc -l 2>&1 | tee -a \
        '" + log_file_path + "';")
        os.system("echo -n 'Number of " + converted + " files: ' \
        2>&1 | tee -a '" + log_file_path + "'; \
        find $src -name '*" + converted + "' | wc -l 2>&1 | tee -a \
        '" + log_file_path + "';")

        # Difference b/w original and converted files
        original_files = os.popen("find $src -name *" + original).read().replace(original, '').split()
        converted_files = os.popen("find $src -name *" + converted).read().replace(converted, '').split()
        original_files_set = set(original_files)
        error_files = [converted_file for converted_file in converted_files if converted_file not in original_files_set]
        os.system("echo 'Good place to start looking if errors exist :" + str(error_files) + "' \
        2>&1 | tee -a " + log_file_path)
        os.system('echo "________________END: ' + current_time + '________________" 2>&1 | tee -a ' + log_file_path)

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
                                videoObject = videoObject.replace("(", "\(").replace(")", "\)")
                                self.MakeModedFiles(object, innerObject, videoObject)
                        os.chdir("..")
                os.chdir("..")
        # Create Log files
        self.createLogFiles(os.path.dirname(os.path.realpath(__file__)) + '/logs/modify_media_ovma.log', '.ogg', '.mp4')
        print ("Completed!")
