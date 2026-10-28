"""The RNVizion mark renders in the face and weight the brand register names.

Moved here from rnv-monitors' Checkly check (2026-10-27). Why it exists: on
2026-09-28 a check of /aiii/ passed with no fonts loaded at all, because
document.fonts.check() answers true for a face nobody declared. So each step
below can fail on its own, for its own reason:

  1. asks    the mark's computed style asks for the register's face and weight
  2. loads   the page declares a face of that family and weight, and one loads
  3. paints  Chrome reports it drew the mark's glyphs with that downloaded face

The face and weight come from rnv-brand's TYPE["mark"], pinned in requirements.txt,
never typed here: when the register changes, the expectation moves with it.

Break it on purpose: run the workflow by hand with block_fonts set. Chrome then
refuses the site's own font folder and step 2 must fail. A separate test proves
every mark page still requests that folder, so the sabotage cannot go stale
without a failure saying so.
"""
import pytest
from selenium.webdriver.support.ui import WebDriverWait

import site_facts
from engine.brand import TYPE
from pages import Page

pytestmark = pytest.mark.browser

MARK = TYPE["mark"]
FAMILY = MARK["family"]
WEIGHTS = {str(w) for w in MARK["weights"]}


def open_mark_page(driver, base_url, path) -> Page:
    page = Page(driver, base_url, path)
    if site_facts.BLOCK_FONTS:
        page.block_urls([f"*{site_facts.FONT_FILES}*"])
    return page.open()


@pytest.mark.parametrize("path", site_facts.MARK_PAGES)
def test_sabotage_target_is_live(driver, base_url, path):
    """The font sabotage blocks FONT_FILES; it proves nothing unless the page requests them."""
    page = Page(driver, base_url, path).open()
    hrefs = page.stylesheet_hrefs()
    assert any(site_facts.FONT_FILES in h for h in hrefs), (
        f"{path} no longer loads a stylesheet from {site_facts.FONT_FILES}, so the font "
        f"sabotage would block nothing. Stylesheets: {hrefs}"
    )


@pytest.mark.parametrize("path", site_facts.MARK_PAGES)
def test_mark_renders_in_the_register_face(driver, base_url, path):
    page = open_mark_page(driver, base_url, path)
    sel = site_facts.MARK_SELECTOR

    # 1. asks
    style = page.computed_font(sel)
    assert style["family"] == FAMILY, f"step 1: the mark asks for {style['declared']!r}, not {FAMILY}"
    assert style["weight"] in WEIGHTS, f"step 1: the mark's weight is {style['weight']}, not one of {sorted(WEIGHTS)}"
    weight = style["weight"]

    # 2. loads
    wait = WebDriverWait(driver, 10, poll_frequency=0.25)
    try:
        wait.until(lambda d: page.face_statuses(FAMILY, weight))
    except Exception:
        pytest.fail(f"step 2: the page declares no {FAMILY} {weight} face")
    try:
        wait.until(lambda d: "loaded" in page.face_statuses(FAMILY, weight))
    except Exception:
        pytest.fail(f"step 2: no {FAMILY} {weight} face finished loading: {page.face_statuses(FAMILY, weight)}")

    # 3. paints
    fonts = page.painted_fonts(sel)
    painted = [f"{f['familyName']} ({'downloaded' if f['isCustomFont'] else 'system'})" for f in fonts]
    assert fonts, "step 3: Chrome reports no font for the mark"
    assert all(f["isCustomFont"] and FAMILY.lower() in f["familyName"].lower() for f in fonts), (
        f"step 3: Chrome drew the mark with {', '.join(painted)}"
    )
