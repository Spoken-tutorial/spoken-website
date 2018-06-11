#!/usr/bin/env python
'''
This script is suppose to delete all obselete cdimages 
zip files inside the 'media/cdimages/' folder older 
than 2 days.
'''
import os
import config

from datetime import datetime, timedelta

dir_path = '{}cdimage/'.format(config.MEDIA_ROOT)


for filename in os.listdir(dir_path):
    file_path = '{}{}'.format(dir_path, filename)
    if filename != 'README' and os.path.isfile(file_path):
        fcreated_time = datetime.fromtimestamp(os.path.getctime(file_path))
        if fcreated_time + timedelta(days=2) < datetime.now():
            print 'file {} is old, going to delete...'.format(filename)
            os.remove(file_path)
