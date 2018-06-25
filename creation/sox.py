#!/usr/bin/python env

from os   import system, path, listdir, chdir, mkdir
from sys  import argv
from time import sleep
import subprocess
from subprocess import Popen, PIPE
  

def execute(cli):
    for each in cli:
        print each
        system(each)
        sleep(0.2)
    return    

def checkVolume(filename):
    #print "checking volume"
    cl = [None]*3
    cl[0] = 'sox '+ filename +' '+filename[:-4]+'s.wav '+'gain -n'
    cl[1] = 'rm -rf '+filename
    cl[2] = 'mv '+filename[:-4]+'s.wav '+filename
    return cl

def CommandsForOGV(filename):
    cli = [None]*6
    cli[0] = 'ffmpeg -y -i ' + filename + ' -qscale 0 -an ' + 'noise.wmv'
    cli[1] = 'ffmpeg -y -i ' + filename + ' -qscale 0 ' + 'nn.wav'
    cli[2] = 'sox nn.wav -t null /dev/null trim 0 0.5 noiseprof myprofile'
    if len(argv)>3:
        cli[3] = 'sox nn.wav nnf.wav noisered myprofile ' + argv[3]
    else:
        cli[3] = 'sox nn.wav nnf.wav noisered myprofile 0.1'
    cli[4] = 'ffmpeg -y -i nnf.wav -i noise.wmv -qscale 0 combined.wmv'
    if not path.isfile(argv[1]):
        cli[5] = 'ffmpeg2theora combined.wmv -o ' + '../' + argv[2] + '/' + filename
    else:
        cli[5] = 'ffmpeg2theora combined.wmv -o ' + argv[2]
    return cli

def CommandsForWAV(filename):
    #print "commands for wav"
    cli = [None]*4
    cli[0] = 'sox '+filename+ ' -t null /dev/null trim 0 0.5 noiseprof myprofile'
    cli[1] = 'sox '+filename+ ' '+filename[0:-4]+'-nonoise.wav noisered myprofile 0.4'
    cli[2] = 'ffmpeg -y -i '+filename[0:-4]+'-nonoise.wav'+' '+filename[0:-4]+'-nonoise.ogg'
    cli[3] = 'rm myprofile '+filename[0:-4]+'-nonoise.wav '+filename
    return cli

def ConvertToWAV(filename):
    #print "converting to wav"
    cli = [None]*1
    cli[0] = 'ffmpeg -y -i '+filename+' '+filename[:-3]+'wav'
    return cli

if __name__ == '__main__':

    s = argv[1]
    if s[-3:]=="ogv":
        execute(CommandsForOGV(argv[1]))
    else:
        if s[-3:]=="wav":
            execute(CommandsForWAV(s))
        else:
            execute(ConvertToWAV(s))
            filen=s[:-3]+'wav'
            execute(checkVolume(filen))
            cli = CommandsForWAV(filen)
            execute(cli)

            
