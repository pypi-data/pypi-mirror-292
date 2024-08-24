# bugster/conftest.py

import pytest
import json
from typing import Dict, Any, Callable
from playwright.sync_api import Browser, BrowserType
from .core.bugster_page import BugsterPage
from .config_loader import load_customer_config


def pytest_addoption(parser):
    parser.addoption(
        "--customer-id",
        action="store",
        required=True,
        help="Customer ID for loading specific configurations",
    )
    parser.addoption(
        "--video-path",
        action="store",
        default="/tmp/tests/videos/",
        help="Directory to store test videos",
    )
    parser.addoption(
        "--cookies-path",
        action="store",
        default="/tmp/session_cookies.json",
        help="Path to the cookies.json file for browser context",
    )
    parser.addoption(
        "--credentials",
        action="store",
        default="{}",
        help="JSON string containing credentials",
    )


@pytest.fixture(scope="session")
def config(request):
    customer_id = request.config.getoption("--customer-id")
    return load_customer_config(customer_id)


@pytest.fixture(scope="session")
def browser_context_args(config, request):
    video_path = request.config.getoption("--video-path")
    cookies_path = request.config.getoption("--cookies-path")
    return config.get_browser_context_args(video_path, cookies_path)


@pytest.fixture(scope="session")
def launch_browser(
    browser_type_launch_args: Dict, browser_type: BrowserType
) -> Callable[..., Browser]:
    def launch(**kwargs: Dict) -> Browser:
        launch_options = {
            **browser_type_launch_args,
            **kwargs,
            "args": ["--disable-gpu", "--single-process"],
            "headless": False,
        }
        return browser_type.launch(**launch_options)

    return launch


@pytest.fixture(scope="function")
def page(playwright, browser_context_args, launch_browser, request):
    browser = launch_browser()
    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    bugster_page = BugsterPage(page)

    if "login" in request.keywords:
        config = request.getfixturevalue("config")
        credentials_json = request.config.getoption("--credentials")
        credentials = json.loads(credentials_json)
        login_strategy = config.LOGIN_STRATEGY()
        login_strategy.login(bugster_page, credentials)

    yield bugster_page

    if request.node.rep_call.failed:
        screenshot_path = f"screenshot_{request.node.name}.png"
        bugster_page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

    video = bugster_page.video
    bugster_page.close()
    context.close()
    browser.close()

    if video:
        video_path = f"video_{request.node.name}.webm"
        video.save_as(video_path)
        print(f"Video saved to {video_path}")


def pytest_configure(config):
    config.addinivalue_line("markers", "login: mark test to run login before test")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
