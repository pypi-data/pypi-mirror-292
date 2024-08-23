from __future__ import annotations

import typing as t

import httpx


class ApiResource:
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8080",
        token: str = "",
        proxy: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._is_async = False
        self._client = None
        self._base_url = base_url.strip().strip("/")
        self._token = token
        self._proxy = proxy
        self._timeout = timeout

    def _get_httpx_params(self) -> dict:
        res = {
            "base_url": self._base_url,
            "proxy": self._proxy,
            "timeout": self._timeout,
        }
        if self._token:
            res["headers"] = {"xc-auth": self._token, "xc-token": self._token}
        return res

    def set_token(self, token: str):
        self._token = token
        if self.client is not None:
            self._client = None

    @property
    def client(self) -> httpx.Client | httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            if self._is_async:
                self._client = httpx.AsyncClient(**self._get_httpx_params())
            else:
                self._client = httpx.Client(**self._get_httpx_params())
        return self._client
    
    def _request(
        self,
        method: t.Literal["get", "post", "patch", "delete"],
        url: str,
        *,
        data: t.Any = None,
        params: t.Any = None,
        json: t.Any = None,
        files: t.Any = None,
        exclude_none: bool = True,
    ) -> t.Any:
        if exclude_none:
            if isinstance(data, dict):
                data = {k:v for k,v in data.items() if v is not None}
            if isinstance(params, dict):
                params = {k:v for k,v in params.items() if v is not None}
            if isinstance(json, dict):
                json = {k:v for k,v in json.items() if v is not None}
        kwds = {
            "method": method.upper(),
            "url": url,
            "data": data,
            "params": params,
            "json": json,
            "files": files,
        }
        def sync_call():
            return self.client.request(**kwds).json()

        async def async_call():
            return (await self.client.request(**kwds)).json()

        if self._is_async:
            return async_call()
        else:
            return sync_call()


class AsyncApiResource(ApiResource):
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8080",
        token: str = "",
        proxy: str | None = None,
        timeout: float | None = None,
    ) -> None:
        super().__init__(
            base_url=base_url,
            token=token,
            proxy=proxy,
            timeout=timeout,
        )
        self._is_async = True
