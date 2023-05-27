# asyncio_swapi-parser

1. В директории проекта создать файл .env и заполнить его по образцу:

```python
PG_USER:postgres
PG_PASSWORD:postgres
PG_DB:swapi_test
```
Подготовить окружение: 
```python
python3 -m venv env

source env/bin/activate
```
```python
pip install -r requirements.txt
```
2. Запустить контейнер с базой данных:
```python
docker-compose up -d
```
3. Запустить приложение выполнив последовательно:
```python
python main.py
```