"""antconnect v2 python package main file to communicate/connect with ANT Common Data Engineering.

ANT:
    * API Documentation:  https://api-alpha.antcde.io/api/2.0/documentation
    * ANT Documentation:  https://docs.antcde.io/
"""

from __future__ import annotations
from pydantic import BaseModel
import requests

from ant_connect.utils import ModelBaseClass, TokenResponse
from ant_connect.config import HostUrlConfig, AlphaHostUrl, TokenConfig


class ApiConnector(BaseModel):
    """
    Static class that allows a user to set up a connection with
    the ANT V2.0 API. Once a user is logged in, all Model calls
    will use that user's credentials.

    ANT:
        * API Documentation:  https://api.antcde.io/api/2.0/documentation
        * ANT Documentation:  https://docs.antcde.io/
    """

    _access_token: str = None
    _host: str = None
    _authenticated: bool = False
    _logging: bool = False
    _alpha: bool = False

    @staticmethod
    def activate(
        access_token: str | TokenResponse,
        logging: bool = False,
        multi_user_mode: bool = False,
        auto_throttle: bool = False,
        alpha: bool = False,
    ) -> None:
        """
        Set the current user . While a user is logged in, all Model calls in the current
        process  will use this user's credentials.

        ### NOTE:\n
        Make sure to create a token before trying to login. Go to https://app.antcde.io/settings to
        "Tokens" or get the access token object with the '_get_token_object' method.

        Args:
            access_token (str): Personal access token to connect to all ANT objects.
            logging (bool, optional): Turn logging on and off. Defaults to False.
            multi_user_mode (bool, optional): Allows a script to handle multiple users. Defaults to False.
            auto_throttle (bool, optional):  When True, the process sleeps when requests in time-frame are exceeded. Defaults to False.
            alpha (bool, optional): Use the alpha host url. Defaults to False.

        Returns:
            ApiConnector: Object containing private connection access token and host
        """
        # TODO docstring format

        if isinstance(access_token, TokenResponse):
            access_token = access_token.access_token

        if not multi_user_mode:
            # Set the access token in the CLASS definition of each model
            ModelBaseClass._access_token = access_token
            ModelBaseClass._auto_throttle = auto_throttle
        else:
            # TODO: add multi user feature
            access_token = None
        
        if alpha:
            host = AlphaHostUrl.host
            ModelBaseClass._get_host = "/".join((host,  AlphaHostUrl.type,  AlphaHostUrl.version))
        else:
            host = HostUrlConfig.host
            ModelBaseClass._get_host = "/".join((host, HostUrlConfig.type, HostUrlConfig.version))

        ApiConnector._access_token = access_token
        ApiConnector._host = host
        ApiConnector._authenticated = True
        ApiConnector._logging = logging

    @classmethod
    def _get_token_object(
        cls,
        username: str,
        password: str,
        client_id: str,
        client_secret: str,
        alpha: bool = False,
    ) -> TokenResponse:
        """Use credentials to get the access token object response.

        Args:
            username (str): ANT user username
            password (str): ANT user password
            client_id (str): ANT user clientid
            client_secret (str): ANT user client secret
            alpha (bool, optional): Use the alpha host url. Defaults to False.

        Raises:
            ValueError: raises an error when creating a connection failed
        """
        # Do login and create logged in token
        parameters = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        if alpha:
            host = AlphaHostUrl.host
        else:
            host = HostUrlConfig.host
        connect_url = "/".join((host, TokenConfig.endpoint))

        connection_response = requests.post(url=connect_url, data=parameters, headers={}, verify=True)

        # check if connection is succesfull
        if connection_response.ok:
            token_object = TokenResponse.from_json(request_response=connection_response.json())
        else:
            raise ValueError(
                f"Could not obtain an access token, response code {connection_response.status_code} was given with response message: '{connection_response.json()['message']}'"
            )

        # return token_object.access_token
        return token_object
