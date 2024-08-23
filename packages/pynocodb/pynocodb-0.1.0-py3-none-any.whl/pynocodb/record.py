from __future__ import annotations

import typing as t

from pynocodb.api_endpoint import ApiEndpoint
from pynocodb.api_resource import ApiResource, AsyncApiResource


class RecordEndpoint(ApiEndpoint):
    '''
    operation on table records, corresponding to /api/v2/tables/{table_id}/* endpoints
    '''

    def __init__(self, api_resouce: ApiResource | AsyncApiResource) -> None:
        super().__init__(api_resouce, endpoint_url="/api/v2/tables")
    
    def list_records(
        self,
        table_id: str,
        view_id: str | None = None,
        fields: t.List[str] | str | None = None,
        sort: str | None = None,
        where: str | None = None,
        offset: int = 0,
        limit: int = -1,
        shuffle: int = 0,
    ) -> dict:
        '''
        List of all rows from {table_id} table and response data fields can be filtered based on query params.
        '''
        url = self.format_url(f"/{table_id}/records")
        params = {
            "view_id": view_id,
            "fields": fields,
            "sort": sort,
            "where": where,
            "offset": offset,
            "limit": limit,
            "shuffle": shuffle,
        }
        return self._api_resouce._request("get", url, params=params)

    def create_record(self, table_id: str, data: dict) -> dict:
        '''
        Insert a new row in table by providing a key value pair object where key refers to the column alias.
        All the required fields should be included with payload excluding autoincrement and column with default value.
        '''
        url = self.format_url(f"{table_id}/records")
        return self._api_resouce._request("post", url, json=data)

    def update_record(self, table_id: str, data: dict) -> dict:
        '''
        Partial update row in table by providing a key value pair object where key refers to the column alias.
        You need to only include columns which you want to update.
        '''
        url = self.format_url(f"{table_id}/records")
        return self._api_resouce._request("patch", url, json=data)

    def delete_record(self, table_id: str, id: int | str) -> dict:
        '''
        Delete a row by using the primary key column value.
        '''
        url = self.format_url(f"{table_id}/records")
        return self._api_resouce._request("delete", url, json={"Id": id})

    def get_record(
        self,
        table_id: str,
        record_id: str | int,
        fields: t.List[str] | str | None = None,
    ) -> dict:
        '''
        Read a row data by using the primary key column value.
        '''
        url = self.format_url(f"{table_id}/records/{record_id}")
        params = None
        if fields:
            params = {"fields": fields}
        return self._api_resouce._request("get", url, params=params)

    def count_records(
        self,
        table_id: str,
        view_id: str | None = None,
        where: str | None = None,
    ) -> dict:
        '''
        Get rows count of a table by applying optional filters.
        '''
        url = self.format_url(f"{table_id}/records/count")
        params = None
        if view_id:
            params = {**(params or {}), "view_id": view_id}
        if where:
            params = {**(params or {}), "where": where}
        return self._api_resouce._request("get", url, params=params)

    def list_link_records(
        self,
        table_id: str,
        record_id: str | int,
        link_field_id: str,
        fields: t.List[str] | str | None = None,
        sort: str | None = None,
        where: str | None = None,
        offset: int = 0,
        limit: int = -1,
    ) -> dict:
        '''
        This API endpoint allows you to retrieve list of linked records for a specific Link field and Record ID.
        The response is an array of objects containing Primary Key and its corresponding display value.
        '''
        url = self.format_url(f"{table_id}/links/{link_field_id}/records/{record_id}")
        params = {
            "fields": fields,
            "sort": sort,
            "where": where,
            "offset": offset,
            "limit": limit,
        }
        return self._api_resouce._request("get", url, params=params)

    def link_records(
        self,
        table_id: str,
        record_id: str | int,
        link_field_id: str,
        ids: t.List[str | int],
    ) -> dict:
        '''
        This API endpoint allows you to link records to a specific Link field and Record ID.
        The request payload is an array of record-ids from the adjacent table for linking purposes.
        Note that any existing links, if present, will be unaffected during this operation.
        '''
        url = self.format_url(f"{table_id}/links/{link_field_id}/records/{record_id}")
        data = [{"Id": x} for x in ids]
        return self._api_resouce._request("post", url, json=data)

    def unlink_records(
        self,
        table_id: str,
        record_id: str | int,
        link_field_id: str,
        ids: t.List[str | int],
    ) -> dict:
        '''
        This API endpoint allows you to unlink records from a specific Link field and Record ID.
        The request payload is an array of record-ids from the adjacent table for unlinking purposes.
        Note that,
            duplicated record-ids will be ignored.
            non-existent record-ids will be ignored.
        '''
        url = self.format_url(f"{table_id}/links/{link_field_id}/records/{record_id}")
        data = [{"Id": x} for x in ids]
        return self._api_resouce._request("delete", url, json=data)
