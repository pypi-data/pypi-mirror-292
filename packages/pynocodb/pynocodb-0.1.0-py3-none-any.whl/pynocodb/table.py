from __future__ import annotations

import typing as t

from pynocodb.api_endpoint import ApiEndpoint
from pynocodb.api_resource import ApiResource, AsyncApiResource


class TableEndpoint(ApiEndpoint):
    def __init__(self, api_resouce: ApiResource | AsyncApiResource) -> None:
        super().__init__(api_resouce, endpoint_url="/api/v2/meta/bases")
    
    def list_tables(
        self,
        base_id: str,
        page: int = 1,
        page_size: int = -1,
        sort: str | None = None,
        include_m2m: bool = False,
    ) -> dict:
        '''
        List all tables in a given base
        '''
        url = self.format_url(f"/{base_id}/tables")
        params = {
            "page": page,
            "pageSize": page_size,
            "sort": sort,
            "includeM2M": include_m2m,
        }
        return self._api_resouce._request("get", url, params=params)

    def get_table_ids(self, base_id: str) -> dict:
        '''
        return mapper of {table_title: table_id, ...}
        '''
        r = self.list_tables(base_id)
        def ret_sync():
            return {x["title"]: x["id"] for x in r["list"]}
        async def ret_async():
            return {x["title"]: x["id"] for x in (await r)["list"]}

        if self.is_async:
            return ret_async()
        else:
            return ret_sync()

    def create_table(
        self,
        base_id: str,
        table_name: str,
        *,
        title: str | None = None,
        columns: dict | None = None,
        meta: str | dict | None = None,
        order: int | None = None,
    ) -> dict:
        '''
        Create a new table in a given base
        '''
        url = self.format_url(f"/{base_id}/tables")
        data = {
            "table_name": table_name,
            "title": title,
            "columns": columns,
            "meta": meta,
            "order": order,
        }
        return self._api_resouce._request("post", url, json=data)

    def update_table(
        self,
        table_id: str,
        table_name: str | None = None,
        title: str | None = None,
        base_id: str | None = None,
        meta: str | dict | None = None,
    ):
        '''
        Update the table meta data by the given table ID
        '''
        url = f"/api/v2/meta/tables/{table_id}"
        data = {
            "table_name": table_name,
            "title": title,
            "base_id": base_id,
            "meta": meta,
        }
        return self._api_resouce._request("patch", url, json=data)

    def get_table_info(self, table_id: str) -> dict:
        '''
        Read the table meta data by the given table ID
        '''
        url = f"/api/v2/meta/tables/{table_id}"
        return self._api_resouce._request("get", url)

    def list_table_fields(self, table_id: str, exclude_virtual: bool = True) -> dict:
        '''
        return mapper of {column_title: column_id, ...}
        '''
        table_info = self.get_table_info(table_id)
        if exclude_virtual:
            res = {x["title"]: x["id"] for x in table_info["columns"] if not x["virtual"]}
        else:
            res = {x["title"]: x["id"] for x in table_info["columns"]}
        return res

    def delete_table(self, table_id: str) -> dict:
        '''
        Delete the table meta data by the given table ID
        '''
        url = f"/api/v2/meta/tables/{table_id}"
        return self._api_resouce._request("delete", url)
