from __future__ import annotations

import typing as t

from pynocodb.api_endpoint import ApiEndpoint
from pynocodb.api_resource import ApiResource, AsyncApiResource


class PublicEndpoint(ApiEndpoint):
    def __init__(self, api_resouce: ApiResource | AsyncApiResource) -> None:
        super().__init__(api_resouce, endpoint_url="/api/v2/public/shared-view")

    def read_shared_view_list(
        self,
        shared_view_id: str,
        where: str | None = None,
    ) -> dict:
        url = self.format_url(f"{shared_view_id}/bulk/dataList")
        params = None
        if where:
            params = {"where": where}
        return self._api_resouce._request("post", url, params=params)

    def read_shared_view_group(
        self,
        shared_view_id: str,
        where: str | None = None,
    ) -> dict:
        url = self.format_url(f"{shared_view_id}/bulk/group")
        params = None
        if where:
            params = {"where": where}
        return self._api_resouce._request("post", url, params=params)

    def read_shared_view_aggregate(
        self,
        shared_view_id: str,
        where: str | None = None,
        filter_json: str | None = None,
        aggregation: list | None = None,
    ) -> dict:
        url = self.format_url(f"{shared_view_id}/bulk/aggregate")
        params = None
        if where:
            params = {**(params or {}), "where": where}
        if filter_json:
            params = {**(params or {}), "filter_json": filter_json}
        if where:
            params = {**(params or {}), "aggregation": aggregation}
        return self._api_resouce._request("post", url, params=params)

    def download_shared_view_attachment(
        self,
        shared_view_id: str,
        column_id: str,
        row_id: str,
        url_or_path: str,
    ) -> dict:
        url = self.format_url(f"{shared_view_id}/downloadAttachment/{column_id}/{row_id}")
        params = None
        if url_or_path:
            params = {"url_or_path": url_or_path}
        return self._api_resouce._request("post", url, params=params)
