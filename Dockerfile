FROM dock0/arch
MAINTAINER emunozh <emunozh@gmail.com>
RUN pacman -S --needed --noconfirm base

ADD ./webapp/requirements.txt /tmp/requirements.txt
RUN pacman -Syu --noconfirm
RUN pacman -S --needed --noconfirm python python-setuptools
RUN pacman -S --needed --noconfirm python python-pip
RUN pacman -S --needed --noconfirm gcc
RUN pacman -S --needed --noconfirm tk
RUN pacman -S --needed --noconfirm gcc-fortran
RUN pip install --no-cache-dir -r requirements.txt

# Add our code
ADD ./webapp /opt/webapp/
WORKDIR /opt/webapp

CMD gunicorn --bind 0.0.0.0:$PORT wsgi
