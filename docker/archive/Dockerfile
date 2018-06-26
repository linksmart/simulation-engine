
# Use an official Python runtime as a parent image
FROM python:3.7-rc-alpine3.7

# Set the working directory to usr/src/app
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apk update
RUN apk --no-cache --update-cache add gcc gfortran py-pip build-base wget freetype-dev libpng-dev openblas-dev libc6-compat
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip3 install --no-cache-dir numpy scipy pandas matplotlib

# Copy the current directory contents into the container usr/src/app
#COPY requirements.txt /usr/src/app/


#RUN pip3 install -r requirements.txt
RUN pip3 install OpenDSSDirect.py[extras]






