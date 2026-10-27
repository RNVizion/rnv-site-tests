"""What the tests expect of the live site.

Every value here is a fact about rnvizion.dev that a person decided, so it lives
in one file instead of being scattered through the tests. Anything that changes
when a post ships (page counts, link counts) is never written here: the tests
discover those by walking the site.

EXPECT_TITLE can be overridden from the workflow's manual run. That is the
sabotage switch: run it with a title the site does not have, and the suite must
go red with a screenshot.
"""
import os

# What the home page's title carries. The site titles its home page with the
# personal layer, "Christian Smith: AI Engineer & Developer" (read by the first
# CI run, 2026-10-27); the first draft of this file guessed "RNVizion" and was wrong.
EXPECT_TITLE = os.environ.get("EXPECT_TITLE") or "Christian Smith"

# The handoff card. Its contact values belong to profile.json in rnv-brand, so
# the tests check that a phone link and an email link exist, never the values.
CARD_PATH = "/card/"

# Pages the browser tests open by name. Everything else is found by walking links.
NAMED_PAGES = ["/", CARD_PATH]

# A path that must not exist. The link checker's positive control: if this does
# not come back 404, the checker cannot see a broken link either.
MISSING_PATH = "/rnv-site-tests-this-page-must-not-exist/"

# Console errors the site is allowed to have, as substrings of the message.
# Each entry says why it is allowed and what removes it.
ALLOWED_CONSOLE_ERRORS: list[str] = [
    # The site has no favicon yet, so every page's request for /favicon.ico gets
    # a 404. Brand Book §9 records the gap as OPEN: the mark is a design decision.
    # tests/test_links.py::test_site_serves_a_favicon is a strict xfail that turns
    # the run red the day /favicon.ico is served. Remove this entry and that marker then.
    "/favicon.ico - Failed to load resource",
]

# A phone-sized viewport for the layout tests (an iPhone 15's CSS pixels).
PHONE = {"width": 390, "height": 844, "pixelRatio": 3.0}
