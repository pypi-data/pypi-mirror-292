import os
import platform

def get(key, default=None):
    var = os.environ.get(key=key, default=default)
    if isinstance(var, str):
        if var.lower() == 'true':
            var = True
        elif var.lower() == 'false':
            var = False
    return var

def get_os_type():
    os_type = platform.system()
    if os_type == "Windows":
        return "Windows"
    elif os_type == "Darwin":
        return "macOS"
    elif os_type == "Linux":
        return "Ubuntu"
    else:
        return "Your OS is not supported"

current_os = get_os_type()

def get_browser_name(browser, current_directory):
    if browser == 'chrome':
        path = f'{current_directory}/allure-results/chrome'
    elif browser == 'firefox':
        path = f'{current_directory}/allure-results/firefox'
    else:
        path = f'{current_directory}/allure-results/edge'
    if current_os == "Windows":
        path = path.replace("/", "\\")
    else:
        pass
    return path


CURRENT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
BROWSER = get("BROWSER", "chrome")  # browser name ["chrome" "edge", "firefox", "remote"]
ALLURE_REPORT_PATH = get_browser_name(browser=BROWSER, current_directory=CURRENT_DIRECTORY)
CREATE_ALLURE_REPORT = get('CREATE_ALLURE_REPORT', True)