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
			if(i.endswith(".ogv") or i.endswith(".OGV")):
				i =i.replace(" ", "-")
				j=i[:-4]
				#.ogv to .mp3
				command="ffmpeg -y -i "+path+"/"+i+" "+path+"/"+j+".mp3"
				subprocess.call(command,shell=True)
				# remove .ogv
				cmd="rm "+path+"/"+i
				subprocess.call(cmd,shell=True)
access(path)
