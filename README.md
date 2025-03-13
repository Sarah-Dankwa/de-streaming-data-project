# Streaming Data

The brief:
Create an application to retrieve articles from the Guardian API and publish it to a message broker so that it can be consumed and analysed by other applications.
The tool will accept a search term (e.g. "machine learning"), an optional "date_from" field, and a reference to a message broker. It will use the search terms to search for articles in the Guardian API. It will then post details of up to ten hits to the message broker.

## Installation

Run make requirements to install all the python dependencies.

```bash
make requirements
```

**Personal Access Token**

A personal access token will need to be generated in github to allow authentication in the command line if changes.

Navigate to *settings* under your user picture, *developer settings* and then create a *classic personal token*.

Set the scope of this token to *repo* and *workflow*.


**GitHub Secrets**

One you have forked and accessed the repository, you must add your aws credentials to github using the secrets feature.

Under your repository name, click  Settings. If you cannot see the "Settings" tab, select the  dropdown menu, then click Settings.

In the "Security" section of the sidebar, select  Secrets and variables, then click Actions.

Click the Secrets tab and then add new repository secret.

Add the following secrets:

| Name | Secret |
|------|-----|
AWS_ACCESS_KEY_ID|{your aws secret access key}
AWS_SECRET_ACCESS_KEY|{your aws secret access key}
AWS_REGION|{your aws default region}

**Resources to add in the AWS console**

You will need to add your guardian api key details to AWS in order to access information from the api.

Navigate to *Secrets Manager* in the AWS console and click store new secret.

Choose ***Other type of secret*** from the options and enter the information as a key value pair.

The key must be **api_key**, and then insert your own api key as the value.

Click next and you will be asked to enter a secret name - this must be **guardian_api_key**.

Leave all other configuration options and click store to add the new secret.

| Key | Value |
|------|-----|
api_key|{your guardian api key}


**Deploying to AWS**

***Step 1:***

Export AWS credentials to terminal with the below command to ensure terraform deploys to correct account and access to secret manager:
Credentials will be shared by AWS user with shared account

	export AWS_ACCESS_KEY_ID=<accesskey>
	export AWS_SECRET_ACCESS_KEY=<secret accesskey>
	export AWS_DEFAULT_REGION=eu-west-2

***Step 2:***

Navigate to the terraform directory of the project 

```bash
cd terraform 
```

Run the terraform init command to intialise the working directory and download the necessary plugins

```bash
terraform init
```
Run the terraform plan command to create a mock-up view of what changes Terraform will make to your aws infrastructure
The lambda function and layer zip files will be created during this plan.

```bash
terraform plan
```

Run the terraform apply command to execute to execute the actions proposed by the plan.

```bash
terraform apply
```

## Execution and Usage

After running terraform apply, the lambda function and its layer and the necessary permissions will be availble in your aws console.

To run the lambda function, the event inputs must be as given:

| Key | Value |
|------|-----|
search_term |{value} - mandatory search value for the api
reference |{value} - mandatory value for sqs stream 
date_from |{value} - optional value for api in the form YYYY-MM-DD


**Example** (the key value pair is entered as json in aws lambda):

```bash
{
  "search_term": "eurovision song contest",
  "reference": "eurovision news",
  "date_from: "2014-01-01"
}

```




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
- make dev-setup
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
