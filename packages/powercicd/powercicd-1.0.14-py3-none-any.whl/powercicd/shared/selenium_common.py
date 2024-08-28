import logging
import os
import socket

from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium import webdriver

log = logging.getLogger(__name__)


_FILE_DIR         = os.path.dirname(os.path.abspath(__file__))
SELENIUM_LOG_PATH = os.path.normpath(os.path.abspath(fr"{_FILE_DIR}\..\.selenium\logs\selenium.log"))
USER_DATA_DIR     = os.path.normpath(os.path.abspath(fr"{_FILE_DIR}\..\.selenium\user_data"))


def find_free_port(start_port=20000, end_port=30000):
    """Finds a free port number in the specified range."""
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))  # Try to bind to the port
                return port  # If successful, return the port
            except OSError:
                pass  # If the port is in use, continue to the next one
    raise ValueError(f"No free port found in the specified range ({start_port}-{end_port}).")


def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def configure_selenium_logger():
    from selenium.webdriver.remote.remote_connection import LOGGER
    LOGGER.propagate = False
    
    log_dir = os.path.dirname(SELENIUM_LOG_PATH)
    log.debug(f"Ensuring the log directory exists: '{log_dir}'")
    os.makedirs(log_dir, exist_ok=True)
    selenium_handler = logging.FileHandler(SELENIUM_LOG_PATH)
    selenium_handler.setLevel(logging.INFO)
    selenium_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    LOGGER.addHandler(selenium_handler)
    log.debug(f"Configured the Selenium logger to write to '{SELENIUM_LOG_PATH}'")
    

def new_browser(tenant: str, keep_browser_open: bool) -> ChromiumDriver:
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    debugging_port = find_free_port()
    log.info(f"Opening new browser: {USER_DATA_DIR=}, {tenant=}, {debugging_port=}, {keep_browser_open=}")

    options = webdriver.EdgeOptions()
    options.add_argument(f'user-data-dir={USER_DATA_DIR}')
    options.add_argument(f"profile-directory={tenant}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--remote-debugging-port={debugging_port}")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    options.add_experimental_option("detach", True)
    
    return webdriver.Edge(options=options)
