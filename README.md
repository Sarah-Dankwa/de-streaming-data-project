# Streaming Data

The brief:
Create an application to retrieve articles from the Guardian API and publish it to a message broker so that it can be consumed and analysed by other applications.
The tool will accept a search term (e.g. "machine learning"), an optional "date_from" field, and a reference to a message broker. It will use the search terms to search for articles in the Guardian API. It will then post details of up to ten hits to the message broker.

## Installation

Run make requirements to install all the python dependencies.

```bash
make requirements
```

**GitHub Secrets**

Add following secrets to github secrets

|Secret|Value|
|------|-----|
AWS_ACCESS_KEY_ID|aws secret access key
AWS_SECRET_ACCESS_KEY|aws secret access key
AWS_REGION|aws default region

**Resources to add in the AWS console**

Create secrets in secrets manager with the Guardian api key details

**secret name: guardian_api_key**


|Key|Value|

|api_key|{your api key}|

**Deploying to AWS**

Export AWS credentials to terminal to ensure terraform deploys to correct account and access to secret manager:
Credentials will be shared by AWS user with shared account

	export AWS_ACCESS_KEY_ID=<accesskey>
	export AWS_SECRET_ACCESS_KEY=<secret accesskey>
	export AWS_DEFAULT_REGION=eu-west-2

Then run terraform init

```bash
terraform init
```

## Execution and Usage

The inputs to the lambda function must be given as:

|Key|Value|

|search_term|{value}| - mandatory search value for api
|reference|{value}| - mandatory value for sqs stream reference name
|date_from|{value}| - optional value for api


## Used Technologies

**Programming Languages**
- Python
- Makefile


**Amazon Web Services**
- Alerts & Metrics
- Cloudwatch
- IAMs
- Lambda
- S3 Buckets
- Secrets Manager

**DevOps**
- Terraform
- Makefile
- GitHub Actions
- GitHub Secrets

**Testing**
- pytest library
- moto library
- unittest mock & patch

## Current Features

- Stream lambda function - connects to external API with given payload to 
retreive articles on the provided search material

- Lambda layer - Functions use custom requests and pydantic lambda layer 

- Cloudwatch logs - gives info about which files have been changed and logs any errors that have occurred


## Daily set up

Export AWS credentials to terminal to ensure terraform deploys to correct account and access to secret manager:
Credentials will be shared by AWS user with shared account

	export AWS_ACCESS_KEY_ID=<accesskey>
	export AWS_SECRET_ACCESS_KEY=<secret accesskey>
	export AWS_DEFAULT_REGION=eu-west-2


Makefile
- make requirements (only once or when pip list updated)
- make dev setup
- make run-checks

Ensure venv is active and python path exported
- source venv/bin/activate
- export PYTHONPATH=$(pwd)


END OF DAY: Terraform destroy!

## Contributors

**ME**
[Sarah Dankwa](https://github.com/Sarah-Dankwa)
- [Northcoders](https://github.com/northcoders)


## Further Setup information

##########PROJECT STRUCTURE##########

GitHub/workflow/
- deploy.yml

src/
- stream.py
test/
- test_stream.py
terraform/
- IAM
- Cloudwatch
- Lambda
- Data

.gitignore

requirements.txt

README.md

MAKEFILE

#############TESTING##################

Use of purest is required

Where applicable AWS Moto mocking should be applied

###########CICD####################### 

checks will be performed upon pull requests and push to main.

## Badges
![Amazon AWS](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)

![GitHub Actions](https://img.shields.io/badge/Github%20Actions-282a2e?style=for-the-badge&logo=githubactions&logoColor=367cfe)


![python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

![terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)

![vscode](https://img.shields.io/badge/VSCode-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)
