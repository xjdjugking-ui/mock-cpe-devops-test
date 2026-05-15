"""UI test fixtures — requires Flask server running at http://127.0.0.1:5000."""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
HEADLESS = os.environ.get("HEADLESS", "1") == "1"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "screenshots")


def _make_driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")
    return webdriver.Chrome(options=opts)


@pytest.fixture
def driver():
    d = _make_driver()
    yield d
    d.quit()


@pytest.fixture
def logged_in_driver(driver):
    """Driver already authenticated as admin."""
    driver.get(f"{BASE_URL}/login")
    driver.find_element("id", "username").send_keys("admin")
    driver.find_element("id", "password").send_keys("admin123")
    driver.find_element("id", "login-button").click()
    yield driver


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    yield
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        path = os.path.join(SCREENSHOT_DIR, f"{request.node.name}.png")
        driver.save_screenshot(path)
        try:
            import allure
            allure.attach.file(path, name="screenshot",
                               attachment_type=allure.attachment_type.PNG)
        except Exception:
            pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
