FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app

RUN mkdir tmp
EXPOSE 8000
CMD [ "python","app/main.py" ]



