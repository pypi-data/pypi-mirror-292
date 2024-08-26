import pytest


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
