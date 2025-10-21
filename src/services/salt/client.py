import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx

from src.services.salt import exceptions, models

log = logging.getLogger(__name__)


class SaltAPIClient:
    def __init__(self, api_url: str, ssl_verify: bool = False):
        """
        Initializes the client.

        Note:
            For a fully authenticated instance, use the `create` classmethod.
        """
        self.api_url = api_url.rstrip("/")
        self.__client = httpx.AsyncClient(
            base_url=self.api_url,
            verify=ssl_verify,
            timeout=30.0,
        )
        self.__token: Optional[str] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

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
        await instance._login(auth_payload)
        return instance

    async def _login(self, auth_payload: Dict[str, Any]):
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
            self.__client.headers["X-Auth-Token"] = str(self.__token)
            log.info("Successfully authenticated with Salt API.")
            log.debug(f"Token: {str(self.__token[:8])}...")
        except httpx.HTTPStatusError as e:
            log.error(
                f"Authentication failed: {e.response.status_code} - {e.response.text}"
            )
            await self.close()
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
        if not self.__client.is_closed:
            await self.__client.aclose()
            log.info("Salt API client session closed.")

    async def _run_job(
        self,
        fun: str,
        tgt: str,
        tgt_type: str = "glob",
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        client: str = "local_sync",
    ) -> Dict[str, Any]:
        if not self.__token:
            raise exceptions.SaltAPIError(
                "Cannot run command without a valid login session."
            )
        payload = [
            {
                "client": client,
                "tgt": tgt,
                "fun": fun,
                "tgt_type": tgt_type,
                "arg": args or [],
                "kwarg": kwargs or {},
            }
        ]
        log.debug(f"Submitting Salt job: client={client}, fun={fun}, tgt={tgt}")
        try:
            response = await self.__client.post("/minions", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            log.error(f"Salt API command '{fun}' failed", exc_info=True)
            raise exceptions.SaltAPIError(
                f"API command '{fun}' failed",
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e

    async def get_job_result(self, jid: str) -> Dict[str, Any]:
        log.debug(f"Fetching result for JID: {jid}")
        try:
            response = await self.__client.get(f"/jobs/{jid}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            log.error(f"Failed to fetch result for JID {jid}", exc_info=True)
            raise exceptions.SaltAPIError(
                f"Failed to fetch result for JID {jid}",
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e

    async def run_command(
        self,
        fun: str,
        tgt: str,
        tgt_type: str = "glob",
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        timeout: int = 120,
        poll_interval: float = 2.0,
    ) -> Dict[str, Any]:
        job_submission_response = await self._run_job(
            fun=fun,
            tgt=tgt,
            tgt_type=tgt_type,
            args=args,
            kwargs=kwargs,
            client="local_async",
        )
        try:
            jid = job_submission_response["return"][0]["jid"]
            log.info(f"Successfully submitted job. JID: {jid}")
        except (KeyError, IndexError):
            raise exceptions.SaltAPIError(
                "Could not parse JID from Salt API response",
                response_text=str(job_submission_response),
            )

        total_wait_time = 0
        while total_wait_time < timeout:
            job_result = await self.get_job_result(jid)
            info_block = job_result.get("info", [{}])[0]
            return_block = job_result.get("return", [{}])[0]

            targeted_minions = set(info_block.get("Minions", []))
            if not targeted_minions:
                log.warning(f"Job {jid} did not target any minions.")
                return {}

            returned_minions = set(return_block.keys())
            if targeted_minions.issubset(returned_minions):
                log.info(
                    f"Job {jid} completed successfully. All {len(targeted_minions)} minions have returned."
                )
                return return_block
            log.debug(
                f"Job {jid} running. Got {len(returned_minions)}/{len(targeted_minions)} results. Waiting..."
            )
            await asyncio.sleep(poll_interval)
            total_wait_time += poll_interval

        raise exceptions.SaltAPIError(f"Job {jid} timed out after {timeout} seconds.")

    async def get_minion_grains(
        self,
        target: str = "*",
        target_type: str = "glob",
    ) -> models.MinionGrainsResponse:
        log.info(f"Fetching grains for target: {target}")
        response = await self.run_command(
            fun="grains.items",
            tgt=target,
            tgt_type=target_type,
        )
        log.debug(f"Received grains response from Salt API: {response}")
        validated_response = models.MinionGrainsResponse.model_validate(response)
        log.info("Successfully fetched and validated grains.")
        return validated_response

    # async def get_minion_grains(
    #     self,
    #     target: str = "*",
    #     target_type: str = "glob",
    # ) -> Dict[str, Any]:
    #     log.info(f"Fetching grains for target: {target}")
    #     response = await self.run_command(
    #         fun="grains.items",
    #         tgt=target,
    #         tgt_type=target_type,
    #     )
    #     log.debug(f"Received grains response from Salt API: {response}")
    #     log.info("Successfully fetched and validated grains.")
    #     return response
