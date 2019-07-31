FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD requirements-dev.txt /code/
ADD requirements-py3.txt /code/
ADD requirements-common.txt /code/
RUN apt-get update && apt-get install -y default-libmysqlclient-dev
RUN pip3 install -r requirements-dev.txt
RUN pip3 install -r requirements-py3.txt
ADD . /code/
RUN cp sample.config.py spoken/config.py
RUN touch events/display.py