#!/bin/bash

export  WORKSPACE='var/lib/jenkins/workspace/venv/bin'

if [ ! -d "venv" ]; then
        virtualenv venv
fi
. venv/bin/activate



pwd

python3 manage.py test --keepdb scriptmanager
