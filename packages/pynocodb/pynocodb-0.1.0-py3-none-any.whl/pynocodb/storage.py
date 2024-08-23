from __future__ import annotations

import typing as t

from pynocodb.api_endpoint import ApiEndpoint
from pynocodb.api_resource import ApiResource, AsyncApiResource


class StorageEndpoint(ApiEndpoint):
    def __init__(self, api_resouce: ApiResource | AsyncApiResource) -> None:
        super().__init__(api_resouce, endpoint_url="/api/v1/storage")

    def upload_attachment(
        self,
        files: list,
        path: str | None = None,
    ) -> dict:
        url = self.format_url(f"/upload")
        params = None
        if path:
            params = {"path": path}
        return self._api_resouce._request("post", url, params=params, files=files)
