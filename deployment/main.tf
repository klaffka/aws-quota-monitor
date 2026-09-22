provider "aws" {
  region = var.aws_region

  # The report bucket and several resource names are derived from the caller's
  # account. Planning with the wrong credentials therefore does not fail, it
  # quietly proposes to replace the bucket under a new name. Naming the account
  # turns that into a refusal before anything is planned.
  allowed_account_ids = var.aws_account_id != "" ? [var.aws_account_id] : null
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
  bucket     = aws_s3_bucket.reports.id
  depends_on = [aws_s3_bucket_versioning.reports]

  rule {
    id     = "delete-old-reports"
    status = "Enabled"

    filter {}
    expiration {
      days = var.report_retention_days
    }
    noncurrent_version_expiration {
      noncurrent_days = var.report_retention_days
    }
  }
  rule {
    id     = "remove-orphan-delete-markers"
    status = "Enabled"
    filter {}
    expiration {
      expired_object_delete_marker = true
    }
  }
}

resource "aws_s3_bucket_public_access_block" "reports" {
  bucket                  = aws_s3_bucket.reports.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Lambda Layer with Python dependencies (boto3, etc.)
resource "aws_lambda_layer_version" "qm_dependencies" {
  filename            = data.local_file.lambda_layer.filename
  layer_name          = "qm-dependencies"
  compatible_runtimes = ["python3.14"]
  source_code_hash    = data.local_file.lambda_layer.content_base64sha256

  # A new dependency set publishes a new layer version and Terraform would
  # delete the old one first, leaving the functions pointing at a version that
  # no longer exists -- and the collector runs every ten minutes. Keeping the
  # old version closes that gap and leaves something to roll back to.
  # `create_before_destroy` cannot do it here: it propagates to this resource's
  # dependencies, and the data source that reads the built ZIP cannot carry a
  # lifecycle block, so the graph becomes a cycle.
  skip_destroy = true

  depends_on = [data.local_file.lambda_layer]
}

resource "aws_iam_role" "lambda_exec" {
  name = "qm-quotacontroller-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = ""
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
  timeout       = 900
  memory_size   = 512
  architectures = ["x86_64"]

  source_code_hash = filebase64sha256(data.archive_file.quota_collector_zip.output_path)

  # Attach the dependencies layer
  layers = [aws_lambda_layer_version.qm_dependencies.arn]

  # propagate tags to the lambda function
  tags = var.tags

  environment {
    variables = {
      QM_QUOTA_TABLE     = aws_dynamodb_table.qm_quotalog.name
      QM_ALERT_TOPIC_ARN = aws_sns_topic.qm_alerts.arn
      QM_ALERT_THRESHOLD = var.alert_threshold_pct
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
  memory_size   = 512
  architectures = ["x86_64"]

  source_code_hash = filebase64sha256(data.archive_file.reporting_zip.output_path)

  # Attach the dependencies layer
  layers = [aws_lambda_layer_version.qm_dependencies.arn]

  # propagate tags to the lambda function
  tags = var.tags

  environment {
    variables = {
      QM_QUOTA_TABLE   = aws_dynamodb_table.qm_quotalog.name
      QM_REPORT_BUCKET = aws_s3_bucket.reports.id
      QM_REPORT_DAYS   = var.report_days_back
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
          "ec2:Describe*",
          "ec2:GetIpamPoolCidrs",
          "ec2:GetTransitGatewayMulticastDomainAssociations",
          "ec2:List*",
          "ec2:SearchTransitGatewayMulticastGroups"
        ],
        Resource = "*"
      },
      {
        Sid    = "RAMChecks",
        Effect = "Allow",
        Action = [
          "organizations:List*",
          "ram:Get*",
          "ram:List*"
        ],
        Resource = "*"
      },
      {
        Sid    = "LambdaChecks",
        Effect = "Allow",
        Action = [
          "lambda:GetAccountSettings",
          "lambda:GetFunctionConfiguration",
          "lambda:GetPolicy",
          "lambda:List*"
        ],
        Resource = "*"
      },
      {
        Sid    = "KmsChecks",
        Effect = "Allow",
        Action = [
          "kms:Describe*",
          "kms:GetKeyRotationStatus",
          "kms:List*"
        ],
        Resource = "*"
      },
      {
        Sid    = "SsmChecks",
        Effect = "Allow",
        Action = [
          "ssm:Describe*",
          "ssm:List*"
        ],
        Resource = "*"
      },
      {
        Sid    = "Route53ResolverChecks",
        Effect = "Allow",
        Action = [
          "route53resolver:List*"
        ],
        Resource = "*"
      },
      {
        Sid    = "AccountQuotaChecks",
        Effect = "Allow",
        Action = [
          "access-analyzer:List*",
          "acm-pca:List*",
          "acm:List*",
          "aco-automation:List*",
          "aidevops:List*",
          "airflow-serverless:List*",
          "airflow:List*",
          "amplify:List*",
          "amplifyuibuilder:List*",
          "aoss:BatchGetLifecyclePolicy",
          "aoss:Get*",
          "aoss:List*",
          "apigateway:GET",
          "apigateway:Get*",
          "apigateway:List*",
          "app-integrations:List*",
          "appconfig:List*",
          "appflow:Describe*",
          "appflow:List*",
          "application-autoscaling:Describe*",
          "application-signals:List*",
          "appmesh:Describe*",
          "appmesh:List*",
          "apprunner:List*",
          "appstream:Describe*",
          "appstream:List*",
          "appsync:List*",
          "aps:List*",
          "athena:List*",
          "auditmanager:Get*",
          "auditmanager:List*",
          "autoscaling-plans:Describe*",
          "autoscaling:Describe*",
          "backup:Describe*",
          "backup:List*",
          "batch:Describe*",
          "bedrock-agentcore:Get*",
          "bedrock-agentcore:List*",
          "bedrock:ExportAutomatedReasoningPolicyVersion",
          "bedrock:Get*",
          "bedrock:List*",
          "cases:BatchGetCaseRule",
          "cases:Get*",
          "cases:List*",
          "cases:SearchAllRelatedItems",
          "cassandra:Get*",
          "cassandra:List*",
          "chime:Get*",
          "chime:List*",
          "cleanrooms-ml:Get*",
          "cleanrooms-ml:List*",
          "cleanrooms:List*",
          "cloud9:List*",
          "cloudformation:Describe*",
          "cloudformation:GetTemplate",
          "cloudformation:List*",
          "cloudhsm:Describe*",
          "cloudtrail:Describe*",
          "cloudtrail:Get*",
          "cloudtrail:List*",
          "cloudwatch:Describe*",
          "codeartifact:Describe*",
          "codeartifact:List*",
          "codebuild:BatchGetBuilds",
          "codebuild:BatchGetProjects",
          "codebuild:List*",
          "codecommit:List*",
          "codedeploy:BatchGetDeployments",
          "codedeploy:Get*",
          "codedeploy:List*",
          "codeguru-profiler:List*",
          "codepipeline:Get*",
          "codepipeline:List*",
          "cognito-identity:List*",
          "cognito-idp:Describe*",
          "cognito-idp:List*",
          "comprehend:List*",
          "config:Describe*",
          "connect-campaigns:Get*",
          "connect-campaigns:List*",
          "connect:List*",
          "connect:SearchEmailAddresses",
          "databrew:List*",
          "dataexchange:List*",
          "datasync:List*",
          "datazone:List*",
          "datazone:Search",
          "datazone:SearchTypes",
          "dax:Describe*",
          "deadline:List*",
          "directconnect:Describe*",
          "discovery:List*",
          "dlm:Get*",
          "dms:Describe*",
          "docdb-elastic:Get*",
          "docdb-elastic:List*",
          "drs:Describe*",
          "drs:List*",
          "ds:Describe*",
          "dsql:List*",
          "dynamodb:Describe*",
          "dynamodb:List*",
          "ecr:Describe*",
          "ecs:Describe*",
          "ecs:List*",
          "eks:Describe*",
          "eks:List*",
          "elasticache:Describe*",
          "elasticbeanstalk:Describe*",
          "elasticbeanstalk:List*",
          "elasticfilesystem:Describe*",
          "elasticloadbalancing:Describe*",
          "elasticmapreduce:List*",
          "entityresolution:List*",
          "es:Describe*",
          "es:List*",
          "events:List*",
          "evidently:List*",
          "evs:List*",
          "finspace:Get*",
          "finspace:List*",
          "firehose:List*",
          "fis:Get*",
          "fis:List*",
          "fms:Get*",
          "fms:List*",
          "forecast:Describe*",
          "forecast:List*",
          "fsx:Describe*",
          "gamelift:Describe*",
          "gamelift:List*",
          "gameliftstreams:List*",
          "geo:List*",
          "glacier:List*",
          "glue:Describe*",
          "glue:GetCatalogs",
          "glue:GetColumnStatisticsTaskRun",
          "glue:GetConnections",
          "glue:GetCrawlers",
          "glue:GetDatabases",
          "glue:GetDevEndpoints",
          "glue:GetJobRuns",
          "glue:GetJobs",
          "glue:GetMLTaskRuns",
          "glue:GetMLTransforms",
          "glue:GetPartitions",
          "glue:GetSecurityConfigurations",
          "glue:GetTableVersions",
          "glue:GetTables",
          "glue:GetTriggers",
          "glue:GetUserDefinedFunctions",
          "glue:List*",
          "glue:QuerySchemaVersionMetadata",
          "grafana:List*",
          "greengrass:Get*",
          "greengrass:List*",
          "groundstation:Get*",
          "groundstation:List*",
          "guardduty:List*",
          "iam:GetAccountSummary",
          "identitystore:List*",
          "imagebuilder:Get*",
          "imagebuilder:List*",
          "inspector2:List*",
          "inspector:List*",
          "interconnect:List*",
          "internetmonitor:Get*",
          "internetmonitor:List*",
          "iot:Describe*",
          "iot:Get*",
          "iot:List*",
          "iotanalytics:List*",
          "iotevents:List*",
          "iotfleetwise:Get*",
          "iotfleetwise:List*",
          "iotsitewise:Describe*",
          "iotsitewise:List*",
          "iottwinmaker:Get*",
          "iottwinmaker:List*",
          "ivs:List*",
          "ivschat:List*",
          "kafka:List*",
          "kafkaconnect:List*",
          "kinesis:List*",
          "kinesisanalytics:List*",
          "kinesisvideo:List*",
          "lakeformation:Get*",
          "lakeformation:List*",
          "launchwizard:List*",
          "lex:Describe*",
          "lex:List*",
          "license-manager-linux-subscriptions:List*",
          "license-manager-user-subscriptions:List*",
          "license-manager:List*",
          "lightsail:Get*",
          "logs:Describe*",
          "logs:List*",
          "m2:Get*",
          "m2:List*",
          "macie2:Describe*",
          "macie2:Get*",
          "macie2:List*",
          "mediaconnect:Describe*",
          "mediaconnect:List*",
          "mediaconvert:List*",
          "medialive:List*",
          "mediapackage-vod:List*",
          "mediapackage:List*",
          "mediapackagev2:Get*",
          "mediapackagev2:List*",
          "mediastore:List*",
          "mediatailor:Describe*",
          "mediatailor:List*",
          "memorydb:Describe*",
          "mgn:Describe*",
          "mgn:List*",
          "migrationhub-orchestrator:List*",
          "migrationhub-strategy:List*",
          "mobiletargeting:Get*",
          "mobiletargeting:List*",
          "mq:Describe*",
          "mq:List*",
          "neptune-graph:List*",
          "network-firewall:Describe*",
          "network-firewall:List*",
          "networkmonitor:List*",
          "oam:List*",
          "observabilityadmin:List*",
          "omics:List*",
          "outposts:List*",
          "payment-cryptography:List*",
          "pca-connector-ad:List*",
          "pca-connector-scep:List*",
          "pcs:List*",
          "personalize:List*",
          "polly:List*",
          "profile:Get*",
          "profile:List*",
          "proton:List*",
          "qldb:List*",
          "quicksight:Describe*",
          "quicksight:List*",
          "rbin:Get*",
          "rbin:List*",
          "rds:Describe*",
          "redshift:Describe*",
          "refactor-spaces:List*",
          "rekognition:Describe*",
          "rekognition:List*",
          "repostspace:List*",
          "resiliencehub:Get*",
          "resiliencehub:List*",
          "resource-explorer-2:List*",
          "resource-groups:List*",
          "robomaker:List*",
          "rolesanywhere:List*",
          "route53profiles:List*",
          "rtbfabric:List*",
          "rum:List*",
          "s3-outposts:List*",
          "s3:GetBucketNotification",
          "s3:GetBucketTagging",
          "s3:GetLifecycleConfiguration",
          "s3:GetReplicationConfiguration",
          "s3:List*",
          "sagemaker:Describe*",
          "sagemaker:List*",
          "scheduler:List*",
          "schemas:List*",
          "scn:List*",
          "secretsmanager:List*",
          "securityagent:List*",
          "securityhub:Describe*",
          "securityhub:Get*",
          "securityhub:List*",
          "serverlessrepo:List*",
          "servicecatalog:Describe*",
          "servicecatalog:List*",
          "servicecatalog:SearchProductsAsAdmin",
          "servicediscovery:Get*",
          "servicediscovery:List*",
          "servicequotas:List*",
          "ses:List*",
          "shield:List*",
          "snow-device-management:List*",
          "snowball:List*",
          "sns:GetSubscriptionAttributes",
          "sns:List*",
          "social-messaging:List*",
          "sqs:GetQueueAttributes",
          "sqs:List*",
          "ssm-contacts:Get*",
          "ssm-contacts:List*",
          "ssm-incidents:List*",
          "ssm-quicksetup:List*",
          "ssm-sap:List*",
          "sso:List*",
          "states:List*",
          "storagegateway:Describe*",
          "storagegateway:List*",
          "supportauthz:List*",
          "swf:CountOpenWorkflowExecutions",
          "swf:List*",
          "synthetics:Describe*",
          "textract:List*",
          "thinclient:List*",
          "timestream-influxdb:List*",
          "timestream:List*",
          "tnb:List*",
          "transcribe:List*",
          "transfer:Describe*",
          "transfer:List*",
          "translate:List*",
          "verifiedpermissions:List*",
          "voiceid:List*",
          "vpc-lattice:Get*",
          "vpc-lattice:List*",
          "waf-regional:Get*",
          "waf-regional:List*",
          "wafv2:Describe*",
          "wafv2:Get*",
          "wafv2:List*",
          "wellarchitected:Get*",
          "wellarchitected:List*",
          "wisdom:List*",
          "workspaces-instances:List*",
          "workspaces-web:List*",
          "workspaces:Describe*",
          "xray:Get*",
          "xray:List*"
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

  input_transformer {
    input_paths    = { scheduled_time = "$.time" }
    input_template = <<-JSON
      {"source":"eventbridge-scheduler","period":"previous_month","time":<scheduled_time>}
    JSON
  }
}

resource "aws_lambda_permission" "allow_eventbridge_reporting" {
  statement_id  = "AllowExecutionFromEventBridgeReporting"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reporting.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.reporting_schedule.arn
}

# The heartbeat is emitted only after every operational step succeeds.
resource "aws_iam_role_policy" "collector_heartbeat" {
  name = "qm-collector-heartbeat"
  role = aws_iam_role.lambda_exec.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "cloudwatch:PutMetricData"
      Resource  = "*"
      Condition = { StringEquals = { "cloudwatch:namespace" = "QuotaMonitor" } }
    }]
  })
}

locals {
  functions = {
    collector = aws_lambda_function.quota_collector.function_name
    reporting = aws_lambda_function.reporting.function_name
  }
  operational_alarms = {
    collector_errors    = { function = local.functions.collector, metric = "Errors" }
    collector_throttles = { function = local.functions.collector, metric = "Throttles" }
    reporting_errors    = { function = local.functions.reporting, metric = "Errors" }
    reporting_throttles = { function = local.functions.reporting, metric = "Throttles" }
  }
}

resource "aws_cloudwatch_log_group" "lambda" {
  for_each          = local.functions
  name              = "/aws/lambda/${each.value}"
  retention_in_days = 30
  tags              = var.tags
}

resource "aws_cloudwatch_metric_alarm" "operational" {
  for_each            = local.operational_alarms
  alarm_name          = "qm-${each.key}"
  namespace           = "AWS/Lambda"
  metric_name         = each.value.metric
  dimensions          = { FunctionName = each.value.function }
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.qm_alerts.arn]
  tags                = var.tags
}

resource "aws_cloudwatch_metric_alarm" "collector_missing" {
  alarm_name          = "qm-collector-no-success"
  namespace           = "QuotaMonitor"
  metric_name         = "CollectorSuccess"
  dimensions          = { Account = data.aws_caller_identity.current.account_id, Region = var.aws_region }
  statistic           = "Sum"
  period              = 1800
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "LessThanThreshold"
  treat_missing_data  = "breaching"
  alarm_actions       = [aws_sns_topic.qm_alerts.arn]
  tags                = var.tags
}
