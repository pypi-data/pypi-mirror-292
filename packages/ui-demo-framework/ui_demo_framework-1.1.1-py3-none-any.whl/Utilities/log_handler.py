import logging
import os
from datetime import date, datetime
import threading


class Logger:
    logs_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Logs'))
    lock = threading.Lock()
    current_date = date.today()
    logger = None
    execution_number = 1
    first_test_case_logged = False
    summary_logged = False

    @classmethod
    def setup_logging(cls):
        with cls.lock:
            if cls.logger is not None:
                return cls.logger

            today = date.today()

            # Check if the date has changed
            if cls.current_date != today:
                cls.current_date = today
                cls.execution_number = 1

            # Get today's date in the desired format
            date_today = today.strftime('%d %B %y')

            # Create main logs directory if it doesn't exist
            if not os.path.exists(cls.logs_base_dir):
                os.makedirs(cls.logs_base_dir)

            # Create sub-directory for today's date
            date_dir = os.path.join(cls.logs_base_dir, date_today)
            if not os.path.exists(date_dir):
                os.makedirs(date_dir)

            # Adjust execution number based on existing log files
            cls.execution_number = cls._get_next_execution_number(date_dir)

            log_file_path = cls._get_log_file_path(date_dir, cls.execution_number)
            cls.logger = cls._create_logger(log_file_path)
            return cls.logger

    @classmethod
    def _get_next_execution_number(cls, date_dir):
        existing_files = os.listdir(date_dir)
        max_execution_number = 0
        for file_name in existing_files:
            if file_name.startswith("Execution") and file_name.endswith(".log"):
                try:
                    number = int(file_name[len("Execution"):].split('-')[0])
                    if number > max_execution_number:
                        max_execution_number = number
                except ValueError:
                    continue
        return max_execution_number + 1

    @classmethod
    def _create_logger(cls, log_file_path):
        logger = logging.getLogger('AutomationLogger')
        logger.setLevel(logging.DEBUG)

        # Clear any existing handlers to avoid duplication
        logger.handlers = []

        # Create file handler
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(logging.Formatter("%(asctime)s : %(levelname)s : %(message)s"))

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s : %(levelname)s : %(message)s"))

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    @classmethod
    def _get_log_file_path(cls, date_dir, execution_number):
        time_str = datetime.now().strftime('%H-%M-%S')
        return os.path.join(date_dir, f"Execution{execution_number}-({time_str}).log")

    @classmethod
    def get_logger(cls):
        if cls.logger is None:
            return cls.setup_logging()
        return cls.logger

    @classmethod
    def log_test_case_name(cls, test_case_name):
        if cls.logger is None:
            cls.setup_logging()

        # Define the header for the test case
        header = (f"************************************ {test_case_name} "
                  f"****************************************")

        # Write the header without extra newlines
        if cls.first_test_case_logged:
            for handler in cls.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    with open(handler.baseFilename, 'a') as log_file:
                        log_file.write(f"\n{header}\n")
        else:
            cls.first_test_case_logged = True
            for handler in cls.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    with open(handler.baseFilename, 'a') as log_file:
                        log_file.write(f"{header}\n")

        cls.logger.info(f"Test Case: {test_case_name}")

    @classmethod
    def log_summary_report(cls):
        if cls.logger is None:
            cls.setup_logging()

        header = ("************************************* Summary Report "
                  "*******************************************")

        if cls.summary_logged:
            # Avoid adding extra newlines for subsequent summary reports
            header = header.strip()

        for handler in cls.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                with open(handler.baseFilename, 'a') as log_file:
                    log_file.write(f"\n{header}\n")

        cls.logger.info("Generating custom terminal summary")
        cls.summary_logged = True

    @classmethod
    def log_end(cls):
        if cls.logger is None:
            cls.setup_logging()

        header = ("************************************** End "
                  "*******************************************************")

        for handler in cls.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                with open(handler.baseFilename, 'a') as log_file:
                    log_file.write(f"\n{header}\n")
