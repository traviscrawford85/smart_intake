"""
Clio API helper functions for rate limiting and pagination.
"""

import asyncio
import importlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import httpx

try:
    config_module = importlib.import_module("app.config")
    loaded_settings = getattr(config_module, "settings", None)
    if loaded_settings is not None and hasattr(loaded_settings, "CLIO_ACCESS_TOKEN"):

        class SafeSettings:
            CLIO_ACCESS_TOKEN = getattr(loaded_settings, "CLIO_ACCESS_TOKEN")

        settings = SafeSettings()
    else:
        raise AttributeError
except (ImportError, ModuleNotFoundError, AttributeError):
    # Fallback: define a dummy settings object for development/testing
    class DummySettings:
        CLIO_ACCESS_TOKEN = "your-access-token"

    settings = DummySettings()


@dataclass
class RateLimit:
    """Rate limit configuration for Clio API."""

    max_requests: int = 100  # Max requests per window
    window_seconds: int = 60  # Time window in seconds
    current_requests: int = 0
    window_start: Optional[datetime] = None

    def __post_init__(self):
        if self.window_start is None:
            self.window_start = datetime.utcnow()

    def can_make_request(self) -> bool:
        """Check if we can make a request within rate limits."""
        now = datetime.utcnow()

        # Reset window if expired
        if self.window_start is not None and (
            now - self.window_start >= timedelta(seconds=self.window_seconds)
        ):
            self.current_requests = 0
            self.window_start = now

        return self.current_requests < self.max_requests

    def record_request(self) -> None:
        """Record that a request was made."""
        self.current_requests += 1

    def time_until_reset(self) -> float:
        """Get seconds until rate limit window resets."""
        now = datetime.utcnow()
        if self.window_start is None:
            self.window_start = now
        reset_time = self.window_start + timedelta(seconds=self.window_seconds)
        return max(0, (reset_time - now).total_seconds())


