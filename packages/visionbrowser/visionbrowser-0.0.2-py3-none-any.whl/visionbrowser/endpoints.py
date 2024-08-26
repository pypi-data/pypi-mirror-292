import aiohttp
import json
from typing import Any, Dict, Optional

from .exceptions import FailedConnection, APIError

BASE_URL = 'https://v1.empr.cloud/api/v1'


class Folders:
    @staticmethod
    async def get_folders_list(token: str) -> Dict[str, Any]:
        """
        Retrieves a list of folders.

        Args:
            token: Your API authentication token.

        Returns:
            A dictionary containing information about the folders.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def create_folder(token: str, folder_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Creates a new folder.

        Args:
            token: Your API authentication token.
            folder_data: A dictionary containing the folder data.
                Example:
                    {
                        'folder_name': 'Folder Name',
                        'folder_icon': 'Icon Name',
                        'folder_color': '#RRGGBB'
                    }

        Returns:
            A dictionary containing information about the created folder.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, data=json.dumps(folder_data)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def edit_folder(token: str, folder_data: Dict[str, str], folder_id: str) -> Dict[str, Any]:
        """
        Edits an existing folder.

        Args:
            token: Your API authentication token.
            folder_data: A dictionary containing the updated folder data.
                Example:
                    {
                        'folder_name': 'New Folder Name',
                        'folder_icon': 'New Icon Name',
                        'folder_color': '#RRGGBB'
                    }
            folder_id: The ID of the folder to edit.

        Returns:
            A dictionary containing information about the edited folder.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.patch(url, headers=headers, data=json.dumps(folder_data)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def delete_folder(token: str, folder_id: str) -> Dict[str, Any]:
        """
        Deletes a folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder to delete.

        Returns:
            A dictionary containing the API response.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.delete(url, headers=headers) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e


class Profiles:
    @staticmethod
    async def get_profiles_list(token: str, folder_id: str, id_arg: Optional[str] = '') -> Dict[str, Any]:
        """
        Retrieves a list of profiles for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.
            id_arg: Optional argument to filter profiles by ID.
                    Can be an empty string (returns all profiles) or a string in the format "?id={profile_id}".
                    Example of id_arg:
                        - name (String), Search by profile name
                        - pn (Integer), Page number
                        - ps (Integer), Page size

        Returns:
            A dictionary containing information about the profiles.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/profiles{id_arg}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def get_profiles_info(token: str, folder_id: str, profile_id: str) -> Dict[str, Any]:
        """
        Retrieves detailed information about a specific profile.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder containing the profile.
            profile_id: The ID of the profile.

        Returns:
            A dictionary containing detailed information about the profile.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/profiles/{profile_id}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def get_fingerprints(token: str, platform: str, version: str) -> Dict[str, Any]:
        """
        Retrieves fingerprints for a specific platform and version.

        Args:
            token: Your API authentication token.
            platform: The platform (e.g., "chrome", "firefox").
            version: The browser version (e.g., "91.0.4472.124").

        Returns:
            A dictionary containing fingerprint data.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/fingerprints/{platform}/{version}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def import_cookies(token: str, folder_id: str, profile_id: str, cookies: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imports cookies into a specific profile.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder containing the profile.
            profile_id: The ID of the profile.
            cookies: A dictionary containing the cookies to import.

        Returns:
            A dictionary containing the API response.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/cookies/import/{folder_id}/{profile_id}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, data=json.dumps(cookies)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def export_cookies(token: str, folder_id: str, profile_id: str) -> Dict[str, Any]:
        """
        Exports cookies from a specific profile.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder containing the profile.
            profile_id: The ID of the profile.

        Returns:
            A dictionary containing the exported cookies.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/cookies/{folder_id}/{profile_id}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def create_profile(token: str, folder_id: str, profile_id: str):
        """
        Creates a new profile. (Not implemented yet)
        """
        raise NotImplementedError("This method is not implemented yet.")

    @staticmethod
    async def edit_profile(token: str, folder_id: str, profile_id: str):
        """
        Edits an existing profile. (Not implemented yet)
        """
        raise NotImplementedError("This method is not implemented yet.")

    @staticmethod
    async def delete_profile(token: str, folder_id: str, profile_id: str):
        """
        Deletes a profile. (Not implemented yet)
        """
        raise NotImplementedError("This method is not implemented yet.")


class Proxy:
    @staticmethod
    async def get_proxy_list(token: str, folder_id: str) -> Dict[str, Any]:
        """
        Retrieves a list of proxies for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.

        Returns:
            A dictionary containing information about the proxies.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/proxies'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def create_proxy(token: str, folder_id: str, proxies: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new proxy for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.
            proxies: A dictionary containing the proxy data.
                Example:
                    body = {
                      "proxies": [
                        {
                          "proxy_name": "Proxy",
                          "proxy_type": "SOCKS5",
                          "proxy_ip": "1.1.1.1",
                          "proxy_port": 1080
                        }
                      ]
                    }

        Returns:
            A dictionary containing information about the created proxy.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/proxies'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, data=json.dumps(proxies)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def edit_proxy(token: str, folder_id: str, proxy_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edits an existing proxy for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.
            proxy_id: The ID of the proxy to edit.
            changes: A dictionary containing the changes to apply to the proxy.
                Example:
                    body = {
                      "proxy_name": "Proxy",
                      "proxy_type": "SOCKS5",
                      "proxy_ip": "1.1.1.1",
                      "proxy_port": 12345,
                      "update_url": "https://link-to-update-proxy.com/api/update"
                    }

        Returns:
            A dictionary containing information about the edited proxy.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/proxies/{proxy_id}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(url, headers=headers, data=json.dumps(changes)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def delete_proxy(token: str, folder_id: str, proxies: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deletes proxies for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.
            proxies: A dictionary containing the proxies to delete.
                Example:
                    body = {
                      "proxy_ids": [
                        "e3b7b1e0-9b0a-4c9a-8b9a-9b0a4c9a8b9a"
                      ]
                    }

        Returns:
            A dictionary containing the API response.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/proxies'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.delete(url, headers=headers, data=json.dumps(proxies)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e


class Statuses:
    @staticmethod
    async def get_status_list(token: str, folder_id: str) -> Dict[str, Any]:
        """
        Retrieves a list of statuses for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.

        Returns:
            A dictionary containing information about the statuses.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/statuses'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def create_status(token: str, folder_id: str, statuses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates new statuses for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.
            statuses: A dictionary containing the statuses' data.
                Example:
                    body = {
                      "statuses": [
                        [
                          "Good",
                          "#00AB55"
                        ]
                      ]
                    }

        Returns:
            A dictionary containing information about the created statuses.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/statuses'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, data=json.dumps(statuses)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def edit_status(token: str, folder_id: str, status_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edits an existing status for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.
            status_id: The ID of the status to edit.
            changes: A dictionary containing the changes to apply to the status.
                Example:
                    body = {
                      "name": "New Status",
                      "color": "#000000"
                    }

        Returns:
            A dictionary containing information about the edited status.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/statuses/{status_id}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(url, headers=headers, data=json.dumps(changes)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def delete_status(token: str, folder_id: str, statuses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deletes statuses for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.
            statuses: A dictionary containing the statuses to delete.
                Example:
                    body = {
                      "status_ids": [
                        "e3b7b1e0-9b0a-4c9a-8b9a-9b0a4c9a8b9a"
                      ]
                    }


        Returns:
            A dictionary containing the API response.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/statuses'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.delete(url, headers=headers, data=json.dumps(statuses)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

class Tags:
    @staticmethod
    async def get_tags_list(token: str, folder_id: str) -> Dict[str, Any]:
        """
        Retrieves a list of tags for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.

        Returns:
            A dictionary containing information about the tags.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/tags'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def create_tag(token: str, folder_id: str, tags: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates new tags for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.
            tags: A dictionary containing the tags' data.
                Example:
                    body = {
                      "tags": [
                        "1",
                        "2"
                      ]
                    }

        Returns:
            A dictionary containing information about the created tags.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/tags'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, data=json.dumps(tags)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def edit_tag(token: str, folder_id: str, tag_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edits an existing tag for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.
            tag_id: The ID of the tag to edit.
            changes: A dictionary containing the changes to apply to the tag.
                Example:
                    body = {
                      "name": "Tag1"
                    }

        Returns:
            A dictionary containing information about the edited tag.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/tags/{tag_id}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(url, headers=headers, data=json.dumps(changes)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def delete_tag(token: str, folder_id: str, tags: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deletes tags for a specific folder.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder.
            tags: A dictionary containing the tags to delete.
                Example:
                    body = {
                      "tag_ids": [
                        "your_tag_id"
                      ]
                    }

        Returns:
            A dictionary containing the API response.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/folders/{folder_id}/tags'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.delete(url, headers=headers, data=json.dumps(tags)) as response:
                    response_json = await response.json()

                    if 'error' in response_json:
                        raise APIError(response_json['error'])

                    return response_json
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e