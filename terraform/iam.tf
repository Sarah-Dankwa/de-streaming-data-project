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

########################################## SQS ###########################################################