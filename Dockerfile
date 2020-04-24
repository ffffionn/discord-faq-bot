FROM python:3

ADD . /app/

RUN pip install -r /app/requirements.txt

CMD [ "python", "/app/main.py" ]