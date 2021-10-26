FROM debian:buster AS builder

WORKDIR /build

RUN apt-get update
RUN apt-get -y install git build-essential python-dev cmake libtbb-dev libboost-program-options-dev libboost-python-dev python-jinja2
RUN git clone --no-checkout https://github.com/PixarAnimationStudios/USD
RUN cd USD && git checkout v20.05

RUN cmake \
    -DCMAKE_INSTALL_PREFIX=/usr/local/USD \
    -DTBB_ROOT_DIR=/usr \
    -DBOOST_ROOT=/usr \
    -DPXR_ENABLE_GL_SUPPORT=FALSE \
    -DPXR_BUILD_IMAGING=FALSE \
    -DPXR_BUILD_USD_IMAGING=FALSE \
    -DPXR_BUILD_TESTS=FALSE \
    /build/USD
RUN cmake --build . --target install -- -j3

FROM debian:buster-slim
RUN apt-get update
RUN apt-get -y install python libpython2.7 python-pillow python-numpy libtbb2 libboost-python1.67.0

RUN apt-get -y install python3-pip

RUN pip3 install flask
RUN pip3 install boto3

RUN apt-get -y install nodejs npm
RUN apt-get -y install curl

RUN npm install -g n
RUN n latest

RUN npm install -g obj2gltf

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade Pillow
RUN pip3 install requests

COPY --from=builder /usr/local/USD /usr/local/USD

WORKDIR /usr/usdzconvert
COPY usdzconvert /usr/usdzconvert

USER 1001
ENV PYTHONPATH=/usr/local/USD/lib/python:$PYTHONPATH
ENV PATH=/usr/usdzconvert:$PATH

COPY main.py main.py

ENTRYPOINT [ "python3", "-u" ]

CMD [ "main.py" ]