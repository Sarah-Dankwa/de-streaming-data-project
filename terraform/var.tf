variable "stream_lambda" {
  type    = string
  default = "stream"
}

variable "metric_namespace" {
  type = string
  default = "stream_metric"
}

variable "log_group_name" {
  type = string
  default = "stream_log_group"
}