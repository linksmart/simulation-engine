
# Use an official Python runtime as a parent image
FROM garagon/opendss:0.2_python3.6.5

#RUN apt-get update -y && apt-get install -y \
#    python3-yaml

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












