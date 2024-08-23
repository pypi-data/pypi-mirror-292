from __future__ import annotations

from pynocodb.api_resource import ApiResource, AsyncApiResource
from pynocodb.auth import AuthEndpoint
from pynocodb.base import BaseEndpoint
from pynocodb.public import PublicEndpoint
from pynocodb.storage import StorageEndpoint
from pynocodb.source import SourceEndpoint
from pynocodb.table import TableEndpoint
from pynocodb.record import RecordEndpoint
from pynocodb.utils import UtilsEndpoint


class ClientMixin:
    def __init__(self) -> None:
        self.auth = AuthEndpoint(self.api_resource)
        self.base = BaseEndpoint(self.api_resource)
        self.public = PublicEndpoint(self.api_resource)
        self.storage = StorageEndpoint(self.api_resource)
        self.source = SourceEndpoint(self.api_resource)
        self.table = TableEndpoint(self.api_resource)
        self.record = RecordEndpoint(self.api_resource)
        self.utils = UtilsEndpoint(self.api_resource)

    def set_token(self, token: str):
        return self.api_resource.set_token(token)


class Client(ClientMixin):
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8080",
        token: str = "",
        proxy: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.api_resource = ApiResource(base_url=base_url, token=token, proxy=proxy, timeout=timeout)
        super().__init__()


class AsyncClient(ClientMixin):
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8080",
        token: str = "",
        proxy: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.api_resource = AsyncApiResource(base_url=base_url, token=token, proxy=proxy, timeout=timeout)
        super().__init__()
