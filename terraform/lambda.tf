# Set up lambda block in terraform to 
# point to local code file and add layers or enviroment variables where needed.

// create zip file function.zip in stream folder by packaging a Python script stream.py into a zip file 
data "archive_file" "lambda" {
  type             = "zip"
  output_file_mode = "0666"
  source_file      = "${path.module}/../src/stream.py"
  output_path      = "${path.module}/../stream.zip"
}

// Create layer zip files to allow requests and dotenv modules to be imported and used by lambda
data "archive_file" "custom_layer" {
  type             = "zip"
  output_file_mode = "0777"
  source_dir     = "${path.module}/../dependencies/"
  output_path    = "${path.module}/../layer_info.zip"

}


// Create layer resource using zip file from local machine
resource "aws_lambda_layer_version" "layer" {
    layer_name = "custom_layer"
    filename   = data.archive_file.custom_layer.output_path
    compatible_runtimes = ["python3.11"]

  }

// create lambda function with name 'stream' using the zip file 'stream/function.zip' from local machine
resource "aws_lambda_function" "stream_lambda_function" {

  # Defines the lambda function's name in aws, which is used as identifier for lambda functions
  function_name    = var.stream_lambda

  # Specifies the local location of the function
  filename = data.archive_file.lambda.output_path
  
  # This ensures the Lambda function code will only be updated if the hash of the ZIP file changes
#   source_code_hash = filebase64sha256("stream.zip")

  #Specifies the IAM role that the stream Lambda function will assume when it runs, where there is attached permissions of using other resources
  role             = aws_iam_role.stream_lambda_role.arn

  # Define the entry point of the Lambda function 'stream', which is 'lambda_handler()' inside 'stream.py' 
  handler          = "${var.stream_lambda}.lambda_handler"  
  runtime          = "python3.11"
  timeout          = 120
  
  publish = true

  # specify layers for the aws lambda function;  
  layers           = [aws_lambda_layer_version.layer.arn]

  }
  
 

