# pull official base image
#FROM harbor.diia.digital/docker-cache/library/python:3.6
FROM python:3.8


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# install dependencies
RUN apt-get update
# pdf converter deps
##RUN apt-get install -y libreoffice inkscape ffmpeg xvfb python3-pip  python3-dev

RUN apt-get install -y  exiftool
# textract  deps
# RUN apt-get install -y python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils pstotext tesseract-ocr \
# flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig

WORKDIR /opt/apps/mrs



RUN mkdir -p /opt/apps/mrs
RUN mkdir -p /install

# copy project install
COPY ./requirements.txt /install/requirements.txt
# install python depends
RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install -r /install/requirements.txt

COPY ./modules /install/modules
# copy project
COPY ./apps /opt/apps/mrs/apps
COPY ./config /opt/apps/mrs/config
COPY ./manage.py /opt/apps/mrs/manage.py
COPY ./entrypoint.sh /opt/apps/mrs/entrypoint.sh
COPY ./entrypoint_admin.sh /opt/apps/mrs/entrypoint_admin.sh
COPY ./celery_run.sh /opt/apps/mrs/celery_run.sh 

RUN chmod +x /opt/apps/mrs/entrypoint.sh
RUN chmod +x /opt/apps/mrs/entrypoint_admin.sh
RUN chmod +x /opt/apps/mrs/celery_run.sh


