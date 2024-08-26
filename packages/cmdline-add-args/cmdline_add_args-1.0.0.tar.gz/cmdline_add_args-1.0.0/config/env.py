import os

import platform

def get_os_type():
    os_type = platform.system()
    if os_type == "Windows":
        return "Windows"
    elif os_type == "Darwin":
        return "macOS"
    else:
        return "Your OS is not supported"

current_os = get_os_type()

def get(key, default=None):
    var = os.environ.get(key=key, default=default)
    if isinstance(var, str):
        if var.lower() == 'true':
            var = True
        elif var.lower() == 'false':
            var = False
    return var


def get_browser_name(browser, current_directory):
    if browser == 'chrome':
        path = f'{current_directory}/chrome_report/allure-results'
    elif browser == 'firefox':
        path = f'{current_directory}/firefox_report/allure-results'
    else:
        path = f'{current_directory}/edge_report/allure-results'
    if current_os == "Windows":
        path = path.replace("/", "\\")
    else:
        pass
    return path


CURRENT_DIRECTORY = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
BROWSER = get("BROWSER", "chrome")  # browser name ["chrome" "edge", "firefox", "remote"]
ALLURE_REPORT_PATH = get_browser_name(browser=BROWSER, current_directory=CURRENT_DIRECTORY)

CREATE_ALLURE_REPORT = get('CREATE_ALLURE_REPORT', True)

