variable "aws_account_id" {
  description = "Account this deployment belongs to; refuse to run against any other. Empty disables the check."
  type        = string
  default     = ""
  validation {
    condition     = var.aws_account_id == "" || can(regex("^[0-9]{12}$", var.aws_account_id))
    error_message = "aws_account_id must be twelve digits, or empty."
  }
}

variable "aws_region" {
  description = "AWS region for all monitor resources"
  type        = string
  default     = "eu-central-1"
  validation {
    condition     = can(regex("^[a-z]{2}(-[a-z]+)+-[0-9]+$", var.aws_region))
    error_message = "aws_region must be an AWS region identifier."
  }
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "alert_threshold_pct" {
  description = "Quota utilization percentage threshold for alerts"
  type        = number
  default     = 80
  validation {
    condition     = var.alert_threshold_pct > 0 && var.alert_threshold_pct <= 100
    error_message = "alert_threshold_pct must be greater than 0 and at most 100."
  }
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
  validation {
    condition     = var.report_retention_days >= 1 && floor(var.report_retention_days) == var.report_retention_days
    error_message = "report_retention_days must be a positive integer."
  }
}

variable "report_days_back" {
  description = "Default days back for manual rolling reports"
  type        = number
  default     = 30
  validation {
    condition     = var.report_days_back >= 1 && var.report_days_back <= 455 && floor(var.report_days_back) == var.report_days_back
    error_message = "report_days_back must be an integer from 1 to 455."
  }
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
