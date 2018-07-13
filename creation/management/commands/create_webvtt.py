# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py create_webvtt"

from __future__ import absolute_import, print_function, unicode_literals
import os
import io
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

    def MakeModedFiles(self, object, innerObject, scriptObject):
        '''
        PATH: Input folder path
        DESIRED_PATH: Output folder path
        Arguments:
            object: Course Code
            innerObject: script Code
            scriptObject: script Object to Convert
        This function makes VTT from SRT Files.
        '''
        # Input File
        FILE = PATH + object + "/" + \
            innerObject + "/" + scriptObject

        # Make required Directories
        if not os.path.isfile(FILE[:-4] + ".vtt"):
            bashCommand = "mkdir -p " + DESIRED_PATH + object + "/" + innerObject + "/"
            os.system(bashCommand)

            # Make the file
            output = "WEBVTT\n\n"
            with io.open(FILE, encoding='utf8') as fout:
                line = fout.readline()

                while line:
                    if "-->" in line:
                        output = output + line[:8] + ".000 --> "
                        output = output + line[13:21]
                        output = output + ".000" + "\n"
                    else:
                        output = output + line
                    line = fout.readline()

            with io.open(FILE[:-4] + ".vtt", "a", encoding='utf8') as fout:
                objectList = output.split("\n")
                for object in objectList:
                    fout.write(object)
                    fout.write('\n')

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
        SRT to WEBVTT
        ---
        Usage: 
        Requires input folder path in PATH variable
        Requires output folder path in DESIRED_PATH variable
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
                        scriptList = os.listdir('.')
                        for scriptObject in scriptList:
                            if scriptObject.endswith(".srt"):
                                self.MakeModedFiles(object, innerObject, scriptObject)
                        os.chdir("..")
                os.chdir("..")
        # Create Log files
        self.createLogFiles(os.path.dirname(os.path.realpath(__file__)) + '/logs/create_webvtt.log', '.srt', '.vtt')
        print ("Completed!")
