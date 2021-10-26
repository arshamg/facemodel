FROM nvidia/cuda:11.0-base
CMD nvidia-smi


# FROM python:3.8.0-slim AS build
# FROM nvidia/cuda:11.2.1-runtime-ubuntu20.04
FROM nvidia/cuda:10.2-base

WORKDIR /build

RUN apt-get clean && apt-get update -y
RUN apt-get install -y wget git g++

# COPY DECA/ DECA/

#############

# RUN apt-get clean && \
#     apt-get update -y && \
#     apt-get install -y python3-dev build-essential libssl-dev libffi-dev libjpeg-dev zlib1g-dev libjpeg62 && \
#     apt-get install -y wget git ca-certificates curl nginx 

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get install -y nginx
RUN apt-get install -y python3-pip


RUN pip3 install --user torch==1.7.1+cu101 torchvision==0.8.2+cu101 -f https://download.pytorch.org/whl/torch_stable.html


RUN apt-get install -y python3-gevent python3-opencv
RUN pip install gunicorn gevent

RUN pip install requests flask

RUN git clone https://github.com/YadiraF/DECA
RUN cd DECA && pip install -r requirements.txt
RUN pip install "git+https://github.com/facebookresearch/pytorch3d.git"

RUN pip uninstall -y numba
RUN pip install numba==0.54.0

RUN mkdir -p /opt/ml
RUN mkdir /opt/ml/results
# RUN mkdir -p /.cache/clip

# COPY requirements.txt .
ENV PATH=/root/.local/bin:$PATH

ENV PATH="/opt/ml/code:/root/.local/bin:${PATH}"

# COPY code/serve /opt/ml/code/serve
COPY code/ /opt/ml/code/
COPY /code . 

# COPY data/deca_model.tar /build/DECA/data/deca_model.tar
# COPY data/generic_model.pkl /build/DECA/data/generic_model.pkl

RUN wget https://download-3d.s3.us-east-2.amazonaws.com/deca_model.tar -O /build/DECA/data/deca_model.tar
# COPY /build/deca_model.tar /build/DECA/data/deca_model.tar

RUN wget https://download-3d.s3.us-east-2.amazonaws.com/generic_model.pkl -O /build/DECA/data/generic_model.pkl
# COPY ./generic_model.pkl /build/DECA/data/generic_model.pkl

RUN chmod +x /opt/ml/code/serve

# RUN pip3 install --user --upgrade pip
# RUN pip install --user cython
# # RUN pip3 install --user torch==1.7.1+cu101 torchvision==0.8.2+cu101 -f https://download.pytorch.org/whl/torch_stable.html
# RUN pip3 install --user torch==1.8 torchvision -f https://download.pytorch.org/whl/torch_stable.html
# RUN pip3 install --user -r requirements.txt

# RUN wget -O /.cache/clip/ViT-B-32.pt "https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt"


# FROM python:3.8.0-slim

# RUN apt-get clean && \
#     apt-get update -y && \
#     apt-get install -y libjpeg62 ca-certificates nginx python3-opencv

# RUN apt-get install libtinfo5


# RUN mkdir -p /opt/ml/code
# WORKDIR /opt/ml/code

# COPY --from=build /root/.local /root/.local
# COPY --from=build /build/ .
# COPY --from=build /opt/ml /opt/ml
# COPY --from=build /.cache/clip /root/.cache/clip

# SageMaker will automatically run the serve script so we need to make
# sure it has execution permissions.
# RUN chmod +x serve
# RUN chmod +x /opt/ml/code/serve
