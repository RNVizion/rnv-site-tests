"""Shared setup: the site's address, the browsers, and evidence when a test fails.

Every browser test gets a fresh headless Chrome. When one fails, a screenshot and
the page's HTML are saved to artifacts/, which the workflow uploads, so a red run
shows what the browser saw.
"""
import os
import pathlib
import re

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

import site_facts

ARTIFACTS = pathlib.Path("artifacts")


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        default=os.environ.get("SITE_URL") or "https://rnvizion.dev",
        help="Site to test (default https://rnvizion.dev, or $SITE_URL)",
    )


@pytest.fixture(scope="session")
def base_url(request) -> str:
    return request.config.getoption("--base-url").rstrip("/")


def _options() -> webdriver.ChromeOptions:
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    if os.environ.get("CHROME_BINARY"):
        opts.binary_location = os.environ["CHROME_BINARY"]
    return opts


def _start(opts):
    # Selenium Manager finds a matching driver; CHROMEDRIVER names one by hand where it can't.
    service = Service(os.environ["CHROMEDRIVER"]) if os.environ.get("CHROMEDRIVER") else None
    driver = webdriver.Chrome(options=opts, service=service)
    driver.set_page_load_timeout(30)
    return driver


@pytest.fixture
def driver(request):
    """A desktop-sized browser."""
    opts = _options()
    opts.add_argument("--window-size=1366,900")
    d = _start(opts)
    yield d
    _save_evidence(request, d)
    d.quit()


@pytest.fixture
def phone(request):
    """A phone-sized browser, with a mobile viewport and touch."""
    opts = _options()
    opts.add_experimental_option("mobileEmulation", {"deviceMetrics": site_facts.PHONE})
    d = _start(opts)
    yield d
    _save_evidence(request, d)
    d.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def _save_evidence(request, driver):
    report = getattr(request.node, "rep_call", None)
    if report is None or not report.failed:
        return
    ARTIFACTS.mkdir(exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
    try:
        driver.save_screenshot(str(ARTIFACTS / f"{name}.png"))
        (ARTIFACTS / f"{name}.html").write_text(driver.page_source, encoding="utf-8")
    except Exception as exc:  # evidence is best effort; never mask the real failure
        print(f"could not save evidence for {name}: {exc}")
