# Robot Console Improved

This is a project to improve the console output of Robot Framework.

## Development

### Setup

For setting up a development environment, use hatch to set up the dependencies. Use the command `hatch build` to create the environment.

If you use Pycharm as IDE, run the command `hatch env run which python` and use the outputted path for the interpreter.
Also, in the run/debug configurations, select **Emulate terminal in output console** by selecting Modify options > Emulate terminal in output console.

For entering the hatch virtual environment, use the commando `hatch shell`.

### Usage

To run the application enter the hatch virtual environment and use the comando `rci {tests}` where {tests} is the path to the tests to be run.

### Pycharm Run/Debug Configurations

![img.png](pycharm_conf.png)

The {tests} in the configuration image indicates the path to the tests to be run.

## Installation

The Python package is available in the package registry of this repository.
A new build is generated for every push to the main branch or when a tag is created.
To install this tool, use the pip command provided in the package registry.

### Dependencies

The setup already covers some of the dependency setup, but the Robot Console Improved also supports the [robotframework-debuglibrary](https://github.com/xyb/robotframework-debuglibrary). To install this, first enter the virtual environment with `hatch shell` and then install the robotframework-debuglibrary with `pip install robotframework-debuglibrary`.

### Usage

After installation, you can run the application using the command `rci {tests}`, where {tests} represents the path to the tests you wish to execute.

If you are already using robotframework in your project and want to integrate the `RobotConsoleImproved` application, follow these steps:

1) Run the command `which robot` to obtain the path to the robot executable.
2) Run the command `which rci` to obtain the path to the rci executable.
3) Copy the rci file to the robot location using the following command: `cp {path_from_which_rci} {path_from_which_robot}`.

If you decide to revert to using robotframework instead of the RobotConsoleImproved tool, you can reinstall it with the following command: `pip install --force-reinstall robotframework`.

## Tests

To run the tests, first enter the hatch environment with ´hatch shell´ and then execute the command `hatch run tests:cov`.

## CI

[Dagger](https://dagger.io/) is used to run the CI, it can also be run locally. To do this, you must first create a virtual environment (if you do not already have one) with the command `python -m venv venv` and then enter the environment with `source venv/bin/activate`.

Then run the following command to install the correct pip packages `pip install dagger-io anyio typer`.

Once the packages are installed the CI can be run from the root folder `RobotConsoleImproved` with the command `python ci/main.py`
