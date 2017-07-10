#!/usr/bin/python
import sys
import subprocess
from os import listdir
from os.path import isfile, join, isdir

path=sys.argv[1]

def access(path):
	files=listdir(path)
	for i in files:
		if(isdir(path+"/"+i)==True):
			access(path+"/"+i)
		else:
			if(i.endswith(".mov") or i.endswith(".MOV")):
				i =i.replace(" ", "-")
				j=i[:-4]
				if("English" in i):
					j=j[:-8]
				#mute the video
				cmd="ffmpeg -i "+path+"/"+i+" -c copy -an "+path+"/silent_"+i
				subprocess.call(cmd,shell=True)
				#conversion to .webm
				cmd="ffmpeg -i "+path+"/silent_"+i+" -vcodec libvpx -cpu-used -5 -deadline realtime "+path+"/"+j+".webm"
				subprocess.call(cmd,shell=True)
				#remove .mov	
				cmd="rm "+path+"/silent_"+i+" "+path+"/"+i
				subprocess.call(cmd,shell=True)
access(path)
