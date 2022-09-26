
FROM python:3.9-alpine

WORKDIR /labs-tools-commons-recon-service

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD . /labs-tools-commons-recon-service

EXPOSE 5000

CMD [ "python3", "app.py" ]
