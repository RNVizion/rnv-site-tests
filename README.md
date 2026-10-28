# rnv-site-tests

Browser tests for [rnvizion.dev](https://rnvizion.dev), written in Python with Selenium WebDriver and pytest, run in GitHub Actions on every push, every pull request, every Monday, and on demand.

## What it checks

| Check | How |
|---|---|
| The home page’s title is what the site decided | Selenium reads the rendered title |
| The navigation is visible and every link is labeled | Selenium finds the nav links, checks each has text or an `aria-label` |
| The contact card offers a phone link and an email link | Selenium looks for `tel:` and `mailto:` links. The values belong to the brand manifest, so the test never copies them |
| No internal link is broken | Selenium walks the links a visitor would see; `requests` reads each one's HTTP status, which a browser doesn't expose |
| No unexpected errors in the browser console | Chrome's console log, read through WebDriver |
| Every image has alt text | Every `<img>` must carry an `alt` attribute (`alt=""` is allowed for decoration) |
| The RNVizion mark renders in Montserrat 900 on `/` and `/aiii/` | Three steps that each fail on their own: the CSS asks for the face, a face of that family and weight loads, and Chrome reports (through the DevTools Protocol) that it drew the mark with that downloaded file. The face and weight are read from `rnv-brand`'s `TYPE["mark"]`, never typed |
| Nothing scrolls sideways on a phone | Chrome's mobile emulation at 390 px wide; the page may not be wider than the screen |

**Page objects** (`pages.py`) hold how to find things; the tests hold what to check. **Site facts** (`site_facts.py`) hold the few values a person decided, in one place. **Nothing is counted by hand:** links are found by walking the site, so a new post is covered the day it ships.

## How it proves it can fail

- **A positive control:** a page that must not exist has to come back 404. If it doesn't, the link checker is blind and a green run means nothing.
- **Harness tests:** the link filter is held to cases worked by hand, with no browser and no network.
- **Sabotage runs:** Actions → *site tests* → *Run workflow*, and put a title the site doesn't have in **expect_title**. The run must go red, and the failed test's screenshot and HTML are attached to the run.
- **A font sabotage run:** *Run workflow* with **block_fonts** ticked. Chrome refuses the site's own `/assets/webfonts/` folder, and the mark check must fail at step 2. `test_sabotage_target_is_live` proves every mark page still requests that folder, so the sabotage can't quietly start blocking nothing.
- **Evidence on failure:** every failed browser test saves a screenshot and the page source to `artifacts/`, which the workflow uploads.

## Run it on your machine

Needs Python 3.13 and Google Chrome. Selenium finds a matching ChromeDriver by itself.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt   # includes rnv-brand, pinned by commit
python -m pytest -v                                  # against rnvizion.dev
python -m pytest -v --base-url http://localhost:8000  # against a local copy of the site
```

## The mark check's history

It began as a Checkly browser check in `rnv-monitors` (September 2026) and moved here on 2026-10-27, so the repo that checks whether the site is *right* holds every correctness check and `rnv-monitors` checks only whether things *answer*. Two lessons came with it:

- **2026-09-28:** a weaker check of `/aiii/` passed with no fonts loaded at all. `document.fonts.check()` answers true for a face nobody declared, which is why this check asks three separate questions.
- **2026-10-27:** the Checkly version's sabotage blocked Google Fonts, but the site had moved to serving its own fonts, so the sabotage blocked nothing and would have passed. Nothing reported it. Here a test fails the day the sabotage target goes stale.

Proved before it moved, against a local copy of the site at `rnvizion.github.io@b798f55`: the normal run passes; blocking the font folder fails at step 2; the mark's CSS switched to another family fails at step 1; Inter served under Montserrat's name fails at step 3, with Chrome reporting it drew Inter; and the font stylesheet removed fails the target test.

## Known gaps it tracks

**No favicon (Brand Book §9, OPEN).** The first run found every page asking for `/favicon.ico` and getting a 404, the same gap the Brand Book had recorded by hand. Until the icon is designed, that one console message is allowed in `site_facts.py`, and `test_site_serves_a_favicon` is a strict expected failure: the day the icon goes live, it turns the run red so the allowance gets removed instead of forgotten.

## What it doesn't check

How the pages look, beyond fitting the screen; external links (other people's sites go down for their own reasons); the Ask the Corpus demo, which runs on Hugging Face, not on this site; and anything behind a login.
