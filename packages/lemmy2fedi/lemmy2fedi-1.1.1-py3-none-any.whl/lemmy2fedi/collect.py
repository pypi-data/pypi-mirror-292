"""Methods to collect information from Lemmy Instances."""

from hashlib import sha256
from typing import Any

import httpx
import msgspec.json
import stamina
from httpx import AsyncClient
from loguru import logger as log
from minimal_activitypub import Status
from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import NetworkError


@stamina.retry(on=(httpx.ConnectError, httpx.HTTPError), attempts=3)
async def read_community(instance: str, name: str, client: AsyncClient, sort: str = "Hot", limit: int = 10) -> Any:
    """Read lemmy community posts with sort on Hot."""
    url = f"https://{instance}/api/v3/post/list?limit={limit}&sort={sort}&community_name={name}"
    response = await client.get(url=url)
    log.debug(f"{instance}/c/{name} - {response.status_code} - {response.headers=}")
    response.raise_for_status()

    msgspec_response = msgspec.json.decode(response.content)

    return msgspec_response


@stamina.retry(on=NetworkError, attempts=3)
async def read_home_timeline(instance: ActivityPub, after_id: str) -> list[Status]:
    """Read public timeline."""
    timeline: list[Status] = await instance.get_home_timeline(min_id=after_id)

    return timeline


async def determine_attachment_hash(url: str, client: AsyncClient) -> str:
    """Determine attachment hash."""
    response = await client.get(url=url)
    url_hash = sha256(response.content).hexdigest()
    return url_hash
