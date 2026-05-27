"""
hitl_search_agent.utils.image_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Image URL extraction from Tavily search results.
"""

from __future__ import annotations

from typing import Any


def extract_image_urls(raw_results: Any) -> list[str]:
    """
    Extract image URLs from Tavily results.

    Tavily responses may contain images in different shapes depending on
    package version and search options, so this function handles several
    common formats:

    1. raw_results["images"] = ["url1", "url2", ...]
    2. raw_results["images"] = [{"url": "..."}, ...]
    3. raw_results["results"][i]["image_url"]
    4. raw_results["results"][i]["images"]
    """

    image_urls: list[str] = []

    if not raw_results:
        return image_urls

    def add_image(candidate: Any) -> None:
        if isinstance(candidate, str):
            image_urls.append(candidate)
        elif isinstance(candidate, dict):
            url = (
                candidate.get("url")
                or candidate.get("image_url")
                or candidate.get("src")
            )
            if url:
                image_urls.append(url)

    if isinstance(raw_results, dict):
        top_level_images = raw_results.get("images", [])

        for image in top_level_images:
            add_image(image)

        for result in raw_results.get("results", []):
            if not isinstance(result, dict):
                continue

            add_image(result.get("image_url"))
            add_image(result.get("image"))

            for nested_image in result.get("images", []):
                add_image(nested_image)

    elif isinstance(raw_results, list):
        for item in raw_results:
            if not isinstance(item, dict):
                continue

            add_image(item.get("image_url"))
            add_image(item.get("image"))

            for nested_image in item.get("images", []):
                add_image(nested_image)

    # Remove duplicates while preserving order.
    unique_urls: list[str] = []
    seen: set[str] = set()

    for url in image_urls:
        if url and url not in seen:
            unique_urls.append(url)
            seen.add(url)

    return unique_urls
