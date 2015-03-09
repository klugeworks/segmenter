FROM ubuntu

MAINTAINER noone

RUN ["apt-get", "update", "-y"]
RUN ["apt-get", "install", "-y", "python-virtualenv", "lame", "sox", "libsox-fmt-mp3", "curl"]
WORKDIR /segmenter/
RUN ["virtualenv", "env"]
ADD requirements.txt /segmenter/
RUN ["/segmenter/env/bin/pip", "install", "-r", "/segmenter/requirements.txt"]
ADD  . /segmenter/
CMD /segmenter/env/bin/python /segmenter/segmenter2.py
