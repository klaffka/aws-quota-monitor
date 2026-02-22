output "quota_collector_function_name" {
  description = "Name of the quota collector Lambda function"
  value       = aws_lambda_function.quota_collector.function_name
}

output "quota_collector_function_arn" {
  description = "ARN of the quota collector Lambda function"
  value       = aws_lambda_function.quota_collector.arn
}

output "reporting_function_name" {
  description = "Name of the reporting Lambda function"
  value       = aws_lambda_function.reporting.function_name
}

output "reporting_function_arn" {
  description = "ARN of the reporting Lambda function"
  value       = aws_lambda_function.reporting.arn
}

output "dynamodb_table_name" {
  description = "DynamoDB table for quota logs"
  value       = aws_dynamodb_table.qm_quotalog.name
}

output "sns_topic_arn" {
  description = "SNS Topic for quota alerts"
  value       = aws_sns_topic.qm_alerts.arn
}

output "reports_bucket_name" {
  description = "S3 bucket for quota reports"
  value       = aws_s3_bucket.reports.id
}

output "reports_bucket_arn" {
  description = "ARN of S3 reports bucket"
  value       = aws_s3_bucket.reports.arn
}
