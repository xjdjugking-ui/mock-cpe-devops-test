"""UI test fixtures — supports local Chrome or remote Selenium via SELENIUM_REMOTE_URL."""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
HEADLESS = os.environ.get("HEADLESS", "1") == "1"
SELENIUM_REMOTE_URL = os.environ.get("SELENIUM_REMOTE_URL", "")
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "screenshots")


def _make_driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--disable-gpu")

    if SELENIUM_REMOTE_URL:
        return webdriver.Remote(
            command_executor=SELENIUM_REMOTE_URL,
            options=opts,
        )
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
    WebDriverWait(driver, 10).until(lambda d: "/dashboard" in d.current_url)
    yield driver


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    yield
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    if failed:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        path = os.path.join(SCREENSHOT_DIR, f"{request.node.name}.png")
        driver.save_screenshot(path)
        try:
            import allure
            # 截图附件
            allure.attach.file(
                path,
                name="failure_screenshot.png",
                attachment_type=allure.attachment_type.PNG,
            )
            # 页面源码附件
            allure.attach(
                driver.page_source,
                name="page_source.html",
                attachment_type=allure.attachment_type.HTML,
            )
            # 浏览器控制台日志
            try:
                logs = driver.get_log("browser")
                log_text = "\n".join(
                    f"[{e['level']}] {e['message']}" for e in logs
                ) or "(no console logs)"
            except Exception:
                log_text = "(console log unavailable)"
            allure.attach(
                log_text,
                name="browser_console.log",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:
            pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_configure(config):
    """Write allure environment.properties for the Environment panel."""
    env_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "allure-results", "environment.properties"
    )
    os.makedirs(os.path.dirname(env_file), exist_ok=True)
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(f"BASE_URL={BASE_URL}\n")
        f.write(f"BROWSER=chrome\n")
        f.write(f"HEADLESS={HEADLESS}\n")
        f.write(f"SELENIUM_RUNNER={'remote' if SELENIUM_REMOTE_URL else 'local'}\n")
        f.write(f"PLATFORM={'Docker' if SELENIUM_REMOTE_URL else 'Windows'}\n")
