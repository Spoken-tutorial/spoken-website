#!/usr/bin/python env

from os   import system, path, listdir, chdir, mkdir
from sys  import argv
from time import sleep
import subprocess
from subprocess import Popen, PIPE
  

def execute(cli):     
    for each in cli:
        system(each)
        sleep(0.2)
    return    

def checkVolume(filename):
    song = AudioSegment.from_wav(filename)
    print song
    return True

def CommandsForOGV(filename):
     cli = [None]*6
     cli[0] = 'ffmpeg -y -i ' + filename + ' -qscale 0 -an ' + 'noise.wmv'
     cli[1] = 'ffmpeg -y -i ' + filename + ' -qscale 0 ' + 'nn.wav'
     cli[2] = 'sox nn.wav -t null /dev/null trim 0 0.5 noiseprof myprofile'
     if len(argv)>3:
         cli[3] = 'sox nn.wav nnf.wav noisered myprofile ' + argv[3]
     else:
         cli[3] = 'sox nn.wav nnf.wav noisered myprofile 0.26'
     cli[4] = 'ffmpeg -y -i nnf.wav -i noise.wmv -qscale 0 combined.wmv'
     if not path.isfile(argv[1]):
         cli[5] = 'ffmpeg2theora combined.wmv -o ' + '../' + argv[2] + '/' + filename
     else:
         cli[5] = 'ffmpeg2theora combined.wmv -o ' + argv[2]
     return cli

def CommandsForWAV(filename):
    cli = [None]*4
    cli[0] = 'sox '+filename+ ' -t null /dev/null trim 0 0.5 noiseprof myprofile'
    cli[1] = 'sox '+filename+ ' '+filename[0:-4]+'-nonoise.wav noisered myprofile 0.3'
    cli[2] = 'ffmpeg -y -i '+filename[0:-4]+'-nonoise.wav'+' '+filename[0:-4]+'-nonoise.ogg'
    cli[3] = 'rm myprofile '+filename[0:-4]+'-nonoise.wav '+filename
    return cli

def ConvertToWAV(filename):
    cli = [None]*1
    cli[0] = 'ffmpeg -i '+filename+' '+filename[:-3]+'wav'
    return cli

if __name__ == '__main__':

    s = argv[1]
    if s[-3:]=="ogv":
        execute(CommandsForOGV(argv[1]))
    else:
        if s[-3:]=="wav":
            p = subprocess.Popen(["python", "logmmse.py", "ele.wav","abc.wav"], stdout=subprocess.PIPE)  
            p.communicate()
        else:
            print s[-3:]
            execute(ConvertToWAV(argv[1]))
            filen=argv[1][:-3]+'wav'
            print filen
            execute(CommandsForWAV(filen))

            
