
# Use an official Python runtime as a parent image
FROM python:3.7.5-stretch

# Set the working directory to usr/src/app
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

#RUN apk update
#RUN apk --no-cache --update-cache add gcc gfortran py-pip build-base wget freetype-dev libpng-dev openblas-dev libc6-compat
#RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
#RUN pip3 install --no-cache-dir numpy scipy pandas matplotlib

RUN apt-get update -y && apt-get install -y \
    wget \
    ca-certificates \
	gcc \
	g++ \
	patch \
	gfortran \
	subversion \
	build-essential \
	--no-install-recommends \
	&& rm -rf /var/lib/apt/lists/*

###### "First apt-get install finished"
RUN apt-get update -y && apt-get install -y git-core curl zlib1g-dev libssl-dev libreadline-dev libyaml-dev libsqlite3-dev sqlite3 libxml2-dev libxslt1-dev libcurl4-openssl-dev software-properties-common libffi-dev

#RUN apt-get update -y && apt-get install -y \
#    python3-yaml
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade OpenDSSDirect.py[extras]

# Set the working directory to usr/src/app
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip3 install -r requirements.txt
RUN pip3 install -U redis
# Copy the current directory contents into the container usr/src/app
COPY main.py /usr/src/app/

COPY swagger_server /usr/src/app/swagger_server
COPY tests /usr/src/app/tests
COPY simulator /usr/src/app/simulator
COPY data_management /usr/src/app/data_management
COPY profess /usr/src/app/profess
COPY profiles /usr/src/app/profiles
COPY gesscon /usr/src/app/gesscon
#COPY "C:/Program Files/OpenVPN/config/s4g-ca.cert" /usr/src/app/openvpn/s4g-ca.cert











