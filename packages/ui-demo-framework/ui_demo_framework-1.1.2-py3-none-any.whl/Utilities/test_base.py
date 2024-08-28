import pytest
from Utilities.log_handler import Logger
from Utilities.read_properties import ReadConfig
from Utilities.web_driver_helper import WebDriverHelper


@pytest.mark.usefixtures("session_setup")
class TestBase:
    log = None
    read_config = ReadConfig()

    @pytest.fixture(autouse=True)
    def setup(self, request, session_setup):
        """Fixture to set up before each test method"""
        test_case_name = request.node.name
        self.log = Logger.get_logger()
        self.driver = session_setup
        request.cls.driver = self.driver
        self.helper = WebDriverHelper(self.driver, self.log)
        request.cls.helper = self.helper
