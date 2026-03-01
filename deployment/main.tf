provider "aws" {
  region = "eu-central-1"
}

# S3 Bucket for reports
resource "aws_s3_bucket" "reports" {
  bucket = var.report_bucket_name != "" ? var.report_bucket_name : "qm-reports-${data.aws_caller_identity.current.account_id}"
  tags   = var.tags
}

# Enable versioning for reports bucket
resource "aws_s3_bucket_versioning" "reports" {
  bucket = aws_s3_bucket.reports.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle policy for reports
resource "aws_s3_bucket_lifecycle_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id

  rule {
    id     = "delete-old-reports"
    status = "Enabled"

    expiration {
      days = var.report_retention_days
    }
  }
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Lambda Layer with Python dependencies (boto3, etc.)
resource "aws_lambda_layer_version" "qm_dependencies" {
  filename            = data.archive_file.lambda_layer.output_path
  layer_name          = "qm-dependencies"
  compatible_runtimes = ["python3.14"]
  source_code_hash    = data.archive_file.lambda_layer.output_base64sha256

  depends_on = [data.archive_file.lambda_layer]
}

resource "aws_iam_role" "lambda_exec" {
  name = "qm-quotacontroller-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect    = "Allow"
        Sid       = ""
      }
    ]
  })
  # allow tags to be passed in via variable
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "attach_lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Inline policy for Service Quotas access
resource "aws_iam_role_policy" "lambda_service_quotas" {
  name = "qm-quotacontroller-service-quotas"
  role = aws_iam_role.lambda_exec.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "servicequotas:GetServiceQuota",
          "servicequotas:ListServiceQuotas",
          "servicequotas:ListServices",
          "cloudwatch:GetMetricData",
          "cloudwatch:GetMetricStatistics",
          "sts:GetCallerIdentity"
        ],
        Resource = "*"
      }
    ]
  })
}

# Inline policy to allow Lambda to access S3 for reports
resource "aws_iam_role_policy" "lambda_s3" {
  name = "qm-quotacontroller-s3"
  role = aws_iam_role.lambda_exec.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource = [
          aws_s3_bucket.reports.arn,
          "${aws_s3_bucket.reports.arn}/*"
        ]
      }
    ]
  })
}

# SNS Topic for quota alerts
resource "aws_sns_topic" "qm_alerts" {
  name = "qm-quota-alerts"
  tags = var.tags
}

resource "aws_sns_topic_subscription" "qm_alerts_email" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.qm_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

locals {
  cw_alarm_config_raw = var.enable_cloudwatch_metric_alarms && var.cloudwatch_metric_alarms_config_file != "" ? jsondecode(file(var.cloudwatch_metric_alarms_config_file)) : []
  cw_alarm_list       = can(local.cw_alarm_config_raw.alarms) ? local.cw_alarm_config_raw.alarms : local.cw_alarm_config_raw
  cw_alarm_map        = { for alarm in local.cw_alarm_list : alarm.alarm_name => alarm }
}

resource "aws_cloudwatch_metric_alarm" "qm_metric_alarms" {
  for_each = var.enable_cloudwatch_metric_alarms ? local.cw_alarm_map : {}

  alarm_name                = each.value.alarm_name
  alarm_description         = lookup(each.value, "alarm_description", "Quota metric alarm managed by Terraform")
  comparison_operator       = lookup(each.value, "comparison_operator", "GreaterThanOrEqualToThreshold")
  evaluation_periods        = lookup(each.value, "evaluation_periods", 1)
  datapoints_to_alarm       = lookup(each.value, "datapoints_to_alarm", null)
  threshold                 = each.value.threshold
  treat_missing_data        = lookup(each.value, "treat_missing_data", "notBreaching")
  insufficient_data_actions = lookup(each.value, "insufficient_data_actions", [])

  namespace   = each.value.namespace
  metric_name = each.value.metric_name
  statistic   = lookup(each.value, "statistic", "Maximum")
  period      = lookup(each.value, "period", 300)
  unit        = lookup(each.value, "unit", null)
  dimensions  = lookup(each.value, "dimensions", null)

  alarm_actions = [aws_sns_topic.qm_alerts.arn]
  ok_actions    = lookup(each.value, "ok_to_sns", false) ? [aws_sns_topic.qm_alerts.arn] : []

  tags = var.tags
}

# Inline policy to allow Lambda to publish to SNS topic
resource "aws_iam_role_policy" "lambda_sns" {
  name = "qm-quotacontroller-sns"
  role = aws_iam_role.lambda_exec.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sns:Publish"
        ],
        Resource = [
          aws_sns_topic.qm_alerts.arn
        ]
      }
    ]
  })
}

