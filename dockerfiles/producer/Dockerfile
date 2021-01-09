FROM python:3.6

WORKDIR /opt/workspace/producer
COPY wiki_media/producer .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]