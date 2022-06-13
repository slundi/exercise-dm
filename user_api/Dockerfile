# https://fastapi.tiangolo.com/deployment/docker/
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

EXPOSE 8080

#sleep 20s to wait for Postgres DB to start
CMD sleep 20 && uvicorn main:app --host 0.0.0.0 --port 8080 --proxy-headers
