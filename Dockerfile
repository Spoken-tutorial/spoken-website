FROM python:2.7.12
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD requirements-dev.txt /code/
RUN pip install -r requirements-dev.txt
RUN apt-get install libmysqlclient-dev
ADD . /code/