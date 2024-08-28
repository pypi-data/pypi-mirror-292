import os
import configparser
import site
import importlib.util


def load_pytest_ini_from_site_packages(config):
    site_packages = site.getsitepackages()
    site_packages_path = site_packages[0]
    pytest_ini_path = os.path.join(site_packages_path, 'src', 'pytest.ini')

    if os.path.exists(pytest_ini_path):
        print(f"Found pytest.ini at {pytest_ini_path}")
        config_parser = configparser.ConfigParser()
        config_parser.read(pytest_ini_path)

        # Example: Override an option from pytest.ini if necessary
        if 'pytest' in config_parser and 'maxfail' in config_parser['pytest']:
            config.option.maxfail = int(config_parser['pytest']['maxfail'])
    else:
        print(f"Warning: {pytest_ini_path} does not exist")


def pytest_configure(config):
    # Load pytest.ini
    load_pytest_ini_from_site_packages(config)

    # Load conftest.py from site-packages
    site_packages = site.getsitepackages()
    site_packages_path = site_packages[0]
    conftest_path = os.path.join(site_packages_path, 'src', 'conftest.py')

    if os.path.exists(conftest_path):
        spec = importlib.util.spec_from_file_location("conftest", conftest_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"Loaded conftest.py from {conftest_path}")
    else:
        print(f"Warning: {conftest_path} does not exist")