# Inline policy to allow Lambda to publish to SNS topic
resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "qm-quotacontroller-dynamodb"
  role = aws_iam_role.lambda_exec.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem",
          "dynamodb:BatchGetItem"
        ],
        Resource = [
          aws_dynamodb_table.qm_quotalog.arn,
          "${aws_dynamodb_table.qm_quotalog.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_lambda_function" "quota_collector" {
  function_name = "qm-quota-collector"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "functions.quota-collector.main.lambda_handler"
  runtime       = "python3.14"
  filename      = data.archive_file.quota_collector_zip.output_path
  timeout       = 300
  memory_size   = 512

  source_code_hash = filebase64sha256(data.archive_file.quota_collector_zip.output_path)

  # Attach the dependencies layer
  layers = [aws_lambda_layer_version.qm_dependencies.arn]

  # propagate tags to the lambda function
  tags = var.tags

  environment {
    variables = {
      QM_QUOTA_TABLE      = aws_dynamodb_table.qm_quotalog.name
      QM_ALERT_TOPIC_ARN  = aws_sns_topic.qm_alerts.arn
      QM_ALERT_THRESHOLD  = var.alert_threshold_pct
    }
  }

}

resource "aws_lambda_function" "reporting" {
  function_name = "qm-reporting"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "functions.reporting.main.lambda_handler"
  runtime       = "python3.14"
  filename      = data.archive_file.reporting_zip.output_path
  timeout       = 900
  memory_size   = 256

  source_code_hash = filebase64sha256(data.archive_file.reporting_zip.output_path)

  # Attach the dependencies layer
  layers = [aws_lambda_layer_version.qm_dependencies.arn]

  # propagate tags to the lambda function
  tags = var.tags

  environment {
    variables = {
      QM_QUOTA_TABLE      = aws_dynamodb_table.qm_quotalog.name
      QM_REPORT_BUCKET    = aws_s3_bucket.reports.id
      QM_REPORT_DAYS      = var.report_days_back
    }
  }

}

# Inline policy to allow Lambda to access EC2 for quota checks
resource "aws_iam_role_policy" "lambda_ec2" {
  name = "qm-quotacontroller-ec2"
  role = aws_iam_role.lambda_exec.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "EC2Checks",
        Effect = "Allow",
        Action = [
          # EC2 collector checks
          "ec2:DescribeInstances",
          "ec2:DescribeImages",
          "ec2:DescribeImageAttribute",
          "ec2:DescribeClientVpnEndpoints",
          "ec2:DescribeClientVpnAuthorizationRules",
          # VPC collector checks
          "ec2:DescribeVpcs",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeNetworkAcls",
          "ec2:DescribeRouteTables",
          "ec2:DescribeSubnets",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeInternetGateways",
          "ec2:DescribeEgressOnlyInternetGateways",
          "ec2:DescribeVpcEndpoints",
          "ec2:DescribeNatGateways",
          "ec2:DescribeVpcPeeringConnections",
          "ec2:DescribeVpcBlockPublicAccessExclusions"
        ],
        Resource = "*"
      },
      {
        Sid    = "RAMChecks",
        Effect = "Allow",
        Action = [
          "ram:ListResources",
          "ram:ListPrincipals"
        ],
        Resource = "*"
      },
      {
        Sid    = "LambdaChecks",
        Effect = "Allow",
        Action = [
          "lambda:GetAccountSettings",
          "lambda:ListFunctions",
          "lambda:GetPolicy",
          "lambda:ListEventSourceMappings"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_dynamodb_table" "qm_quotalog" {
  name         = "qm-quotalog"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "PK"
  range_key = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = var.tags
}

# EventBridge Rule for Quota Collector (every 10 minutes)
resource "aws_cloudwatch_event_rule" "quota_collector_schedule" {
  name                = "qm-collector-schedule"
  description         = "Trigger quota collector every 10 minutes"
  schedule_expression = "rate(10 minutes)"
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "quota_collector_target" {
  rule      = aws_cloudwatch_event_rule.quota_collector_schedule.name
  target_id = "qm-collector-lambda"
  arn       = aws_lambda_function.quota_collector.arn

  input = jsonencode({
    source = "eventbridge-scheduler"
  })
}

resource "aws_lambda_permission" "allow_eventbridge_collector" {
  statement_id  = "AllowExecutionFromEventBridgeCollector"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.quota_collector.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.quota_collector_schedule.arn
}

# EventBridge Rule for Report Generation (1st of every month at 00:00 UTC)
resource "aws_cloudwatch_event_rule" "reporting_schedule" {
  name                = "qm-reporting-schedule"
  description         = "Trigger report generation on 1st of month at 00:00 UTC"
  schedule_expression = "cron(0 0 1 * ? *)"
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "reporting_target" {
  rule      = aws_cloudwatch_event_rule.reporting_schedule.name
  target_id = "qm-reporting-lambda"
  arn       = aws_lambda_function.reporting.arn

  input = jsonencode({
    source   = "eventbridge-scheduler"
    days_back = 30
  })
}

resource "aws_lambda_permission" "allow_eventbridge_reporting" {
  statement_id  = "AllowExecutionFromEventBridgeReporting"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reporting.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.reporting_schedule.arn
}
