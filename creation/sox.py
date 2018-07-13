#!/usr/bin/python env
# Standard Library
from os import system
from os import mkdir
from os import path
from os import listdir
from os import chdir
from sys import argv
from time import sleep
import subprocess
from subprocess import Popen, PIPE

try:
    # Third Party Stuff
    from django.conf import settings
    FFMPEG_VP8_PATH = settings.FFMPEG_VP8_PATH
except:
    # To be imported only when script called from 
    # outside of the django application.
    # This is recommended only in development environments.
    print "\nWARNING: HARD CODED PATH FOR FFmpeg, Please improve this code.\n"
    FFMPEG_VP8_PATH = "/usr/bin/ffmpeg"


def executeCommands(cli):
    for each in cli:
        print each
        system(each)
        sleep(0.2)
    return


def checkVolume(filename):
    #print "checking volume"
    cl = [None] * 3
    cl[0] = 'sox ' + filename + ' ' + filename[:-4] + 's.wav ' + 'gain -n'
    cl[1] = 'rm -rf ' + filename
    cl[2] = 'mv ' + filename[:-4] + 's.wav ' + filename
    return cl


# def CommandsForOGV(filename):
#     cli = [None]*6
#     cli[0] = 'ffmpeg -y -i ' + filename + ' -qscale 0 -an ' + 'noise.wmv'
#     cli[1] = 'ffmpeg -y -i ' + filename + ' -qscale 0 ' + 'nn.wav'
#     cli[2] = 'sox nn.wav -t null /dev/null trim 0 0.5 noiseprof myprofile'
#     if len(argv)>3:
#         cli[3] = 'sox nn.wav nnf.wav noisered myprofile ' + argv[3]
#     else:
#         cli[3] = 'sox nn.wav nnf.wav noisered myprofile 0.1'
#     cli[4] = 'ffmpeg -y -i nnf.wav -i noise.wmv -qscale 0 combined.wmv'
#     if not path.isfile(argv[1]):
#         cli[5] = 'ffmpeg2theora combined.wmv -o ' + '../' + argv[2] + '/' + filename
#     else:
#         cli[5] = 'ffmpeg2theora combined.wmv -o ' + argv[2]
#     return cli


def CommandsForWAV(filename):
    #print "commands for wav"
    cli = [None] * 4
    cli[0] = 'sox ' + filename + ' -t null /dev/null trim 0 0.5 noiseprof myprofile'
    cli[1] = 'sox ' + filename + ' ' + filename[0:-4] + '-nonoise.wav noisered myprofile 0.4'
    cli[2] = FFMPEG_VP8_PATH + ' -y -i ' + filename[0:-4] + '-nonoise.wav' + ' ' + filename[0:-4] + '-nonoise.ogg'
    cli[3] = 'rm myprofile ' + filename[0:-4] + '-nonoise.wav ' + filename
    return cli


def ConvertToWAV(filename):
    #print "converting to wav"
    cli = [None] * 1
    cli[0] = FFMPEG_VP8_PATH + ' -y -i ' + filename + ' ' + filename[:-3] + 'wav'
    return cli


def soxAudioManipulation(s):
    if s[-3:] == "wav":
        executeCommands(CommandsForWAV(s))
    else:
        executeCommands(ConvertToWAV(s))
        filen = s[:-3] + 'wav'
        executeCommands(checkVolume(filen))
        cli = CommandsForWAV(filen)
        executeCommands(cli)

if __name__ == '__main__':
    s = argv[1]
    soxAudioManipulation(s)
