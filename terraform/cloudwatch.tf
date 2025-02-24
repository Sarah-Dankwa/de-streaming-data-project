//Creating cloudwatch log group
resource "aws_cloudwatch_log_group" "stream_log_group" {
  name              = var.log_group_name
  retention_in_days = 3
}

//Creating cloudwatch log metric filter
resource "aws_cloudwatch_log_metric_filter" "error_metric_filter" {
  name           = "Stream_error_metric_filter"
  pattern        = "ERROR"
  log_group_name = aws_cloudwatch_log_group.stream_log_group.name

  metric_transformation {
    name      = "ErrorCount"
    namespace = var.metric_namespace
    value     = "1"
  }
}



