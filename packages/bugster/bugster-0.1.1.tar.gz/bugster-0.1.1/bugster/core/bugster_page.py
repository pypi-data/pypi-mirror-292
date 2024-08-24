# bugster/core/bugster_page.py

from playwright.sync_api import Page
from .bugster_locator import BugsterLocator


class BugsterPage:
    def __init__(self, page: Page):
        self.page = page

    def __getattr__(self, name):
        return getattr(self.page, name)

    def locator(self, selector: str, **kwargs):
        return BugsterLocator(self.page.locator(selector, **kwargs))

    def get_by_text(self, text: str, **kwargs):
        return BugsterLocator(self.page.get_by_text(text, **kwargs))

    def get_by_role(self, role: str, **kwargs):
        return BugsterLocator(self.page.get_by_role(role, **kwargs))

    def get_by_placeholder(self, placeholder: str, **kwargs):
        return BugsterLocator(self.page.get_by_placeholder(placeholder, **kwargs))

    def get_by_label(self, label: str, **kwargs):
        return BugsterLocator(self.page.get_by_label(label, **kwargs))
