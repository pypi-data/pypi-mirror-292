import aiohttp
from .exceptions import *
from typing import Any, Optional, Dict
import json
import logging


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
BASE_URL = 'http://localhost:3030'


class Api:
    @staticmethod
    async def get_launched_profiles(token: str) -> Dict[str, Any]:
        """
        Retrieves a list of launched profiles.

        Args:
            token: Your API authentication token.

        Returns:
            A dictionary containing information about the launched profiles.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
        """
        url = f'{BASE_URL}/list'
        headers = {'X-Token': token}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    return await response.json()
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def start_profile(token: str, folder_id: str, profile_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Starts a profile.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder containing the profile.
            profile_id: The ID of the profile to start.
            data: Optional data to pass to the profile on startup. Example: --headless, or else

        Returns:
            A dictionary containing information about the started profile.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
            APIError: If the API returns an error.
        """
        url = f'{BASE_URL}/start/{folder_id}/{profile_id}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                if data:
                    async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                        response_json = await response.json()
                else:
                    async with session.get(url, headers=headers) as response:
                        response_json = await response.json()

                if 'error' in response_json:
                    raise APIError(response_json['error'])

                if response_json.get('port') is None:
                    logger.warning(
                        "The port was found to be empty after the application/process returned. "
                        "Most likely the profile was launched inside Vision, or some other issue occurred."
                    )

                return response_json

            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e

    @staticmethod
    async def stop_profile(token: str, folder_id: str, profile_id: str) -> str:
        """
        Stops a profile.

        Args:
            token: Your API authentication token.
            folder_id: The ID of the folder containing the profile.
            profile_id: The ID of the profile to stop.

        Returns:
            The response text from the API.

        Raises:
            FailedConnection: If a connection to the API cannot be established.
        """
        url = f'{BASE_URL}/stop/{folder_id}/{profile_id}'
        headers = {'X-Token': token, 'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    return await response.text()
            except aiohttp.client_exceptions.ClientConnectorError as e:
                raise FailedConnection() from e
