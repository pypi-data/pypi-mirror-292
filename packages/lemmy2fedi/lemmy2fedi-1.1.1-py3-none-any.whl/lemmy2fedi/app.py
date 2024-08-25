"""High level logic for lemmy2feed."""

import asyncio
import sys
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Optional

import httpx
import msgspec.toml
import stamina
import typer
from httpx import AsyncClient
from loguru import logger as log
from minimal_activitypub import Status
from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import NetworkError

from lemmy2fedi import __version__
from lemmy2fedi.collect import determine_attachment_hash
from lemmy2fedi.collect import read_community
from lemmy2fedi.collect import read_home_timeline
from lemmy2fedi.config import Configuration
from lemmy2fedi.config import create_default_config
from lemmy2fedi.control import PostRecorder
from lemmy2fedi.publish import connect
from lemmy2fedi.publish import cross_post
from lemmy2fedi.publish import post_media

logging_config_path = Path("logging-config.toml")
if logging_config_path.exists():
    with logging_config_path.open(mode="rb") as log_config_file:
        logging_config = msgspec.toml.decode(log_config_file.read())

    for handler in logging_config.get("handlers"):
        if handler.get("sink") == "sys.stdout":
            handler["sink"] = sys.stdout

    log.configure(**logging_config)

stamina.instrumentation.set_on_retry_hooks([])


@log.catch
async def main(config_path: Path, max_posts: int | None) -> None:
    """Read communities and post to fediverse account."""
    log.info(f"Welcome to Lemmy2Fedi({__version__})")

    if config_path.exists():
        with config_path.open(mode="rb") as config_file:
            config_content = config_file.read()
            config = msgspec.toml.decode(config_content, type=Configuration)

    else:
        config = await create_default_config()
        with config_path.open(mode="wb") as config_file:
            config_file.write(msgspec.toml.encode(config))
        print("Please review your config file, adjust as needed, and run lemmy2fedi again.")
        sys.exit(0)

    async with AsyncClient(http2=True, timeout=30) as client:
        try:
            instance: ActivityPub
            my_username: str
            instance, my_username = await connect(auth=config.fediverse, client=client)
        except NetworkError as error:
            log.info(f"Unable to connect to your Fediverse account with {error=}")
            log.opt(colors=True).info("<red><bold>Can't continue!</bold></red> ... Exiting")
            sys.exit(1)

        with PostRecorder(history_db_path=config.history_db_path) as recorder:
            statuses_posted: int = 0
            while True:
                for _i in range(config.max_crossposts):
                    await cross_post_lemmy(
                        client=client,
                        config=config,
                        instance=instance,
                        recorder=recorder,
                    )
                    statuses_posted += 1
                    if max_posts and (statuses_posted >= max_posts):
                        break

                # Boost timeline posts
                if max_reblogs := config.fediverse.max_reblog:
                    try:
                        await boost_home_timeline(
                            instance=instance,
                            my_username=my_username,
                            recorder=recorder,
                            max_boosts=max_reblogs,
                            no_reblog_tags=config.fediverse.no_reblog_tags,
                            post_recorder=recorder,
                            client=client,
                        )
                    except NetworkError as error:
                        log.warning(f"We've encountered the following error when boosting statuses: {error}")

                recorder.prune(max_age_in_days=config.history_prune_age)

                if not config.run_continuously:
                    break

                if max_posts and (statuses_posted >= max_posts):
                    log.debug(f"We've created {statuses_posted} statuses. Stopping now.")
                    break

                wait_until = datetime.now(tz=UTC) + timedelta(seconds=config.delay_between_posts)
                log.opt(colors=True).info(
                    f"<dim>Waiting until {wait_until:%Y-%m-%d %H:%M:%S %z} "
                    f"({config.delay_between_posts}s) before checking again.</>"
                )
                await asyncio.sleep(delay=config.delay_between_posts)


