#!/usr/local/bin/python3
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

request = Request('http://127.0.0.1')

# https://docs.python.org/3/library/urllib.error.html
try:
    with urlopen(request) as response:
        if response.status != 200:
            print(f'Healthcheck failed: Request returned the HTTP Status {response.status}')
            sys.exit(1)
except HTTPError as e:
    print(f'Healthcheck failed: HTTPError {e}')
    sys.exit(1)
except URLError as e:
    print(f'Healthcheck failed: URLError {e}')
    sys.exit(1)
