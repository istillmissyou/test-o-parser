""" Модуль для отправки сообщений через тг бот. """

import logging
import random
import textwrap
import time

import requests
from telethon.utils import sanitize_parse_mode
from test_o_parser.settings import REPORT_BOT_TOKEN, REPORT_CHAT_ID


def tg_report(message: str, parse_mode: str = None):
    """ Отправка сообщения в Telegram чат.

    :param parse_mode: режим парсинга сообщений
    :param message: текст сообщения.
    """
    logger = logging.getLogger('app.telegram')

    try:
        if parse_mode:
            add_params = {'parse_mode': parse_mode}
            raw_message, _ = sanitize_parse_mode(parse_mode).parse(message)
            logger.warning(raw_message)
        else:
            add_params = {}
            logger.warning(message)

        text_chunks = textwrap.wrap(f'Parser Ozon сообщает: {message}\n', width=4000, replace_whitespace=False)
        if len(text_chunks) > 4:
            text_chunks = text_chunks[:2] + ['...'] + text_chunks[-2:]

        for text in text_chunks:
            params = {'chat_id': REPORT_CHAT_ID, 'text': text}
            params.update(add_params)
            resp = requests.get(
                url=f"https://api.telegram.org/bot{REPORT_BOT_TOKEN}/sendmessage",
                params=params
            )
            if resp.json()['ok']:
                logger.info('Notification successfully send')
            else:
                logger.warning(f'tg_report not ok: {resp.json()}')
            time.sleep(random.uniform(1, 2))
    except Exception as e:
        logger.exception(e)
