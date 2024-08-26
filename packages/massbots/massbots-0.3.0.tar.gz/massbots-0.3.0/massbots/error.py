import json
from json import JSONDecodeError

from massbots.openapi import ApiException, ApiError


def error_wrap(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, ApiException):
                raise Error(e)
            raise e

    return wrapper


class Error(Exception):
    def __init__(self, e: ApiException):
        if e.data and isinstance(e.data, ApiError):
            self.error = e.data.error
        else:
            try:
                self.error = json.loads(e.body).get("error")
            except JSONDecodeError:
                self.error = None

        self._e = e

    def __str__(self):
        s = f"{self._e.reason} ({self._e.status})"
        if self.error:
            s += f": {self.error}"
        return s
