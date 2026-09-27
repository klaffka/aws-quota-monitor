# Reporter cannot enumerate application resources or publish quota alerts.
resource "aws_iam_role" "reporting_exec" {
  name               = "qm-reporting-exec"
  assume_role_policy = aws_iam_role.lambda_exec.assume_role_policy
  tags               = var.tags
}

resource "aws_iam_role_policy" "reporting" {
  name = "qm-reporting"
  role = aws_iam_role.reporting_exec.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["servicequotas:ListServices", "servicequotas:ListServiceQuotas", "cloudwatch:GetMetricData", "sts:GetCallerIdentity"], Resource = "*" },
      { Effect = "Allow", Action = ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan", "dynamodb:PutItem", "dynamodb:BatchWriteItem"], Resource = aws_dynamodb_table.qm_quotalog.arn },
      { Effect = "Allow", Action = ["logs:CreateLogStream", "logs:PutLogEvents"], Resource = "${aws_cloudwatch_log_group.lambda["reporting"].arn}:*" }
    ]
  })
}

resource "aws_lambda_alias" "live" {
  for_each = {
    collector = { name = aws_lambda_function.quota_collector.function_name, version = aws_lambda_function.quota_collector.version }
    reporting = { name = aws_lambda_function.reporting.function_name, version = aws_lambda_function.reporting.version }
  }
  name             = "live"
  function_name    = each.value.name
  function_version = lookup(var.lambda_version_overrides, each.key, each.value.version)
}

resource "aws_sqs_queue" "failed_events" {
  name                       = "qm-failed-events"
  message_retention_seconds  = 1209600
  visibility_timeout_seconds = 960
  sqs_managed_sse_enabled    = true
  tags                       = var.tags
}

resource "aws_sqs_queue_policy" "failed_events" {
  queue_url = aws_sqs_queue.failed_events.url
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Sid = "DenyInsecureTransport", Effect = "Deny", Principal = "*", Action = "sqs:*", Resource = aws_sqs_queue.failed_events.arn, Condition = { Bool = { "aws:SecureTransport" = "false" } } },
      { Sid = "EventBridgeDelivery", Effect = "Allow", Principal = { Service = "events.amazonaws.com" }, Action = "sqs:SendMessage", Resource = aws_sqs_queue.failed_events.arn,
      Condition = { ArnEquals = { "aws:SourceArn" = [aws_cloudwatch_event_rule.quota_collector_schedule.arn, aws_cloudwatch_event_rule.reporting_schedule.arn] } } }
    ]
  })
}

resource "aws_iam_role_policy" "failed_event_delivery" {
  for_each = { collector = aws_iam_role.lambda_exec.name, reporting = aws_iam_role.reporting_exec.name }
  name     = "qm-failed-event-delivery"
  role     = each.value
  policy   = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["sqs:SendMessage"], Resource = aws_sqs_queue.failed_events.arn }] })
}

resource "aws_lambda_function_event_invoke_config" "failures" {
  for_each                     = aws_lambda_alias.live
  function_name                = each.value.function_name
  qualifier                    = each.value.name
  maximum_event_age_in_seconds = 21600
  maximum_retry_attempts       = 2
  destination_config {
    on_failure {
      destination = aws_sqs_queue.failed_events.arn
    }
  }
  depends_on = [aws_iam_role_policy.failed_event_delivery]
}

resource "aws_cloudwatch_metric_alarm" "failed_events" {
  alarm_name          = "qm-failed-events"
  namespace           = "AWS/SQS"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  dimensions          = { QueueName = aws_sqs_queue.failed_events.name }
  statistic           = "Maximum"
  period              = 300
  evaluation_periods  = 1
  comparison_operator = "GreaterThanThreshold"
  threshold           = 0
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.qm_alerts.arn]
  tags                = var.tags
}

resource "aws_cloudwatch_metric_alarm" "destination_failures" {
  for_each            = local.functions
  alarm_name          = "qm-${each.key}-destination-failures"
  namespace           = "AWS/Lambda"
  metric_name         = "DestinationDeliveryFailures"
  dimensions          = { FunctionName = each.value }
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  comparison_operator = "GreaterThanThreshold"
  threshold           = 0
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.qm_alerts.arn]
  tags                = var.tags
}

resource "aws_s3_bucket_policy" "reports_tls" {
  bucket = aws_s3_bucket.reports.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [{
    Sid       = "DenyInsecureTransport", Effect = "Deny", Principal = "*", Action = "s3:*",
    Resource  = [aws_s3_bucket.reports.arn, "${aws_s3_bucket.reports.arn}/*"],
    Condition = { Bool = { "aws:SecureTransport" = "false" } }
  }] })
}
