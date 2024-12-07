# pull official base image
FROM python:3.12.4-slim

# set work directory
WORKDIR /usr/src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip

#need to install these for dependencies
RUN apt-get update && apt-get -y install libpq-dev gcc

# install system dependencies
RUN apt-get update && apt-get install -y netcat-traditional

RUN apt-get -y install gdal-bin libgdal-dev
RUN apt-get -y install python3-gdal

RUN apt-get -y install binutils libproj-dev

COPY ./requirements.txt .
RUN pip install -r requirements.txt

#copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' ./entrypoint.sh


# copy project
COPY . .


RUN chmod +x /usr/src/entrypoint.sh

ENTRYPOINT ["/usr/src/entrypoint.sh"]
