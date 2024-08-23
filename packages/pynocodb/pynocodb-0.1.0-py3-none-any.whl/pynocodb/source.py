from __future__ import annotations

import typing as t

from pynocodb.api_endpoint import ApiEndpoint, all_pages
from pynocodb.api_resource import ApiResource, AsyncApiResource


class SourceEndpoint(ApiEndpoint):
    def __init__(self, api_resouce: ApiResource | AsyncApiResource) -> None:
        super().__init__(api_resouce, endpoint_url="/api/v1/db/meta/projects")

    def get_sources(
        self,
        base_id: str,
    ) -> dict:
        url = self.format_url(f"{base_id}/bases")
        return self._api_resouce._request("get", url)
