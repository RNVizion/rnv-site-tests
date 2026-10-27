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

# The brand name every page title carries.
EXPECT_TITLE = os.environ.get("EXPECT_TITLE") or "RNVizion"

# The handoff card. Its contact values belong to profile.json in rnv-brand, so
# the tests check that a phone link and an email link exist, never the values.
CARD_PATH = "/card/"

# Pages the browser tests open by name. Everything else is found by walking links.
NAMED_PAGES = ["/", CARD_PATH]

# A path that must not exist. The link checker's positive control: if this does
# not come back 404, the checker cannot see a broken link either.
MISSING_PATH = "/rnv-site-tests-this-page-must-not-exist/"

# Console errors the site is allowed to have, as substrings of the message.
# Empty until a first run shows a third-party error worth tolerating; each entry
# gets a comment saying why.
ALLOWED_CONSOLE_ERRORS: list[str] = []

# A phone-sized viewport for the layout tests (an iPhone 15's CSS pixels).
PHONE = {"width": 390, "height": 844, "pixelRatio": 3.0}
