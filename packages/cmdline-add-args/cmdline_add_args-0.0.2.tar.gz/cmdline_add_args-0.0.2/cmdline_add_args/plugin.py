import pytest

from config.env import ALLURE_REPORT_PATH, CREATE_ALLURE_REPORT


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(args):
    print("pytest_load_initial_conftests is called")


    if CREATE_ALLURE_REPORT:
        new_args = ["-v", f"--alluredir={ALLURE_REPORT_PATH}"]
        args[:] = new_args + args
        print(f"Modified pytest args: {args}")
    else:
        print("CREATE_ALLURE_REPORT is False or not defined")
