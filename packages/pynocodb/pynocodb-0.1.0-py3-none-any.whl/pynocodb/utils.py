from __future__ import annotations

import typing as t

from pynocodb.api_endpoint import ApiEndpoint
from pynocodb.api_resource import ApiResource, AsyncApiResource


class UtilsEndpoint(ApiEndpoint):
    def __init__(self, api_resouce: ApiResource | AsyncApiResource) -> None:
        super().__init__(api_resouce, endpoint_url="/api/v2/meta/nocodb")

    def get_app_info(self) -> dict:
        url = self.format_url(f"/info")
        return self._api_resouce._request("get", url)
