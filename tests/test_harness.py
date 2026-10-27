"""The suite's own logic, tested without a browser or a network.

If the link filter is wrong, the link test can pass while checking the wrong
links, so the filter is held to cases worked by hand.
"""
from pages import internal_links, same_site

BASE = "https://rnvizion.dev"


def test_same_site_ignores_www_and_case():
    assert same_site("https://WWW.rnvizion.dev/bio/", BASE)
    assert not same_site("https://github.com/RNVizion", BASE)


def test_internal_links_keeps_own_pages_once_in_order():
    hrefs = [
        "https://rnvizion.dev/bio/",
        "https://rnvizion.dev/bio/#top",      # same page, fragment dropped
        "https://rnvizion.dev/card/",
        "https://rnvizion.dev/bio/",           # duplicate
    ]
    assert internal_links(hrefs, BASE) == ["https://rnvizion.dev/bio/", "https://rnvizion.dev/card/"]


def test_internal_links_drops_other_hosts_and_non_web_schemes():
    hrefs = [
        "https://github.com/RNVizion",
        "mailto:someone@example.com",
        "tel:+15555550100",
        "javascript:void(0)",
        None,
        "",
    ]
    assert internal_links(hrefs, BASE) == []
