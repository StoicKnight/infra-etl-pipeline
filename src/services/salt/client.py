import logging
from typing import Any, Dict, List, Optional

import httpx

from src.services.salt import exceptions, models

log = logging.getLogger(__name__)


class SaltAPIClient:
    def __init__(self, api_url: str, ssl_verify: bool = False):
        """
        Initializes the client. Use the `create` classmethod for a fully
        authenticated instance.
        """
        self.api_url = api_url.rstrip("/")
        self.__client = httpx.AsyncClient(
            base_url=self.api_url,
            verify=ssl_verify,
            timeout=30.0,
        )
        self.__token: Optional[str] = None

        # Attach endpoint handlers, similar to NetBoxAPIClient
        self.minions = MinionsEndpoints(self.__client)
        self.jobs = JobsEndpoints(self.__client)

    @classmethod
    async def create(
        cls,
        api_url: str,
        username: str,
        password: str,
        eauth: str = "pam",
        ssl_verify: bool = False,
    ):
        instance = cls(api_url, ssl_verify)
        auth_payload = {
            "username": username,
            "password": password,
            "eauth": eauth,
        }
        await instance.__login(auth_payload)
        return instance

    async def __login(self, auth_payload: Dict[str, Any]):
        log.info(f"Attempting to authenticate with Salt API at {self.api_url}")
        response: Optional[httpx.Response] = None
        try:
            headers = {"Accept": "application/json"}
            response = await self.__client.post(
                "/login", json=auth_payload, headers=headers
            )
            response.raise_for_status()
            data = response.json()
            self.__token = data["return"][0]["token"]
            self.__client.headers["X-Auth-Token"] = self.__token
            self.__client.headers["Accept"] = "application/json"
            log.info("Successfully authenticated with Salt API.")
            log.debug(f"Token: {self.__token}")

        except httpx.HTTPStatusError as e:
            log.error(
                f"Authentication failed: {e.response.status_code} - {e.response.text}"
            )
            await self.close()  # Ensure client is closed on failure
            raise exceptions.SaltAPIError(
                "Authentication failed",
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e
        except (KeyError, IndexError, TypeError) as e:
            log.error("Failed to parse token from API response", exc_info=True)
            status = response.status_code if response else None
            text = (
                response.text if response else "Response body was malformed or empty."
            )
            await self.close()
            raise exceptions.SaltAPIError(
                "Could not parse auth token from Salt API response",
                status_code=status,
                response_text=text,
            ) from e

    async def close(self):
        await self.__client.aclose()
        log.info("Salt API client session closed.")

    # async def close(self):
    #     await self.__client.aclose()
    #     log.info("Salt API client session closed.")
    #
    # async def _login(self):
    #     """Authenticate with the Salt API and store the session token."""
    #     login_url = f"{self.api_url}/login"
    #     headers = {"Accept": "application/json"}
    #     response: Optional[httpx.Response] = None
    #
    #     log.info(f"Attempting to authenticate with Salt API at {self.api_url}")
    #     try:
    #         response = await self.__client.post(
    #             login_url, json=self.__auth_payload, headers=headers
    #         )
    #         response.raise_for_status()
    #
    #         data = response.json()
    #         self.__token = data["return"][0]["token"]
    #
    #         self.__client.headers["X-Auth-Token"] = self.__token
    #         self.__client.headers["Accept"] = "application/json"
    #         log.info("Successfully authenticated with Salt API.")
    #         log.debug(f"Token: {self.__token}")
    #     except httpx.HTTPStatusError as e:
    #         log.error(
    #             f"Authentication failed with status {e.response.status_code}",
    #             exc_info=True,
    #         )
    #         raise exceptions.SaltAPIError(
    #             "Authentication failed",
    #             status_code=e.response.status_code,
    #             response_text=e.response.text,
    #         ) from e
    #     except (KeyError, IndexError) as e:
    #         log.error("Failed to parse token from API response", exc_info=True)
    #         status = response.status_code if response else None
    #         text = (
    #             response.text if response else "Response body was malformed or empty."
    #         )
    #         raise exceptions.SaltAPIError(
    #             "Could not parse auth token from Salt API response",
    #             status_code=status,
    #             response_text=text,
    #         ) from e

    async def run_command(
        self,
        fun: str,
        tgt: str,
        tgt_type: str = "glob",
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """
        Executes a command against the Salt API.

        Returns:
            Raw JSON dictionary from the API response.
        """
        if not self._token:
            raise exceptions.SaltAPIError(
                "Cannot run command without a valid login session."
            )

        payload = [
            {
                "client": "local",
                "tgt": tgt,
                "fun": fun,
                "tgt_type": tgt_type,
                "arg": args or [],
                "kwarg": kwargs or {},
                "timeout": timeout,
            }
        ]

        log.debug(f"Running Salt command: fun={fun}, tgt={tgt}")
        try:
            response = await self._client.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            log.error(f"Salt API command '{fun}' failed", exc_info=True)
            raise exceptions.SaltAPIError(
                f"API command '{fun}' failed",
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e

    async def get_minion_grains(
        self,
        target: str = "*",
        target_type: str = "glob",
    ) -> models.SaltAPIResponse:
        log.info(f"Fetching grains for target: {target}")
        raw_response = await self.run_command(
            fun="grains.items",
            tgt=target,
            tgt_type=target_type,
        )

        log.debug(f"Received raw grains response from Salt API: {raw_response}")
        validated_response = models.SaltAPIResponse.model_validate(raw_response)
        log.info("Successfully fetched and validated grains.")
        return validated_response
