terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
}
}

provider "aws" {
  region = "eu-west-2"
  default_tags {
    tags = {
      ProjectName = "Streaming-data-project"
      Team = "Sarah-Dankwa"
      Environment = "dev"
    }
  }
}