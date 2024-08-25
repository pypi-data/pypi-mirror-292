"""aiohttp support for Ogero."""

import importlib.util
import logging
import sys

from pyogero.const import (
    API_ENDPOINTS,
    # CERT_PATH,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_OK,
    DefaultHeaders,
    default_headers,
)
from pyogero.exceptions import AuthenticationException
from pyogero.types import (
    Account,
    BillInfo,
    ConsumptionInfo,
    ErrorResponse,
    LoginResponse,
)
from pyogero.utils import (
    parse_accounts,
    parse_bills,
    parse_consumption_info,
    parse_error_message,
)

mod_spec = importlib.util.find_spec("aiohttp")
if mod_spec is None:
    logging.getLogger().error("Failed to import aiohttp")
    sys.exit(1)
else:
    from aiohttp.client import ClientResponse, ClientSession


class Ogero:
    """aiohttp class for interacting with Ogero APIs."""

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession | None = None,
        logger: logging.Logger | None = None,
        debug: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        """
        Init.

        ```
        @param username: str - username for Ogero account
        @param password: str - password for Ogero account
        @param debug: bool - debug mode
        @param logger: Logger
        ```
        """
        if not (username and password):
            msg = "You need to supply both username and password"
            raise AuthenticationException(msg)

        self.username = username
        self.password = password
        self.debug = debug
        self.logger = logger if logger is not None else logging.getLogger()
        self.session_id = None

        if not session:
            self.session = ClientSession()
        else:
            self.session = session

        # self.ssl_context = ssl.create_default_context(cafile=CERT_PATH)

    async def login(self) -> bool:
        """Log into the account and caches the session id."""
        url = API_ENDPOINTS["login"]

        headers = default_headers()
        payload = {"Username": self.username, "Password": self.password}

        async with self.session.post(
            url,
            headers=headers,
            data=payload,
            #   ssl=self.ssl_context
        ) as response:
            self.session_id = None
            await self.handle_response_fail(response)
            jsondata: LoginResponse = await response.json()

        self.logger.debug("Login response status: %s", response.status)

        self.session_id = jsondata["SessionID"]

        return True

    async def get_accounts(
        self, account: Account | None = None
    ) -> list[Account] | None:
        """Get user phone/internet accounts."""
        url = API_ENDPOINTS["dashboard"]

        response = await self.request_get(url, account)
        if response is None:
            return None
        await self.handle_response_fail(response)
        content = await response.text()
        accounts = parse_accounts(content)

        self.logger.debug("Dashboard response status: %s", response.status)
        self.logger.debug("Dumping accounts response: %s", accounts)

        return accounts

    async def get_bill_info(self, account: Account | None = None) -> BillInfo | None:
        """
        Get bill info for phone account.

        ```
        @param account: Account - Phone/Internet account
        ```
        """
        url = API_ENDPOINTS["bill"]

        response = await self.request_get(url, account)
        if response is None:
            return None
        await self.handle_response_fail(response)
        content = await response.text()
        bill_info = parse_bills(content)

        self.logger.debug("Bill response status: %s", response.status)
        self.logger.debug(
            "Dumping bill response: %s \n%s",
            bill_info,
            bill_info.bills if bill_info is not None else None,
        )

        return bill_info

    async def get_consumption_info(
        self, account: Account | None = None
    ) -> ConsumptionInfo | None:
        """
        Get consumption info for internet account.

        ```
        @param account: Account - Phone/Internet account
        ```
        """
        url = API_ENDPOINTS["consumption"]

        response = await self.request_get(url, account)
        if response is None:
            return None
        await self.handle_response_fail(response)
        content = await response.text()
        consumption_info = parse_consumption_info(content)

        self.logger.debug("Consumption response status: %s", response.status)
        self.logger.debug("Dumping consumption response: %s", consumption_info)

        return consumption_info

    async def request_get(
        self,
        url: str,
        account: Account | None = None,
        headers: DefaultHeaders | None = None,
        max_retries: int = 1,
    ) -> ClientResponse | None:
        """
        Send get request and check if session is active.

        ```
        @param url: str - Endpoint url
        @param account: Account - Phone/Internet account
        @param headers: DefaultHeaders
        ```
        """
        if max_retries < 0:
            return None

        if self.session_id is None:
            await self.login()

        try:
            params = self._get_params(account)
            formatted_url = url.format_map(params)
            _headers: DefaultHeaders = (
                headers if headers is not None else default_headers()
            )
            response = await self.session.get(
                formatted_url,
                headers=_headers,
                #   ssl=self.ssl_context
            )
            await self.handle_response_fail(response)
        except AuthenticationException as ex:
            self.logger.debug("AuthenticationException: %s", ex)
            await self.login()
            response = await self.request_get(url, account, headers, max_retries - 1)

        return response

    def _get_params(self, account: Account | None = None) -> dict[str, str]:
        if self.session_id is None:
            msg = "Login first"
            raise AuthenticationException(msg) from None

        return {
            "session_id": self.session_id,
            "username": self.username,
            "phone_account": account.phone if account else "",
            "internet_account": account.internet if account else "",
        }

    async def handle_response_fail(
        self,
        response: ClientResponse,
    ) -> None:
        """
        Handle response status codes.

        ```
        @param response - aiohttp.Response - the full response object
        ```
        """
        if (
            response.status == HTTP_STATUS_BAD_REQUEST
            and response.content_type == "application/json"
        ):
            resp: ErrorResponse = await response.json()
            msg = resp["error"]["message"]
            self.logger.debug("AuthenticationException: %s", msg)
            raise AuthenticationException(msg)

        if response.status == HTTP_STATUS_OK and response.content_type == "text/html":
            content = await response.text()
            msg = parse_error_message(content)
            if msg is not None and msg.startswith("You are required to login"):
                raise AuthenticationException(msg)

        response.raise_for_status()
