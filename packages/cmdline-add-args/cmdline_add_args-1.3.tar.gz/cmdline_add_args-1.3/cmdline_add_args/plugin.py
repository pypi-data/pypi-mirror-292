from dotenv import load_dotenv
import os

import pytest

from cmdline_add_args.allure_report_path import CREATE_ALLURE_REPORT, ALLURE_REPORT_PATH


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(args):
    print("pytest_load_initial_conftests is called")

    if CREATE_ALLURE_REPORT:
        new_args = ["-v", f"--alluredir={ALLURE_REPORT_PATH}", "--clean-alluredir"]
        for arg in new_args:
            if arg not in args:
                if args[-1].split(".")[-1] == "py":
                    args.insert(-1, arg)
                else:
                    args.append(arg)
        print(f"Modified pytest args: {args}")

    env_path = os.path.join(os.getcwd(), 'config', 'env')

    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"Environment file {env_path} not found.")

    create_allure_report = os.getenv('CREATE_ALLURE_REPORT', 'True').lower() == 'true'

    if create_allure_report:
        new_args = ["-v", f"--alluredir={ALLURE_REPORT_PATH}", "--clean-alluredir"]
        for arg in new_args:
            if arg not in args:
                if args[-1].split(".")[-1] == "py":
                    args.insert(-1, arg)
                else:
                    args.append(arg)
        print(f"Modified pytest args: {args}")
    else:
        args[:] = [arg for arg in args if '--alluredir' not in arg and '--clean-alluredir' not in arg]
        print("Allure report is disabled.")

    print(f"Final pytest args: {args}")