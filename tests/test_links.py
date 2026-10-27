"""No internal link is broken. Links are found by walking the site, never listed by hand.

Selenium finds the links the way a visitor's browser renders them; requests then
reads each one's HTTP status, which a browser does not expose.
"""
import pytest
import requests

import site_facts
from pages import Page

pytestmark = pytest.mark.browser

HEADERS = {"User-Agent": "rnv-site-tests (+https://github.com/RNVizion)"}


def status_of(url: str) -> int:
    return requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True).status_code


def test_positive_control_a_missing_page_reads_404(base_url):
    """If this fails, the checker cannot see a broken link, so a green run below means nothing."""
    assert status_of(base_url + site_facts.MISSING_PATH) == 404


def test_every_internal_link_resolves(driver, base_url):
    found: list[str] = []
    for path in site_facts.NAMED_PAGES:
        found += Page(driver, base_url, path).open().internal_links()
    links = list(dict.fromkeys(found))
    assert links, "found no internal links at all, so the walk itself is broken"

    broken = []
    for url in links:
        try:
            code = status_of(url)
        except requests.RequestException as exc:
            broken.append(f"{url} -> {type(exc).__name__}")
            continue
        if code >= 400:
            broken.append(f"{url} -> {code}")
    assert not broken, f"{len(broken)} of {len(links)} internal links broken:\n" + "\n".join(broken)
