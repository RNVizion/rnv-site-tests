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
| Nothing scrolls sideways on a phone | Chrome's mobile emulation at 390 px wide; the page may not be wider than the screen |

**Page objects** (`pages.py`) hold how to find things; the tests hold what to check. **Site facts** (`site_facts.py`) hold the few values a person decided, in one place. **Nothing is counted by hand:** links are found by walking the site, so a new post is covered the day it ships.

## How it proves it can fail

- **A positive control:** a page that must not exist has to come back 404. If it doesn't, the link checker is blind and a green run means nothing.
- **Harness tests:** the link filter is held to cases worked by hand, with no browser and no network.
- **Sabotage runs:** Actions → *site tests* → *Run workflow*, and put a title the site doesn't have in **expect_title**. The run must go red, and the failed test's screenshot and HTML are attached to the run.
- **Evidence on failure:** every failed browser test saves a screenshot and the page source to `artifacts/`, which the workflow uploads.

## Run it on your machine

Needs Python 3.13 and Google Chrome. Selenium finds a matching ChromeDriver by itself.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -v                                  # against rnvizion.dev
python -m pytest -v --base-url http://localhost:8000  # against a local copy of the site
```

## What it doesn't check

How the pages look, beyond fitting the screen; external links (other people's sites go down for their own reasons); the Ask the Corpus demo, which runs on Hugging Face, not on this site; and anything behind a login.
