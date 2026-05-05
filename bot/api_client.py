"""HTTP client wrapping the Gab44 FastAPI backend.

Each Telegram user has a JWT cached on the bot side (returned from
/api/auth/telegram-link). The client adds the JWT for user-scoped routes and
falls back to the service token for the internal surface.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class BackendError(Exception):
    """Backend returned a non-2xx response."""

    def __init__(self, status: int, message: str):
        super().__init__(f"backend {status}: {message}")
        self.status = status
        self.message = message


class BackendClient:
    """Thin async wrapper around the FastAPI backend."""

    def __init__(self, base_url: str, service_token: str, timeout: float = 30.0):
        self._base_url = base_url.rstrip("/")
        self._service_token = service_token
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    # ── Public surface ──────────────────────────────────────────────

    async def link_telegram(self, telegram_user_id: int, **profile: Any) -> dict:
        """Link a Telegram user to a (possibly new) Gab44 account.

        Returns {user_id, subscription_tier, has_birth_data, jwt}.
        """
        return await self._post(
            "/api/auth/telegram-link",
            json={"telegram_user_id": telegram_user_id, **profile},
            service=True,
        )

    async def get_chart(self, jwt: str) -> dict:
        return await self._get("/api/chart/me", jwt=jwt)

    async def get_daily_guidance(self, jwt: str) -> dict:
        return await self._get("/api/guidance/daily", jwt=jwt)

    async def get_transits(self, jwt: str) -> dict:
        return await self._get("/api/transits/upcoming", jwt=jwt)

    async def coach_message(self, jwt: str, session_id: str, message: str) -> dict:
        return await self._post(
            "/api/chat",
            json={"session_id": session_id, "message": message},
            jwt=jwt,
        )

    async def friend_message(self, jwt: str, session_id: str, message: str) -> dict:
        return await self._post(
            "/api/friend/chat",
            json={"session_id": session_id, "message": message},
            jwt=jwt,
        )

    # ── Internal helpers ────────────────────────────────────────────

    async def _get(self, path: str, *, jwt: Optional[str] = None, service: bool = False) -> dict:
        response = await self._client.get(path, headers=self._headers(jwt, service))
        return self._unwrap(response)

    async def _post(
        self,
        path: str,
        *,
        json: Optional[dict] = None,
        jwt: Optional[str] = None,
        service: bool = False,
    ) -> dict:
        response = await self._client.post(path, json=json, headers=self._headers(jwt, service))
        return self._unwrap(response)

    def _headers(self, jwt: Optional[str], service: bool) -> dict:
        headers = {"Accept": "application/json"}
        if jwt:
            headers["Authorization"] = f"Bearer {jwt}"
        if service and self._service_token:
            headers["X-Service-Token"] = self._service_token
        return headers

    @staticmethod
    def _unwrap(response: httpx.Response) -> dict:
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            logger.warning("Backend %s %s -> %s", response.request.method, response.url, response.status_code)
            raise BackendError(response.status_code, str(detail))
        if not response.content:
            return {}
        return response.json()
