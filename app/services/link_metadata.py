"""Fetch a preview image for a link-based idea.

Given a URL, this module fetches the page HTML, looks for a relevant
preview image (Open Graph / Twitter card meta tags, falling back to the
first reasonably sized <img> on the page), downloads that image, and
stores it under the app's local uploads directory so it is served the
same way manually-uploaded images are (via the /uploads static mount).
"""

import logging
import mimetypes
import os
import uuid
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 5.0
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB
USER_AGENT = (
    "Mozilla/5.0 (compatible; LevenBot/1.0; +https://example.com/bot)"
)

_ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
}

_META_IMAGE_PROPERTIES = [
    ("meta", {"property": "og:image:secure_url"}),
    ("meta", {"property": "og:image"}),
    ("meta", {"name": "og:image"}),
    ("meta", {"name": "twitter:image"}),
    ("meta", {"property": "twitter:image"}),
    ("link", {"rel": "image_src"}),
]


def _extract_image_url(html: str, base_url: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")

    for tag_name, attrs in _META_IMAGE_PROPERTIES:
        tag = soup.find(tag_name, attrs=attrs)
        if tag:
            content = tag.get("content") or tag.get("href")
            if content:
                return urljoin(base_url, content.strip())

    # Fallback: first <img> with a src attribute.
    img = soup.find("img", src=True)
    if img:
        return urljoin(base_url, img["src"].strip())

    return None


def _download_image(client: httpx.Client, image_url: str) -> Optional[str]:
    """Download image_url and save it to the uploads dir. Returns local
    '/uploads/<name>' path, or None on failure."""
    try:
        resp = client.get(image_url, follow_redirects=True, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.info("Failed to download link preview image %s: %s", image_url, exc)
        return None

    content_type = resp.headers.get("content-type", "").split(";")[0].strip().lower()
    ext = _ALLOWED_IMAGE_CONTENT_TYPES.get(content_type)
    if not ext:
        # Try to guess from URL path as a fallback.
        guessed_ext = os.path.splitext(urlparse(image_url).path)[1].lstrip(".").lower()
        if guessed_ext in {"jpg", "jpeg", "png", "gif", "webp"}:
            ext = "jpg" if guessed_ext == "jpeg" else guessed_ext
        else:
            logger.info("Unsupported content-type for link preview image: %s", content_type)
            return None

    content = resp.content
    if not content or len(content) > MAX_IMAGE_BYTES:
        return None

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)

    return f"/uploads/{filename}"


def fetch_link_preview_image(url: str) -> Optional[str]:
    """Best-effort fetch of a representative preview image for `url`.

    Returns a local '/uploads/<file>' URL on success, or None if no
    image could be found/downloaded. Never raises - all errors are
    swallowed and logged, since this is a non-critical enhancement to
    idea creation.
    """
    if not url:
        return None

    try:
        with httpx.Client(
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            timeout=REQUEST_TIMEOUT,
        ) as client:
            try:
                resp = client.get(url)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.info("Failed to fetch link %s: %s", url, exc)
                return None

            content_type = resp.headers.get("content-type", "")
            if "text/html" not in content_type:
                return None

            image_url = _extract_image_url(resp.text, str(resp.url))
            if not image_url:
                return None

            return _download_image(client, image_url)
    except Exception:  # noqa: BLE001 - never let preview fetching break idea creation
        logger.exception("Unexpected error fetching link preview for %s", url)
        return None
