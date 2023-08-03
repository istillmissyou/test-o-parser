from __future__ import absolute_import, unicode_literals

import os

from dotenv import load_dotenv

load_dotenv()

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_o_parser.settings')

app = Celery('test_o_parser', broker=f'redis://:{os.getenv("REDIS_PASSWORD")}@{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/0')

app.autodiscover_tasks()
