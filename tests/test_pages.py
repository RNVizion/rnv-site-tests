"""The named pages load and carry what a visitor needs."""
import pytest

import site_facts
from pages import CardPage, HomePage, Page

pytestmark = pytest.mark.browser


def test_home_title_matches_site_facts(driver, base_url):
    home = HomePage(driver, base_url).open()
    assert site_facts.EXPECT_TITLE in home.title, f"title was {home.title!r}"


def test_home_has_visible_navigation(driver, base_url):
    home = HomePage(driver, base_url).open()
    links = home.nav_links()
    assert len(links) >= 2, f"found {len(links)} visible navigation links"
    unlabeled = [a.get_attribute("href") for a in links if not (a.text.strip() or a.get_attribute("aria-label"))]
    assert not unlabeled, f"navigation links with no text or aria-label: {unlabeled}"


def test_card_offers_a_phone_link_and_an_email_link(driver, base_url):
    card = CardPage(driver, base_url, site_facts.CARD_PATH).open()
    assert card.phone_links(), "no tel: link on the card"
    assert card.email_links(), "no mailto: link on the card"


@pytest.mark.parametrize("path", site_facts.NAMED_PAGES)
def test_no_unexpected_console_errors(driver, base_url, path):
    page = Page(driver, base_url, path).open()
    errors = page.console_errors(site_facts.ALLOWED_CONSOLE_ERRORS)
    assert not errors, "console errors:\n" + "\n".join(errors)


@pytest.mark.parametrize("path", site_facts.NAMED_PAGES)
def test_every_image_has_alt_text(driver, base_url, path):
    page = Page(driver, base_url, path).open()
    missing = page.images_missing_alt()
    assert not missing, f"images with no alt attribute: {missing}"
