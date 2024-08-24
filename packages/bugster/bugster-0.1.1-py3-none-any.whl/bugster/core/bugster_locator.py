# bugster/core/bugster_locator.py

from playwright.sync_api import Locator, TimeoutError
import time


class BugsterLocator:
    def __init__(self, locator: Locator):
        self.playwright = locator

    def __call__(self, selector: str, **kwargs):
        return BugsterLocator(self.playwright.locator(selector, **kwargs))

    def click(self, **kwargs):
        time.sleep(1.5)
        if len(self.playwright.all()) > 1:
            try:
                self.playwright.first.click(timeout=5000, **kwargs)
            except TimeoutError:
                self.playwright.nth(1).click(**kwargs)
        else:
            self.playwright.first.click(**kwargs)

    def fill(self, text: str, **kwargs):
        time.sleep(1)
        self.playwright.fill(text, **kwargs)

    def check(self, **kwargs):
        time.sleep(1)
        self.playwright.check(**kwargs)

    def press(self, key: str, **kwargs):
        time.sleep(1)
        self.playwright.press(key, **kwargs)

    def filter(self, **kwargs):
        return BugsterLocator(self.playwright.filter(**kwargs))

    def locator(self, selector: str, **kwargs):
        return BugsterLocator(self.playwright.locator(selector, **kwargs))

    def get_by_text(self, text: str, **kwargs):
        return BugsterLocator(self.playwright.get_by_text(text, **kwargs))

    def get_by_role(self, role: str, **kwargs):
        return BugsterLocator(self.playwright.get_by_role(role, **kwargs))

    def get_by_placeholder(self, placeholder: str, **kwargs):
        return BugsterLocator(self.playwright.get_by_placeholder(placeholder, **kwargs))

    def get_by_label(self, label: str, **kwargs):
        return BugsterLocator(self.playwright.get_by_label(label, **kwargs))

    def __getattr__(self, name):
        return getattr(self.playwright, name)
