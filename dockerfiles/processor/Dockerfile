FROM python:3.6

WORKDIR /opt/workspace/producer
COPY . .
ENV PYTHONPATH="."

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "wiki_media/processor.py", "worker", "-l", "info"]
