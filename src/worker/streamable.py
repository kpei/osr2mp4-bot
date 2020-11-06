import logging
import os

from datetime import timedelta
from pathlib import Path

import requests

from . import ReplyWith
from ..common import enqueue


def upload(video: Path, title: str) -> str:
    """Upload `video` to Streamable."""
    # We're not actually uploading the file ourselves,
    # just supplying a URL where it can find the video file.
    # It's assumed that `video` is available at $SERVER_ADDR.
    # Docker Compose handles this, provided that $SERVER_ADDR is publically accessible.
    # This technique comes from: https://github.com/adrielcafe/AndroidStreamable
    auth = os.environ["STREAMABLE_USERNAME"], os.environ["STREAMABLE_PASSWORD"]
    source_url = f"{os.environ['SERVER_ADDR']}/{video.name}"
    params = {"url": source_url, "title": title}
    resp = requests.get("https://api.streamable.com/import", auth=auth, params=params)
    # If we do something wrong, we still get a 200, but it's an HTML page.
    if resp.headers["Content-Type"] != "application/json":
        raise ReplyWith("Sorry, uploading to Streamable failed.")
    shortcode = resp.json()["shortcode"]
    # Because the response comes before the upload is actually finished,
    # we can't delete the video file yet, although we need to eventually.
    # Create a new job that handles that at some point in the future.
    enqueue(_wait, shortcode, video)
    return f"https://streamable.com/{shortcode}"


def _wait(shortcode: str, video: Path) -> None:
    """Wait for the video with `shortcode` to be uploaded, then delete `video`."""
    resp = requests.get(f"https://api.streamable.com/videos/{shortcode}")
    if not resp.ok:
        logging.warning("Retrieving video failed")
    status = resp.json()["status"]
    if status in [0, 1]:
        # Still in progress, so run this function again in a while.
        # In the meantime, exit so that the worker gets freed up.
        enqueue(_wait, shortcode, video, wait=timedelta(seconds=30))
    elif status == 2:
        # Upload is finished, we can delete the local file now.
        video.unlink()
    else:
        # If this happens too much, then we'll run out of disk space.
        logging.warning(f"Status {status} from Streamable ({shortcode} {video})")
