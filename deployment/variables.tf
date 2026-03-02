variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "alert_threshold_pct" {
  description = "Quota utilization percentage threshold for alerts"
  type        = number
  default     = 80
}

variable "alert_email" {
  description = "Email address for SNS alerts (optional)"
  type        = string
  default     = ""
}

variable "report_bucket_name" {
  description = "S3 bucket name for quota reports (auto-generated if empty)"
  type        = string
  default     = ""
}

variable "report_retention_days" {
  description = "Days to retain reports in S3"
  type        = number
  default     = 90
}

variable "report_days_back" {
  description = "Days back to include in monthly report"
  type        = number
  default     = 30
}

variable "enable_cloudwatch_metric_alarms" {
  description = "Enable creation of CloudWatch metric alarms from JSON config file"
  type        = bool
  default     = false
}

variable "cloudwatch_metric_alarms_config_file" {
  description = "Path to JSON file with CloudWatch alarm definitions (relative to deployment/ or absolute path)"
  type        = string
  default     = ""
}
