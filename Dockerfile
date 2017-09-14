FROM ubuntu:17.10

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y git python3 python3-pip

ADD requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

ENV PYTHONPATH "/pythonathon"
EXPOSE 5000

ADD . /pythonathon
WORKDIR /pythonathon

ADD ./questions.json /questions.json
RUN python3 init_db.py --questions=/questions.json

CMD python3 pythonathon.py