async def cross_post_lemmy(
    client: AsyncClient,
    config: Configuration,
    instance: ActivityPub,
    recorder: PostRecorder,
) -> None:
    """Check lemmy for posts and cross post."""
    for community in config.communities:
        log.debug(f"Processing posts from {community=}")
        try:
            posts = await read_community(
                instance=community.domain_name,
                name=community.name,
                client=client,
                sort=community.sort,
                limit=community.limit,
            )
        except (httpx.ConnectError, httpx.HTTPError) as error:
            log.opt(colors=True).error(
                f"<red>Could not read community</> "
                f"<cyan>{community.domain_name}/c/{community.name}</><red> - got {error}</>"
            )
            break

        for post_dict in posts["posts"]:
            post = post_dict.get("post", {})

            if not (
                recorder.duplicate_check(identifier=post.get("id"))
                or recorder.duplicate_check(identifier=post.get("url"))
                or recorder.duplicate_check(identifier=post.get("ap_id"))
            ):
                media_id: str | None = None
                if post.get("url"):
                    media_id = await post_media(activity_pub=instance, post=post, client=client, post_recorder=recorder)

                if community.only_with_attachment and not media_id:
                    log.opt(colors=True).info(
                        f"<dim><red>Skipping</red> <cyan>{post.get('name')}</cyan> "
                        f"because it has no supported attachment - {post.get('ap_id', '')}</dim>"
                    )
                    recorder.log_post(id=post.get("id"))
                    continue

                media_ids: list[str] = []
                if media_id:
                    media_ids.append(media_id)

                await cross_post(activity_pub=instance, post=post, media_ids=media_ids, tags=community.tags)

                recorder.log_post(id=post.get("id"), url=post.get("url"), ap_id=post.get("ap_id"))

                return


async def boost_home_timeline(  # noqa: PLR0913
    instance: ActivityPub,
    my_username: str,
    recorder: PostRecorder,
    max_boosts: int,
    no_reblog_tags: list[str],
    post_recorder: PostRecorder,
    client: AsyncClient,
) -> None:
    """Boost posts on home timeline."""
    retry_caller = stamina.AsyncRetryingCaller(attempts=3)
    max_id: str = recorder.get_setting(key="max-boosted-id")

    try:
        timeline = await retry_caller(NetworkError, read_home_timeline, instance=instance, after_id=max_id)
    except NetworkError as error:
        log.opt(colors=True).info(f"<dim>encountered {error=}</dim>")
        return

    number_boosted: int = 0
    if len(timeline):
        for status in reversed(timeline):
            status_id = status.get("id")

            if skip_reblog(status=status, my_username=my_username, no_reblog_tags=no_reblog_tags):
                continue

            attachments_not_yet_boosted: bool = True
            for attachment in status.get("media_attachments", []):
                attachment_hash: str = await determine_attachment_hash(url=attachment.get("url"), client=client)
                if post_recorder.duplicate_check(attachment_hash):
                    attachments_not_yet_boosted = False
                    log.opt(colors=True).info(
                        f"<dim><red>Not Boosting:</red> At least one attachment of status at "
                        f"<cyan>{status.get('url')}</cyan> has already been boosted or posted.</dim>"
                    )
                if attachments_not_yet_boosted:
                    recorder.log_post(attachment_hash=attachment_hash)
                else:
                    break

            if attachments_not_yet_boosted:
                await retry_caller(NetworkError, instance.reblog, status_id=status_id)
                log.opt(colors=True).info(f"Boosted <cyan>{status.get('url', '')}</>")
                number_boosted += 1

            max_id = status_id

            if number_boosted >= max_boosts:
                break

        recorder.save_setting(key="max-boosted-id", value=max_id)


def skip_reblog(
    status: Status,
    my_username: str,
    no_reblog_tags: list[str],
) -> bool:
    """Check if there is at least one reason to skip re-blogging the status."""
    if status.get("account", {}).get("bot"):
        log.opt(colors=True).info(
            f"<dim><red>Not Boosting</red> <cyan>{status.get('url', '')}</cyan> because it was posted by a bot</dim>"
        )
        return True

    if my_username == status.get("account", {}).get("username"):
        log.opt(colors=True).debug(
            f"<dim><red>Skipping</red> post from myself - <cyan>{status.get('url', '')}</cyan></dim>"
        )
        return True

    if not len(status.get("media_attachments", [])):
        log.opt(colors=True).info(
            f"<dim><red>Not Boosting</red> <cyan>{status.get('url', '')}</cyan> "
            f"because it has no attachments / media</dim>"
        )
        return True

    status_tags: list[str] = [x["name"].casefold() for x in status.get("tags", [])]
    if any(no_reblog.casefold() in status_tags for no_reblog in no_reblog_tags):
        log.opt(colors=True).info(
            f"<dim><red>Not Boosting</red> <cyan>{status.get('url', '')}</cyan> "
            f"because it contains tags that are in the no_reblog_tags list</dim>"
        )
        return True

    return False


def async_shim(config_path: Path, max_posts: Optional[int] = None) -> None:
    """Start async part."""
    asyncio.run(main(config_path=config_path, max_posts=max_posts))


def typer_shim() -> None:
    """Run actual code."""
    try:
        typer.run(async_shim)
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    typer.run(async_shim)
