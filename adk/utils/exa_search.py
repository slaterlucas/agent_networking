from __future__ import annotations

import os
import typing as t
import requests
from datetime import datetime

EXA_API_KEY = os.getenv("EXA_API_KEY")

if not EXA_API_KEY:
    raise RuntimeError(
        "EXA_API_KEY environment variable not set. Please add it to your .env file."
    )


def exa_search(
    query: str,
    *,
    num_results: int = 10,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    start_published_date: str | None = None,
    text: bool = False,
) -> list[dict]:
    """Thin wrapper around Exa /search (see https://exa.ai/docs)."""

    body: dict[str, t.Any] = {
        "query": query,
        "numResults": num_results,
    }
    if include_domains:
        body["includeDomains"] = include_domains
    if exclude_domains:
        body["excludeDomains"] = exclude_domains
    if start_published_date is None:
        # Only recent pages (last 2 years) as a fallback
        start_published_date = (
            datetime.utcnow().replace(year=datetime.utcnow().year - 2).isoformat() + "Z"
        )
    body["startPublishedDate"] = start_published_date
    if text:
        body["text"] = True

    resp = requests.post(
        "https://api.exa.ai/search",
        headers={
            "x-api-key": EXA_API_KEY,
            "Content-Type": "application/json",
        },
        json=body,
        timeout=20,
    )
    resp.raise_for_status()

    return [
        {
            "title": r["title"],
            "url": r["url"],
            "snippet": r.get("text", "")[:280] if text else "",
        }
        for r in resp.json()["results"]
    ] 