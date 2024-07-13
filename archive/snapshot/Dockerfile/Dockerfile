FROM python

RUN apt-get update

ENV $s3_bucket

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "-u", "snapshot.py"]
