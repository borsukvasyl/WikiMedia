# WikiAnalyzer

## Data flow
![](docs/data_flow.png)

## Technologies
![](docs/technologies.png)

### Run backend
```shell
# run
docker-compose up --build -d
# stop
docker-compose down
```
### Run client
```shell
PYTHONPATH="." python wiki_media/consumer.py fastapi
```
