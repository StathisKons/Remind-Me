import logging
import os
import datetime as dt
import requests
import json

from remind import constants
from discord.ext import commands

from pathlib import Path

logger = logging.getLogger(__name__)
URL_BASE = 'https://clist.by/api/v2/contest'
_CLIST_API_TIME_DIFFERENCE = 30 * 60  # seconds


class ClistApiError(commands.CommandError):
    """Base class for all API related errors."""

    def __init__(self, message=None):
        super().__init__(message or 'Clist API error')


class ClientError(ClistApiError):
    """An error caused by a request to the API failing."""

    def __init__(self):
        super().__init__('Error connecting to Clist API')


def _query_api():
    clist_username = os.getenv('CLIST_API_USERNAME')
    clist_api_key = os.getenv('CLIST_API_KEY')
    if not clist_username or not clist_api_key:
        raise ClistApiError('Clist API credentials missing')
    contests_start_time = dt.datetime.utcnow() - dt.timedelta(days=2)
    contests_start_time_string = contests_start_time.strftime("%Y-%m-%dT%H:%M:%S")

    param = {
        "order_by": "start",
        "limit": "500",
        "start__gte": contests_start_time_string,
        "username": clist_username,
        "api_key": clist_api_key
    }

    try:
        resp = requests.get(URL_BASE, params=param, timeout=(5, 20))
        if resp.status_code != 200:
            raise ClistApiError
        return resp.json()['objects']
    except Exception as e:
        logger.error(f'Request to Clist API encountered error: {e!r}')
        raise ClientError from e


def cache(forced=False):
    current_time_stamp = dt.datetime.utcnow().timestamp()
    db_file = Path(constants.CONTESTS_DB_FILE_PATH)

    db = None
    try:
        with db_file.open() as f:
            db = json.load(f)
    except (OSError, ValueError, KeyError, TypeError):
        pass

    last_time_stamp = db.get('querytime', 0) if isinstance(db, dict) else 0

    if not forced and current_time_stamp - last_time_stamp < _CLIST_API_TIME_DIFFERENCE:
        return

    try:
        contests = _query_api()
    except ClistApiError:
        # Let the bot start and retry later if the first API fetch fails.
        if db is None:
            with db_file.open('w') as f:
                json.dump({'querytime': 0, 'objects': []}, f)
        return

    db = {'querytime': current_time_stamp, 'objects': contests}
    with open(db_file, 'w') as f:
        json.dump(db, f)
