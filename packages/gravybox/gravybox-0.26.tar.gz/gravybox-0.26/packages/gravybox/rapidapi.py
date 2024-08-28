import os

import requests

from gravybox.betterstack import collect_logger
from gravybox.exceptions import BadStatusCode

logger = collect_logger()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_TIMEOUT = 120


def query_rapidapi(url, host, query, extra_headers=None):
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": host
    }
    if extra_headers is not None:
        headers |= extra_headers
    response = requests.get(url, headers=headers, params=query, timeout=RAPIDAPI_TIMEOUT)
    if response.status_code == 200:
        return response.json()
    else:
        raise BadStatusCode(response)
