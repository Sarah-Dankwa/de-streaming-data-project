#################################################################################
#
# Makefile to build the project
#
#################################################################################

# Set variables from .env to MAKE
# include .env
# export

PROJECT_NAME = de-streaming-data-project
REGION = eu-west-2
PYTHON_INTERPRETER = python3
WD=$(shell pwd)
PYTHONPATH=${WD}
SHELL := /bin/bash
PROFILE = default
PIP:=pip3

## Create python interpreter environment.
create-environment:
	@echo ">>> About to create environment: $(PROJECT_NAME)..."
	@echo ">>> check python3 version"
	( \
		$(PYTHON_INTERPRETER) --version; \
	)
	@echo ">>> Setting up VirtualEnv."
	( \
	    $(PIP) install -q virtualenv virtualenvwrapper; \
	    virtualenv venv --python=$(PYTHON_INTERPRETER); \
	)

# # Define utility variable to help calling Python from the virtual environment
# ACTIVATE_ENV := source venv/bin/activate

# Execute python related functionalities from within the project's environment
define execute_in_env
	(source venv/bin/activate && $1)
endef

## Build the environment requirements
requirements: create-environment
	$(call execute_in_env, $(PIP) install -r ./requirements.txt)

## Set up dependencies/python directory and install specific packages
custom-dependencies: 
	
	@echo ">>> Setting up dependencies/python directory..."
	mkdir -p dependencies/python

	@echo ">>> Installing requests to dependencies/python..."
	$(call execute_in_env, $(PIP) install requests "urllib3<2" -t dependencies/python --no-cache-dir)

	@echo ">>> Installing pydantic to dependencies/python..."
	$(call execute_in_env, $(PIP) install pydantic -t dependencies/python --no-cache-dir)

all-requirements: requirements custom-dependencies

################################################################################################################
# Set Up
## Install bandit
bandit:
	$(call execute_in_env, $(PIP) install bandit)

## Install safety
safety:
	$(call execute_in_env, $(PIP) install safety)

## Install black
black:
	$(call execute_in_env, $(PIP) install black==22.12.0)

## Install coverage
coverage:
	$(call execute_in_env, $(PIP) install coverage)

## Install flake8
flake8:
	$(call execute_in_env, $(PIP) install flake8)

## Set up dev requirements (bandit, black, safety, flake8 & coverage)
dev-setup: bandit safety black coverage flake8

################################################################################################################

## Test and Security

## Run the security test (bandit + safety)
security-test:
	$(call execute_in_env, bandit -lll */*.py *c/*.py)
	$(call execute_in_env, safety check -r ./requirements.txt -i 66742 -i 70612)

## Run the black code check
run-black:
	$(call execute_in_env, black  ./src/*.py ./test/*.py)

## Run flake8
run-flake8: 
	$(call execute_in_env, flake8  ./src/*.py ./test/*.py)

## Run the unit tests
unit-tests:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest test/ -vvvrP)

## Run the coverage check
check-coverage:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest --cov=src test/)

## Run all checks
run-checks: run-flake8 unit-tests check-coverage


################################################################################################################

#Deployment
## Run Terraform Init
terraform-init:
	@echo ">>> Initializing Terraform"
	cd terraform && terraform init

## Run Terraform Plan
terraform-plan: custom-dependencies terraform-init
	@echo ">>> Running Terraform Plan ..."
	cd terraform && terraform plan

## Run Terraform Apply
terraform-apply: custom-dependencies terraform-init
	@echo ">>> Running Terraform Apply ..."
	cd terraform && terraform apply -auto-approve

## Run Terraform Destroy
terraform-destroy: custom-dependencies terraform-init
	@echo ">>> Destroying Terraform-managed infrastructure ..."
	cd terraform && terraform destroy -auto-approve

# Clean up dependencies after deployment 
clean-dependencies:
	@echo ">>> Cleanig dependencies/python ..."
	rm -rf dependencies/python
## rm -rf venv
