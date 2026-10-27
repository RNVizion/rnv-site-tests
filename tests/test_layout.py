"""The named pages fit a phone screen: nothing makes the page scroll sideways."""
import pytest

import site_facts
from pages import HomePage, Page

pytestmark = pytest.mark.browser


@pytest.mark.parametrize("path", site_facts.NAMED_PAGES)
def test_no_sideways_scroll_on_a_phone(phone, base_url, path):
    page = Page(phone, base_url, path).open()
    overflow = page.horizontal_overflow()
    assert overflow <= 0, f"{path} is {overflow}px wider than a {site_facts.PHONE['width']}px screen"


def test_navigation_reachable_on_a_phone(phone, base_url):
    home = HomePage(phone, base_url).open()
    assert home.nav_links(), "no visible navigation links at phone width"
