from __future__ import annotations

import typing as t

from pynocodb.api_endpoint import ApiEndpoint
from pynocodb.api_resource import ApiResource, AsyncApiResource


class BaseEndpoint(ApiEndpoint):
    def __init__(self, api_resouce: ApiResource | AsyncApiResource) -> None:
        super().__init__(api_resouce, endpoint_url="/api/v2/meta/bases")
    
    def list_base_users(self, base_id: str) -> dict:
        '''
        List all users in the given base.
        '''
        url = self.format_url(f"/{base_id}/users")
        return self._api_resouce._request("get", url)
    
    def get_base_user_ids(self, base_id: str) -> dict:
        '''
        return mapper of {user_email: user_id, ...} in base
        '''
        users = self.list_base_users(base_id)
        def ret_sync():
            return {x["email"]: x["id"] for x in users["users"]["list"]}
        async def ret_async():
            return {x["email"]: x["id"] for x in (await users)["users"]["list"]}

        if self.is_async:
            return ret_async()
        else:
            return ret_sync()

    def create_base_user(
        self,
        base_id: str,
        email: str,
        roles: t.Literal["no-access", "commenter", "editor", "guest", "owner", "viewer", "creator"] = "no-access",
    ) -> dict:
        '''
        Create a user and add it to the given base
        '''
        url = self.format_url(f"/{base_id}/users")
        data = {
            "email": email,
            "roles": roles,
        }
        return self._api_resouce._request("post", url, json=data)

    def update_base_user(
        self,
        base_id: str,
        user_id: str,
        email: str,
        roles: t.Literal["no-access", "commenter", "editor", "guest", "owner", "viewer", "creator"] = "no-access",
    ) -> dict:
        '''
        Update a given user in a given base. Exclusive for Super Admin.
        Access with API Tokens will be blocked.
        '''
        url = self.format_url(f"/{base_id}/users/{user_id}")
        data = {
            "email": email,
            "roles": roles,
        }
        return self._api_resouce._request("patch", url, json=data)

    def delete_base_user(
        self,
        base_id: str,
        user_id: str,
    ) -> dict:
        '''
        Delete a given user in a given base. Exclusive for Super Admin.
        Access with API Tokens will be blocked.
        '''
        url = self.format_url(f"/{base_id}/users/{user_id}")
        return self._api_resouce._request("delete", url)

    def resend_invite(
        self,
        base_id: str,
        user_id: str,
    ) -> dict:
        '''
        Resend Invitation to a specific user
        '''
        url = self.format_url(f"/{base_id}/users/{user_id}/resend-invite")
        return self._api_resouce._request("post", url)

    def list_bases(self) -> dict:
        '''
        List all base meta data
        '''
        url = self.format_url()
        return self._api_resouce._request("get", url)

    def get_base_ids(self) -> dict:
        '''
        return a mapper of {base_title: base_id, ...}
        '''
        r = self.list_bases()
        def ret_sync():
            if bases := r.get("list"):
                return {x["title"]: x["id"] for x in bases}
            else:
                return {}
        async def ret_async():
            if bases := (await r).get("list"):
                return {x["title"]: x["id"] for x in bases}
            else:
                return {}

        if self.is_async:
            return ret_async()
        else:
            return ret_sync()

    def get_node_info(self, base_id: str="a") -> dict:
        '''
        Get info such as node version, arch, platform, is docker, rootdb and package version of a given base
        TODO: it seems return node info instead of base info, the `base_id` parameter does not matter
        '''
        url = self.format_url(f"/{base_id}/info")
        return self._api_resouce._request("get", url)

    def get_base_info(self, base_id: str) -> dict:
        '''Get the info of a given base'''
        url = self.format_url(f"/{base_id}")
        return self._api_resouce._request("get", url)

    def get_base_cost(self, base_id: str) -> dict:
        '''
        Calculate the Base Cost
        '''
        url = self.format_url(f"/{base_id}/cost")
        return self._api_resouce._request("get", url)

    def create_base(
        self,
        title: str,
        *,
        description: str | None = None,
        color: str | None = None,
        sources: list[dict] | None = None,
        status: str | None = None,
        type: t.Literal["database", "documentation", "dashboard"] = "database",
        linked_db_project_ids: list[str] | None = None,
        meta: str | dict | None = None,
        external: bool = False,
    ) -> dict:
        '''
        Create a new base
        '''
        url = self.format_url()
        data = {
            "title": title,
            "description": description,
            "color": color,
            "sources": sources,
            "status": status,
            "type": type,
            "linked_db_project_ids": linked_db_project_ids,
            "meta": meta,
            "external": external,
        }
        return self._api_resouce._request("post", url, json=data)
    
    def update_base(
        self,
        base_id: str,
        *,
        title: str,
        color: str | None = None,
        status: str | None = None,
        linked_db_project_ids: list[str] | None = None,
        order: int = False,
    ):
        '''
        Update the given base
        '''
        url = self.format_url(f"/{base_id}")
        data = {
            "title": title,
            "color": color,
            "status": status,
            "linked_db_project_ids": linked_db_project_ids,
            "order": order,
        }
        return self._api_resouce._request("patch", url, json=data)
    
    def delete_base(self, base_id: str):
        '''Delete the given base'''
        url = self.format_url(f"/{base_id}")
        return self._api_resouce._request("delete", url)


    def duplicate_base(
        self,
        base_id: str,
        *,
        base: dict | None = None,
        exclude_data: bool = True,
        exclude_views: bool = False,
        exclude_hooks: bool = False,
    ) -> dict:
        url = f"/api/v2/meta/duplicate/{base_id}"
        data = {
            "options": {
                "excludeData": exclude_data,
                "excludeViews": exclude_views,
                "excludeHooks": exclude_hooks,
            },
            "base": base,
        }
        return self._api_resouce._request("post", url, json=data)

    def get_shared_base(self, base_id: str) -> dict:
        '''Get Base Shared Base'''
        url = self.format_url(f"/{base_id}/shared")
        return self._api_resouce._request("get", url)

    def delete_shared_base(self, base_id: str) -> dict:
        '''Delete Base Shared Base'''
        url = self.format_url(f"/{base_id}/shared")
        return self._api_resouce._request("delete", url)

    def create_shared_base(
        self,
        base_id: str,
        password: str,
        roles: t.Literal["commenter", "editor", "viewer"] = "viewer",
    ) -> dict:
        '''Create Base Shared Base'''
        url = self.format_url(f"/{base_id}/shared")
        data = {
            "password": password,
            "roles": roles,
        }
        return self._api_resouce._request("post", url, json=data)

    def update_shared_base(
        self,
        base_id: str,
        password: str,
        roles: t.Literal["commenter", "editor", "viewer"] = "viewer",
    ) -> dict:
        '''Update Base Shared Base'''
        url = self.format_url(f"/{base_id}/shared")
        data = {
            "password": password,
            "roles": roles,
        }
        return self._api_resouce._request("patch", url, json=data)

    def list_base_audits(
        self,
        base_id: str,
        *,
        offset: int = 0,
        limit: int = 100,
        source_id: str | None = None,
        order_by: dict | None = None,
    ) -> dict:
        '''List all audit data in the given base'''
        url = self.format_url(f"/{base_id}/audits")
        params = None
        if offset:
            params = {**(params or {}), "offset": offset}
        if limit:
            params = {**(params or {}), "limit": limit}
        if source_id:
            params = {**(params or {}), "source_id": source_id}
        if order_by:
            params = {**(params or {}), "order_by": order_by}
        return self._api_resouce._request("get", url, params=params)
