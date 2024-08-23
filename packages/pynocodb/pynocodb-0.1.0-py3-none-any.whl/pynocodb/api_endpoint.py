from __future__ import annotations

from functools import wraps
import typing as t

from pynocodb.api_resource import ApiResource, AsyncApiResource


class ApiEndpoint:
    def __init__(self, api_resouce: ApiResource | AsyncApiResource, endpoint_url: str) -> None:
        endpoint_url = endpoint_url.strip().rstrip("/")
        if not endpoint_url.startswith("/"):
            endpoint_url = "/" + endpoint_url
        self._endpoint_url = endpoint_url
        self._api_resouce = api_resouce

    def format_url(self, *urls: str) -> str:
        res = self._endpoint_url
        for url in urls:
            res += "/" + url.strip(" /")
        return res

    @property
    def is_async(self):
        return self._api_resouce._is_async


def all_pages(*args, per_page: int = 100):
    """
    repeat call a request with limit to get all rows
    or simply set limit=-1
    """
    def inner(func):
        @wraps(func)
        def wrapper(*arge, **kwds):
            limit = kwds.get("limit")
            if not (isinstance(limit, int) and limit > 0):
                kwds["limit"] = per_page
            res = {
                "list": [],
                "pageInfo": {
                    "totalRows": 0,
                    "page": 1,
                    "pageSize": 0,
                    "isFirstPage": True,
                    "isLastPage": True,
                }
            }

            while True:
                r = func(*arge, **kwds)
                if "error" in r:
                    return r
                elif "list" in r and "pageInfo" in r:
                    res["list"].extend(r["list"])
                    res["pageInfo"].update({
                        "totalRows": r["pageInfo"]["totalRows"],
                        "pageSize": r["pageInfo"]["totalRows"],
                    })
                    if r["pageInfo"]["isLastPage"]:
                        break
                    kwds["offset"] = kwds.get("offset", 0) + kwds["limit"]
            return res
        return wrapper

    if len(args) == 1 and callable(args[0]):
        return inner(args[0])
    else:
        return inner
