import base64
import os
import sys
from datetime import datetime
import pytest
from pytest_html import extras
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.ie.service import Service as IEService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.chrome import ChromeType
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager, EdgeChromiumDriverManager
from Utilities.email_handler import EmailHandler
from Utilities.log_handler import Logger
from Utilities.read_properties import ReadConfig

global_logger = Logger.setup_logging()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_setup(item):
    """Hook to log the test case name at the beginning of each test"""
    test_case_name = item.nodeid.split("::")[-1]
    Logger.log_test_case_name(test_case_name)
    yield


def pytest_addoption(parser):
    """Adding command-line options to pytest"""
    parser.addoption("--browser_name", action="store", default="chrome")
    parser.addoption("--browsers", action="store", help="Comma-separated list of browsers to run tests on")
    parser.addoption("--ENV", action="store", default="UAT")
    parser.addoption("--num_data_sets", action="store", type=int, default=1)
    parser.addoption("--email_pytest_report", action="store", default="N",
                     help="Send email with reports after test run")
    parser.addoption("--headless", action="store_true", help="Run tests in headless mode")
    parser.addoption("--parallel", action="store_true", help="Run tests in parallel")


@pytest.fixture(scope="function", params=None)
def session_setup(request):
    """Setup fixture to initialize the webdriver based on browser and configuration"""
    config = ReadConfig()
    env = request.config.getoption("ENV")
    config.details = env
    browsers = request.config.getoption("browsers")
    headless = request.config.getoption("--headless")

    if browsers:
        browser_names = browsers.split(",")
    else:
        browser_names = [request.config.getoption("browser_name")]

    parallel = request.config.getoption("--parallel")

    if parallel:
        pytest.mark.parametrize('browser_name', browser_names)

    browser_name = request.param if parallel else browser_names[0]

    global_logger.info("Starting session setup for browser: %s in environment: %s", browser_name, env)
    driver = None
    try:
        driver = get_driver(browser_name.strip(), headless)
        driver.maximize_window()
        driver.get(config.get_url())
        yield driver
    except Exception as e:
        global_logger.error("Error during driver setup: %s", e)
        pytest.fail(f"Setup failed: {e}")
    finally:
        if driver:
            global_logger.info("Quitting WebDriver for the session")
            driver.quit()


def get_driver(browser_name, headless):
    """Returns the appropriate WebDriver instance based on the browser name"""
    global_logger.info("Getting driver for browser: %s", browser_name)
    browser_options = {
        'chrome': get_chrome_driver,
        'chromium': get_chromium_driver,
        'IE': get_ie_driver,
        'edge': get_edge_driver,
        'firefox': get_firefox_driver,
    }
    if browser_name in browser_options:
        driver = browser_options[browser_name](headless)
        global_logger.info("Successfully launched %s browser", browser_name)
        return driver
    else:
        global_logger.error("Browser %s is not supported", browser_name)
        raise ValueError(f"Browser {browser_name} is not supported.")


def get_chrome_driver(headless):
    global_logger.info("Setting up Chrome driver")
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    service = ChromeService(executable_path=ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def get_chromium_driver(headless):
    global_logger.info("Setting up Chromium driver")
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    service = ChromeService(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    return webdriver.Chrome(service=service, options=options)


def get_ie_driver():
    global_logger.info("Setting up IE driver")
    # Note: IE does not support headless mode
    service = IEService(executable_path=IEDriverManager().install())
    return webdriver.Ie(service=service)


def get_edge_driver(headless):
    global_logger.info("Setting up Edge driver")
    options = webdriver.EdgeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    service = EdgeService(executable_path=EdgeChromiumDriverManager().install())
    return webdriver.Edge(service=service, options=options)


def get_firefox_driver(headless):
    global_logger.info("Setting up Firefox driver")
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    service = FirefoxService(executable_path=GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    """Hook to set attributes on the item for each test phase"""
    outcome = yield
    report = outcome.get_result()

    extra = getattr(report, "extras", [])
    if not isinstance(extra, list):
        extra = []

    if report.when == "call":
        # Add URL to report
        extra.append(extras.url("https://www.ticketId.com/"))
        xfail = hasattr(report, "wasxfail")

        if (report.skipped and xfail) or (report.failed and not xfail):
            # Only add additional HTML on failure
            extra.append(extras.html("<div>Additional HTML</div>"))

            driver = item.funcargs.get('session_setup')
            if driver:
                try:
                    # Define screenshots directory
                    screenshots_dir = os.path.join(os.path.dirname(__file__), 'Screenshots')
                    os.makedirs(screenshots_dir, exist_ok=True)

                    # Define screenshot file path
                    screenshot_file = os.path.join(
                        screenshots_dir,
                        f"{item.name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
                    )

                    # Take screenshot and save it
                    driver.save_screenshot(screenshot_file)

                    # Read the screenshot file and encode it to base64
                    with open(screenshot_file, "rb") as image_file:
                        base64_string = base64.b64encode(image_file.read()).decode('utf-8')

                    # Create JavaScript to open the image in a new window
                    html_content = (
                            '<div><img src="data:image/png;base64,%s" alt="screenshot" '
                            'style="width:304px;height:228px;"'
                            'onclick="var w=window.open();w.document.write(\'<img src=\\\'data:image/png;base64,'
                            '%s\\\' style=\\\'width:100%%;\\\'>\');" align="right"/></div>'
                            % (base64_string, base64_string)
                    )
                    extra.append(extras.html(html_content))

                except Exception as e:
                    print(f"Failed to attach screenshot: {e}")

    report.extras = extra
    setattr(item, "rep_" + report.when, report)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Custom summary and send email report if enabled"""
    Logger.log_summary_report()
    global_logger.info("Generating custom terminal summary")
    if not hasattr(terminalreporter.config, 'workerinput'):
        # Custom summary
        terminalreporter.write_sep("=", "Custom Test Summary")
        summary = []

        total_tests = sum(len(terminalreporter.stats.get(x, [])) for x in ['passed', 'failed', 'skipped'])
        summary.append(f"Total tests run: {total_tests}")
        global_logger.info("Total tests run: %d", total_tests)

        passed = terminalreporter.stats.get('passed', [])
        summary.append(f"Passed tests: {len(passed)}")
        global_logger.info("Passed tests: %d", len(passed))

        failed = terminalreporter.stats.get('failed', [])
        summary.append(f"Failed tests: {len(failed)}")
        global_logger.info("Failed tests: %d", len(failed))

        skipped = terminalreporter.stats.get('skipped', [])
        summary.append(f"Skipped tests: {len(skipped)}")
        global_logger.info("Skipped tests: %d", len(skipped))

        summary.append("\nTest Durations:")
        for report in passed + failed + skipped:
            duration = getattr(report, 'duration', 0)
            summary.append(f" - {report.nodeid}: {duration:.2f} seconds")
            global_logger.info("Test: %s took %.2f seconds", report.nodeid, duration)

        summary.append(f"\nExit status: {exitstatus}")
        global_logger.info("Exit status: %d", exitstatus)

        terminalreporter.write("\n".join(summary))
        terminalreporter.write_sep("=", "End of Summary")

        # Send email report if enabled
        if config.getoption("--email_pytest_report").lower() == 'y':
            global_logger.info("Sending email report as it is enabled")
            EmailHandler.send_email_by_gmail()
    Logger.log_end()
