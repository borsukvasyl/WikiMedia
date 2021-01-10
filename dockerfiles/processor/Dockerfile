FROM python:3.6

WORKDIR /opt/workspace/processor
COPY . .
ENV PYTHONPATH="."

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "wiki_media/processor.py", "worker", "-l", "info"]
