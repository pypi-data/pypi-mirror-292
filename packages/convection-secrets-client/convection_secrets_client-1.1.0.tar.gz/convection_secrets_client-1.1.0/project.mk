
PROJECT_OWNER := AccidentallyTheCable
PROJECT_EMAIL := cableninja@cableninja.net
PROJECT_FIRST_YEAR := 2023
PROJECT_LICENSE := GPLv3
PROJECT_NAME := convection-secrets-client
PROJECT_DESCRIPTION := Convection Secrets Client
PROJECT_VERSION := 1.0.0

## Enable Feature 'Python'
BUILD_PYTHON := 1
## Enable Feature 'Shell'
BUILD_SHELL := 0
## Enable Feature 'Docker'
BUILD_DOCKER := 0
## Enable python `dist` Phase for Projects destined for PYPI
PYTHON_PYPI_PROJECT := 1
## Additional Flags for pylint. EX --ignore-paths=mypath
PYLINT_EXTRA_FLAGS := 

### Any Further Project-specific make targets can go here
project_lint:  ## Project-specific lint actions
	pip install -e .
