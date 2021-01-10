FROM python:3.6

WORKDIR /opt/workspace/api
COPY . .
ENV PYTHONPATH="."
EXPOSE 8000

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "wiki_media/api.py"]
