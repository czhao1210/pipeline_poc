FROM python:3.7

MAINTAINER yu <yux.xu@intel.com>

ENV http_proxy=http://child-prc.intel.com:913 \
    https_proxy=http://child-prc.intel.com:913 \
    PYTHONUNBUFFERED=true

COPY requirements/requirements_st_py37.txt requirements.txt

RUN mkdir -p ~/.pip
ADD dockerfiles/pip.conf ~/.pip

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN mv ./src/dtaf_core /usr/local/lib/python3.7/site-packages/

ENV http_proxy= \                                                                                                                
    https_proxy=                                                                                                                 




