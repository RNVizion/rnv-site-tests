"""Page objects for rnvizion.dev.

Tests say what they check; these classes say how to find it on the page. When the
site's markup changes, the fix lands here once instead of in every test.
"""
from urllib.parse import urldefrag, urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def same_site(url: str, base_url: str) -> bool:
    """True when url is on the same host as base_url (www. or not)."""
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return host == urlparse(base_url).netloc.lower().removeprefix("www.")


def internal_links(hrefs, base_url: str) -> list[str]:
    """The distinct http(s) links on the site's own host, fragments removed, in order."""
    seen, out = set(), []
    for href in hrefs:
        if not href:
            continue
        url, _ = urldefrag(href.strip())
        if urlparse(url).scheme not in ("http", "https"):
            continue  # mailto:, tel:, javascript: and the like
        if not same_site(url, base_url):
            continue
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


class Page:
    path = "/"

    def __init__(self, driver, base_url: str, path: str | None = None):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        if path is not None:
            self.path = path

    @property
    def url(self) -> str:
        return self.base_url + self.path

    def open(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return self

    @property
    def title(self) -> str:
        return self.driver.title

    def hrefs(self) -> list[str]:
        """Every link's href as the browser resolved it (absolute)."""
        return [a.get_attribute("href") for a in self.driver.find_elements(By.CSS_SELECTOR, "a[href]")]

    def internal_links(self) -> list[str]:
        return internal_links(self.hrefs(), self.base_url)

    def horizontal_overflow(self) -> int:
        """Pixels the page is wider than the viewport. Above 0 means sideways scrolling."""
        return self.driver.execute_script(
            "return document.documentElement.scrollWidth - document.documentElement.clientWidth"
        )

    def images_missing_alt(self) -> list[str]:
        """The src of every <img> with no alt attribute at all. alt="" (decorative) is allowed."""
        return [
            img.get_attribute("src")
            for img in self.driver.find_elements(By.TAG_NAME, "img")
            if img.get_attribute("alt") is None
        ]

    def console_errors(self, allowed: list[str]) -> list[str]:
        """SEVERE browser-console messages, minus the ones site_facts allows."""
        return [
            entry["message"]
            for entry in self.driver.get_log("browser")
            if entry["level"] == "SEVERE" and not any(a in entry["message"] for a in allowed)
        ]


    # --- fonts -----------------------------------------------------------------

    def block_urls(self, patterns: list[str]):
        """Make Chrome refuse these URL patterns from now on (Chrome DevTools Protocol)."""
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": patterns})
        return self

    def stylesheet_hrefs(self) -> list[str]:
        return self.driver.execute_script(
            "return [...document.querySelectorAll('link[rel=stylesheet]')].map(l => l.href)"
        )

    def computed_font(self, selector: str) -> dict:
        """The first family the element's CSS asks for, and its weight."""
        return self.driver.execute_script(
            """const s = getComputedStyle(document.querySelector(arguments[0]));
               const first = s.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '');
               return {family: first, weight: s.fontWeight, declared: s.fontFamily};""",
            selector,
        )

    def face_statuses(self, family: str, weight: str) -> list[str]:
        """Load status of every declared face with this family and weight."""
        return self.driver.execute_script(
            """return [...document.fonts]
                 .filter(f => f.family.replace(/["']/g, '') === arguments[0] && f.weight === arguments[1])
                 .map(f => f.status);""",
            family, weight,
        )

    def painted_fonts(self, selector: str) -> list[dict]:
        """The fonts Chrome actually drew the element's text with, from the DevTools Protocol."""
        cdp = self.driver.execute_cdp_cmd
        cdp("DOM.enable", {})
        cdp("CSS.enable", {})
        root = cdp("DOM.getDocument", {})["root"]["nodeId"]
        node = cdp("DOM.querySelector", {"nodeId": root, "selector": selector})["nodeId"]
        return cdp("CSS.getPlatformFontsForNode", {"nodeId": node})["fonts"]


class HomePage(Page):
    path = "/"

    def nav_links(self):
        """Visible links in the site's navigation (a <nav>, or the page header if there is none)."""
        links = self.driver.find_elements(By.CSS_SELECTOR, "nav a[href]")
        if not links:
            links = self.driver.find_elements(By.CSS_SELECTOR, "header a[href]")
        return [a for a in links if a.is_displayed()]


class CardPage(Page):
    def phone_links(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "a[href^='tel:']")

    def email_links(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "a[href^='mailto:']")
