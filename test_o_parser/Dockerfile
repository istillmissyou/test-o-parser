FROM python:3.10

WORKDIR /app

COPY requirements.txt .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update 

RUN apt -y install default-libmysqlclient-dev gcc

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

RUN python manage.py collectstatic --no-input

CMD ["gunicorn", "test_o_parser.wsgi:application", "--bind", "0.0.0.0:8000" ]
