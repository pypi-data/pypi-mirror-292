from __future__ import annotations

from pynocodb.api_endpoint import ApiEndpoint
from pynocodb.api_resource import ApiResource, AsyncApiResource


class AuthEndpoint(ApiEndpoint):
    '''
    auth user operations still use the v1 api because nocodb not provides corresponding v2 api documents yet.
    '''
    def __init__(self, api_resouce: ApiResource | AsyncApiResource) -> None:
        super().__init__(api_resouce, endpoint_url="/api/v1/auth")

    def signup(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> dict:
        url = self.format_url("/user/signup")
        data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        }
        r = self._api_resouce._request("post", url, json=data)
        def ret_sync():
            self._api_resouce.set_token(r.get("token"))
            return r
        async def ret_async():
            r2 = await r
            self._api_resouce.set_token(r2.get("token"))
            return r2

        if self.is_async:
            return ret_async()
        else:
            return ret_sync()

    def signin(
        self,
        email: str,
        password: str,
    ) -> dict:
        url = self.format_url("/user/signin")
        data = {
            "email": email,
            "password": password,
        }
        r = self._api_resouce._request("post", url, json=data)
        def ret_sync():
            self._api_resouce.set_token(r.get("token"))
            return r
        async def ret_async():
            r2 = await r
            self._api_resouce.set_token(r2.get("token"))
            return r2

        if self.is_async:
            return ret_async()
        else:
            return ret_sync()

    def signout(self) -> dict:
        url = self.format_url("/user/signout")
        r = self._api_resouce._request("post", url)
        def ret_sync():
            self._api_resouce.set_token(r.get("token"))
            return r
        async def ret_async():
            r2 = await r
            self._api_resouce.set_token(r2.get("token"))
            return r2

        if self.is_async:
            return ret_async()
        else:
            return ret_sync()

    def user_info(
        self,
        base_id: str | None = None,
    ) -> dict:
        url = self.format_url("/user/me")
        params = None
        # TODO: get base_id from base_name
        if base_id:
            params = {
                "base_id": base_id,
            }
        return self._api_resouce._request("get", url, params=params)

    def forgot_password(self, email: str) -> dict:
        url = self.format_url("/password/forgot")
        data = {
            "email": email,
        }
        return self._api_resouce._request("post", url, json=data)

    def change_password(self, old_password: str, new_password: str) -> dict:
        url = self.format_url("/password/change")
        data = {
            "currentPassword": old_password,
            "newPassword": new_password,
        }
        return self._api_resouce._request("post", url, json=data)

    def refresh_token(self) -> dict:
        url = self.format_url("/token/refresh")
        r = self._api_resouce._request("post", url)
        def ret_sync():
            self._api_resouce.set_token(r.get("token"))
            return r
        async def ret_async():
            r2 = await r
            self._api_resouce.set_token(r2.get("token"))
            return r2

        if self.is_async:
            return ret_async()
        else:
            return ret_sync()
