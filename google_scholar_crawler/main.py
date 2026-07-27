"""Fetch public citation data from a Google Scholar author profile."""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup


PROFILE_URL = "https://scholar.google.com/citations"
OUTPUT_DIR = Path(__file__).resolve().parent / "results"
REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    ),
}


class ScholarFetchError(RuntimeError):
    """Raised when Google Scholar does not return a usable author profile."""


def parse_number(value: str) -> int:
    digits = re.sub(r"[^\d]", "", value)
    if not digits:
        return 0
    return int(digits)


def fetch_profile_html(scholar_id: str, attempts: int = 3) -> str:
    params = {
        "user": scholar_id,
        "hl": "en",
        "pagesize": "100",
    }
    last_error = None

    with requests.Session() as session:
        for attempt in range(1, attempts + 1):
            try:
                response = session.get(
                    PROFILE_URL,
                    params=params,
                    headers=REQUEST_HEADERS,
                    timeout=30,
                )
                response.raise_for_status()

                if "gsc_prf_in" not in response.text:
                    raise ScholarFetchError(
                        "Google Scholar returned a challenge or an incomplete profile page"
                    )

                return response.text
            except (requests.RequestException, ScholarFetchError) as error:
                last_error = error
                if attempt < attempts:
                    time.sleep(2**attempt)

    raise ScholarFetchError(
        f"Unable to fetch Google Scholar profile after {attempts} attempts: {last_error}"
    )


def parse_publications(soup: BeautifulSoup) -> dict[str, dict]:
    publications: dict[str, dict] = {}

    for row in soup.select("tr.gsc_a_tr"):
        title_link = row.select_one("a.gsc_a_at")
        if title_link is None:
            continue

        query = parse_qs(urlparse(title_link.get("href", "")).query)
        publication_id = query.get("citation_for_view", [None])[0]
        if not publication_id:
            continue

        metadata = row.select(".gs_gray")
        citation_link = row.select_one(".gsc_a_ac")
        year_element = row.select_one(".gsc_a_y span")
        year = year_element.get_text(strip=True) if year_element else ""

        publications[publication_id] = {
            "author_pub_id": publication_id,
            "bib": {
                "title": title_link.get_text(" ", strip=True),
                "author": metadata[0].get_text(" ", strip=True) if metadata else "",
                "citation": (
                    metadata[1].get_text(" ", strip=True)
                    if len(metadata) > 1
                    else ""
                ),
                "pub_year": year,
            },
            "num_citations": (
                parse_number(citation_link.get_text(strip=True))
                if citation_link
                else 0
            ),
        }

    return publications


def parse_profile(html: str, scholar_id: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    name_element = soup.select_one("#gsc_prf_in")
    statistics = soup.select("#gsc_rsb_st td.gsc_rsb_std")

    if name_element is None:
        raise ScholarFetchError("Google Scholar profile name was not found")
    if not statistics:
        raise ScholarFetchError("Google Scholar citation statistics were not found")

    return {
        "name": name_element.get_text(" ", strip=True),
        "scholar_id": scholar_id,
        "citedby": parse_number(statistics[0].get_text(strip=True)),
        "updated": datetime.now(timezone.utc).isoformat(),
        "publications": parse_publications(soup),
    }


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    scholar_id = os.environ.get("GOOGLE_SCHOLAR_ID", "").strip()
    if not scholar_id:
        raise SystemExit("GOOGLE_SCHOLAR_ID is required")

    profile = parse_profile(fetch_profile_html(scholar_id), scholar_id)
    if profile["citedby"] <= 0:
        raise ScholarFetchError("Citation count is missing or invalid")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "gs_data.json", profile)
    write_json(
        OUTPUT_DIR / "gs_data_shieldsio.json",
        {
            "schemaVersion": 1,
            "label": "citations",
            "message": str(profile["citedby"]),
        },
    )

    print(
        f"Fetched {profile['citedby']} citations and "
        f"{len(profile['publications'])} publications for {profile['name']}."
    )


if __name__ == "__main__":
    main()
