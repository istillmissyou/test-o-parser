# Test-o-parser
Django приложение с REST API для парсинга информации о товарах магазина по ссылке с сайта Ozon и сохранение полученных данных о товарах в базу данных. Также оповещение о завершении парсинга через Telegram бота. И Telegram бот для просмотра товаров последнего парсинга

## Стек технологий
Python 3.10.6, Django 3.2.20, Django REST Framework 3.14.0, MySQL, Docker, AdminLTE, Celery, Redis, Aiogram.

## Установка
Для запуска локально, создайте файл `.env` в главной директории и рядом с файлом "manage.py" с содержанием:
```
SECRET_KEY='django-insecure-wq46%pu)o8c7a3vny3#$*&@%hmvkd#$vm'
DB_NAME='test_o_parser'
DB_USER='mysql_user'
DB_PASSWORD='mysql_password'
DB_HOST='127.0.0.1'
DB_PORT='3306'
REDIS_HOST='localhost'
TG_REDIS_HOST='redis'
REDIS_PORT=6379
REDIS_PASSWORD='qwerty123'
REPORT_BOT_TOKEN=токен тг бота для отправок сообщений
REPORT_CHAT_ID=айди юзера тг (кому отправлять)
```

#### Установка Docker
Для запуска проекта вам потребуется установить Docker и docker-compose.

Установку на операционных системах вы можете прочитать в [документации](https://docs.docker.com/engine/install/) и [про установку docker-compose](https://docs.docker.com/compose/install/).

### Настройка проекта
1. Запустите docker compose:
```bash
docker compose up --build -d
```
2. Запустить django:
```bash
cd test_o_parser
. venv/bin/activate
python manage.py runserver
```
3. Запустить celery:
```bash
cd test_o_parser
. venv/bin/activate
celery -A test_o_parser worker -l INFO
```
4. Создать суперюзера:
```bash
python manage.py createsuperuser
```


## Документация к API
Чтобы открыть документацию локально, запустите сервер и перейдите по ссылке:
[http://127.0.0.1/swagger/](http://127.0.0.1/swagger/)
[http://127.0.0.1/redoc/](http://127.0.0.1/redoc/)

## Автор
Штунь Данил
