########################################## LAMBDA ###########################################################

# Stream Lambda Role

resource "aws_iam_role" "stream_lambda_role" {
  name_prefix = "role-${var.stream_lambda}"
  force_detach_policies = true
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "lambda.amazonaws.com" 
        }
      }
    ]
  }
  EOF
}

# ==========================================
# SQS POLICY FOR STREAM LAMBDA
# ==========================================

data "aws_iam_policy_document" "sqs_stream_document" {
  statement {
    effect   = "Allow"
     actions  = ["sqs:ReceiveMessage",
                "sqs:GetQueueAttributes",
                "sqs:GetQueueAttributes"
    ]
    resources = [
      "arn:aws:sqs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
    ]
  }
}

//Create the IAM policy using the sqs policy document
resource "aws_iam_policy" "sqs_policy_stream" {
  name_prefix = "sqs-policy-${var.stream_lambda}"
  policy      = data.aws_iam_policy_document.sqs_stream_document.json
}


# Attach the Policy to the Lambda Role
resource "aws_iam_role_policy_attachment" "sqs_stream_policy_attachment" {
  role       = aws_iam_role.stream_lambda_role.name
  policy_arn = aws_iam_policy.sqs_policy_stream.arn
}

# ==========================================
# CloudWatch Logs Policy for Stream Lambda
# ==========================================

//The IAM Policy Document specifies the permissions required for stream Lambda to access cloudwatch
data "aws_iam_policy_document" "cw_document_stream" {
  statement {
    effect   = "Allow"
    actions  = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:${aws_cloudwatch_log_group.stream_log_group.name}:*"]
  }
}

// Set up terraform IAMS permissions for Lambda - Cloudwatch
resource "aws_iam_policy" "cw_policy_stream" {
  name_prefix = "cw-policy-${var.stream_lambda}"
  policy      = data.aws_iam_policy_document.cw_document_stream.json
}

# Attach the CW Policy to the Stream Role
resource "aws_iam_role_policy_attachment" "cw_policy_attachment_stream" {
  role       = aws_iam_role.stream_lambda_role.name
  policy_arn = aws_iam_policy.cw_policy_stream.arn
}