class ClioRateLimiter:
    """Rate limiter for Clio API calls with automatic backoff."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.rate_limit = RateLimit(max_requests, window_seconds)
        self.backoff_factor = 1.5
        self.max_backoff = 60  # Max wait time in seconds

    async def wait_if_needed(self) -> None:
        """Wait if we're hitting rate limits."""
        if not self.rate_limit.can_make_request():
            wait_time = self.rate_limit.time_until_reset()
            if wait_time > 0:
                print(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
                # Reset after waiting
                self.rate_limit.current_requests = 0
                self.rate_limit.window_start = datetime.utcnow()

    async def make_request(
        self, client: httpx.AsyncClient, method: str, url: str, **kwargs
    ) -> httpx.Response:
        """Make a rate-limited request to Clio API."""
        await self.wait_if_needed()

        # Add required headers
        headers = kwargs.get("headers", {})
        headers.update(
            {
                "X-API-VERSION": "4.0.12",
                "Authorization": f"Bearer {settings.CLIO_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            }
        )
        kwargs["headers"] = headers

        # Make the request
        response = await client.request(method, url, **kwargs)
        self.rate_limit.record_request()

        # Handle rate limit responses
        if response.status_code == 429:  # Too Many Requests
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited by server. Waiting {retry_after} seconds...")
            await asyncio.sleep(retry_after)
            # Retry the request
            return await self.make_request(client, method, url, **kwargs)

        return response


@dataclass
class PaginationInfo:
    """Pagination information for Clio API responses."""

    current_page: int = 1
    per_page: int = 50
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    has_next: bool = False
    has_prev: bool = False

    @classmethod
    def from_response_headers(cls, headers: Dict[str, str]) -> "PaginationInfo":
        """Create pagination info from response headers."""
        return cls(
            current_page=int(headers.get("X-Current-Page", 1)),
            per_page=int(headers.get("X-Per-Page", 50)),
            total_count=(
                int(headers.get("X-Total-Count", 0))
                if headers.get("X-Total-Count")
                else None
            ),
            total_pages=(
                int(headers.get("X-Total-Pages", 1))
                if headers.get("X-Total-Pages")
                else None
            ),
            has_next=headers.get("X-Has-Next-Page", "false").lower() == "true",
            has_prev=headers.get("X-Has-Previous-Page", "false").lower() == "true",
        )


class ClioPaginator:
    """Helper for paginating through Clio API responses."""

    def __init__(self, rate_limiter: ClioRateLimiter, per_page: int = 50):
        self.rate_limiter = rate_limiter
        self.per_page = per_page

    async def paginate_all(
        self, client: httpx.AsyncClient, url: str, method: str = "GET", **kwargs
    ) -> AsyncGenerator[Tuple[List[Dict[str, Any]], PaginationInfo], None]:
        """
        Paginate through all pages of a Clio API endpoint.

        Yields:
            Tuple of (data_list, pagination_info) for each page
        """
        page = 1
        has_more = True

        while has_more:
            # Add pagination parameters
            params = kwargs.get("params", {})
            params.update({"page": page, "per_page": self.per_page})
            kwargs["params"] = params

            # Make the request
            response = await self.rate_limiter.make_request(
                client, method, url, **kwargs
            )
            response.raise_for_status()

            # Parse response
            data = response.json()
            pagination = PaginationInfo.from_response_headers(dict(response.headers))

            # Extract data array (Clio typically wraps data in a "data" key)
            items = data.get("data", []) if isinstance(data, dict) else []

            yield items, pagination

            # Check if we should continue
            has_more = pagination.has_next
            page += 1

    async def get_page(
        self,
        client: httpx.AsyncClient,
        url: str,
        page: int = 1,
        per_page: Optional[int] = None,
        method: str = "GET",
        **kwargs,
    ) -> Tuple[List[Dict[str, Any]], PaginationInfo]:
        """
        Get a specific page from a Clio API endpoint.

        Returns:
            Tuple of (data_list, pagination_info)
        """
        # Set pagination parameters
        params = kwargs.get("params", {})
        params.update({"page": page, "per_page": per_page or self.per_page})
        kwargs["params"] = params

        # Make the request
        response = await self.rate_limiter.make_request(client, method, url, **kwargs)
        response.raise_for_status()

        # Parse response
        data = response.json()
        pagination = PaginationInfo.from_response_headers(dict(response.headers))

        # Extract data array
        items = data.get("data", []) if isinstance(data, dict) else []

        return items, pagination


class ClioAPIHelper:
    """High-level helper for Clio API operations with rate limiting and pagination."""

    def __init__(
        self, max_requests: int = 100, window_seconds: int = 60, per_page: int = 50
    ):
        self.rate_limiter = ClioRateLimiter(max_requests, window_seconds)
        self.paginator = ClioPaginator(self.rate_limiter, per_page)
        self.base_url = "https://app.clio.com/api/v4"

    async def get_all_contacts(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Get all contacts from Clio API."""
        all_contacts = []
        url = f"{self.base_url}/contacts"

        async for contacts, pagination in self.paginator.paginate_all(client, url):
            all_contacts.extend(contacts)
            print(
                f"Retrieved {len(contacts)} contacts (page {pagination.current_page})"
            )

        return all_contacts

    async def get_all_custom_actions(
        self, client: httpx.AsyncClient
    ) -> List[Dict[str, Any]]:
        """Get all custom actions from Clio API."""
        all_actions = []
        url = f"{self.base_url}/custom_actions"

        async for actions, pagination in self.paginator.paginate_all(client, url):
            all_actions.extend(actions)
            print(
                f"Retrieved {len(actions)} custom actions (page {pagination.current_page})"
            )

        return all_actions

    async def get_all_webhook_subscriptions(
        self, client: httpx.AsyncClient
    ) -> List[Dict[str, Any]]:
        """Get all webhook subscriptions from Clio API."""
        all_subscriptions = []
        url = f"{self.base_url}/webhook_subscriptions"

        async for subscriptions, pagination in self.paginator.paginate_all(client, url):
            all_subscriptions.extend(subscriptions)
            print(
                f"Retrieved {len(subscriptions)} webhook subscriptions (page {pagination.current_page})"
            )

        return all_subscriptions

    async def create_custom_action(
        self, client: httpx.AsyncClient, name: str, url: str, http_method: str = "GET"
    ) -> Dict[str, Any]:
        """Create a custom action in Clio."""
        api_url = f"{self.base_url}/custom_actions"
        payload = {"data": {"name": name, "http_method": http_method, "url": url}}

        response = await self.rate_limiter.make_request(
            client, "POST", api_url, json=payload
        )
        response.raise_for_status()
        return response.json()

    async def create_webhook_subscription(
        self, client: httpx.AsyncClient, url: str, events: List[str]
    ) -> Dict[str, Any]:
        """Create a webhook subscription in Clio."""
        api_url = f"{self.base_url}/webhook_subscriptions"
        payload = {"data": {"url": url, "events": events}}

        response = await self.rate_limiter.make_request(
            client, "POST", api_url, json=payload
        )
        response.raise_for_status()
        return response.json()


# Global helper instance
clio_api_helper = ClioAPIHelper()
