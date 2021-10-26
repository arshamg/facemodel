FROM nickveld/frankmocap-env:pytorch3d

WORKDIR /build

RUN apt-get clean && apt-get update -y
RUN apt-get install -y wget git g++ python3-pip

RUN git clone https://github.com/YadiraF/DECA
RUN cd DECA && pip install -r requirements.txt

RUN pip uninstall -y numba
RUN pip install numba==0.54.0

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get install -y nginx python3-gevent python3-opencv
RUN pip install gunicorn gevent requests flask boto3


RUN mkdir -p /opt/ml
RUN mkdir /opt/ml/results
ENV PATH=/root/.local/bin:$PATH
ENV PATH="/opt/ml/code:/root/.local/bin:${PATH}"

COPY code/ /opt/ml/code/
COPY /code . 

RUN wget https://download-3d.s3.us-east-2.amazonaws.com/deca_model.tar -O /build/DECA/data/deca_model.tar

RUN wget https://download-3d.s3.us-east-2.amazonaws.com/generic_model.pkl -O /build/DECA/data/generic_model.pkl

RUN chmod +x /opt/ml/code/serve
