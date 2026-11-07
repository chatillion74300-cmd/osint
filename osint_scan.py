#!/usr/bin/env python3
"""Check whether a username's public profile URL appears to exist on selected sites.

This is a small, passive checker: it makes one ordinary HTTPS request per site,
checks only HTTP status codes, and does not sign in, scrape page contents, or
attempt to bypass site protections. Results are indicative, not definitive.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Site:
    name: str
    profile_url: str


SITES = (
    Site("GitHub", "https://github.com/{username}"),
    Site("GitLab", "https://gitlab.com/{username}"),
    Site("Reddit", "https://www.reddit.com/user/{username}/"),
    Site("X", "https://x.com/{username}"),
    Site("Instagram", "https://www.instagram.com/{username}/"),
)
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,30}$")
USER_AGENT = "UsernameProfileChecker/1.0 (single-user, low-rate public URL check)"
REQUEST_TIMEOUT = 10
DELAY_SECONDS = 1.5


def check_profile(site: Site, username: str) -> tuple[str, str]:
    """Return a conservative status and profile URL for one site."""
    url = site.profile_url.format(username=username)
    request = Request(url, headers={"User-Agent": USER_AGENT}, method="GET")

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            code = response.status
    except HTTPError as error:
        code = error.code
    except (URLError, TimeoutError, OSError) as error:
        return f"unavailable ({error})", url

    if code == 404:
        return "not found (HTTP 404)", url
    if 200 <= code < 300:
        return "possibly found (HTTP 2xx; verify manually)", url
    if code in (401, 403, 429):
        return f"inconclusive (HTTP {code}; site restricted or rate-limited)", url
    if 300 <= code < 400:
        return f"inconclusive (redirect, HTTP {code})", url
    return f"inconclusive (HTTP {code})", url


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check public profile URLs for one username on a small set of sites."
    )
    parser.add_argument("username", help="one username to check (no bulk lists)")
    args = parser.parse_args()

    if not USERNAME_RE.fullmatch(args.username):
        parser.error("username must be 1–30 characters: letters, digits, dot, underscore, or hyphen")

    print(f"Checking public profile URLs for {args.username!r}. Results can be inconclusive.\n")
    for index, site in enumerate(SITES):
        status, url = check_profile(site, args.username)
        print(f"{site.name:10} {status}\n           {url}")
        if index < len(SITES) - 1:
            time.sleep(DELAY_SECONDS)

    print("\nRespect each site's terms and robots/rate-limit guidance. Verify results manually.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        raise SystemExit(130)
