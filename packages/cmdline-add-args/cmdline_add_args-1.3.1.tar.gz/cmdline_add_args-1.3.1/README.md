# cmdline-add-args

Pytest plugin for handling and adding command line arguments

This plugin allows you to add custom arguments before running a test and generate Allure reports. It provides a flexible
way to inject arguments into Pytest and control the reporting process with Allure.

## Features

- Handling custom arguments
- Generating Allure reports
- Easy integration with Pytest

## Usage

- You need to create a config folder at the root of your project
- In this folder, create an env.py file in which the ALLURE_REPORT_PATH and CREATE_ALLURE_REPORT variables will be
  specified
  e.g:
- CREATE_ALLURE_REPORT = get('CREATE_ALLURE_REPORT', True)
- ALLURE_REPORT_PATH = f'{current_directory}/allure-results/browser_name'