# How to start server


## How to use this starter

Clone the repository:

Run docker:
```
docker-compose -f docker-compose-local.yaml up -d
```

Create a virtual environment with python:
```
python3 -m venv .venv
```

Activate the virtual environment:
```
source .venv/bin/activate
```

Install the requirements:
```
pip install -r requirements.txt
```
create database "test" and tables with command:
```
python3 create-tables.py
```

Start the local server:
```
fastapi dev main.py
```
on server
```
fastapi run main.py
```
