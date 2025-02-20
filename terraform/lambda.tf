# Stream Lambda Role

# resource "aws_iam_role" "stream_lambda_role" {
#   name_prefix = "role-${var.extract_lambda}"
#   force_detach_policies = true
#   assume_role_policy = <<EOF
#   {
#     "Version": "2012-10-17",
#     "Statement": [
#       {
#         "Effect": "Allow",
#         "Action": "sts:AssumeRole",
#         "Principal": {
#           "Service": "lambda.amazonaws.com"
#         }
#       }
#     ]
#   }
#   EOF
# }
