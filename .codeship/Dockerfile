FROM indico/indicoapi-docker-cuda-8-0

RUN pip3 install --upgrade pip
RUN pip3 --version

RUN pip3 uninstall IndicoIo msgpack-numpy setuptools -y
RUN pip3 install setuptools --upgrade

RUN pip3 install IndicoIo==1.1.5 msgpack-numpy==0.4.1 tensorflow==1.6 html5lib==1.0b8 nose

RUN python3 -m spacy download en
ENV LANG C.UTF-8

ADD . /finetune
WORKDIR /finetune

RUN python3 setup.py develop --upgrade
