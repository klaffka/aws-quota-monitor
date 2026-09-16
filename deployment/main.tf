provider "aws" {
  region = var.aws_region
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
          # EC2 collector checks
          "ec2:DescribeCapacityReservations",
          "ec2:DescribeVolumes",
          "ec2:DescribeIpams",
          "ec2:DescribeIpamScopes",
          "ec2:DescribeIpamPools",
          "ec2:GetIpamPoolCidrs",
          "ec2:DescribeIpamResourceDiscoveries",
          "ec2:DescribeIpamInternetRegistryAssociations",
          "ec2:DescribeIpamPrefixListResolvers",
          "ec2:DescribeSnapshots",
          "ec2:DescribeSnapshotTierStatus",
          "ec2:DescribeFastSnapshotRestores",
          "ec2:DescribeHosts",
          "ec2:DescribeTransitGateways",
          "ec2:DescribeTransitGatewayMulticastDomains",
          "ec2:SearchTransitGatewayMulticastGroups",
          "ec2:GetTransitGatewayMulticastDomainAssociations",
          "ec2:DescribeTransitGatewayAttachments",
          "ec2:DescribeVerifiedAccessEndpoints",
          "ec2:DescribeFpgaImages",
          "ec2:DescribeCustomerGateways",
          "ec2:DescribeVpnGateways",
          "ec2:DescribeManagedPrefixLists",
          "ec2:DescribeSecurityGroupVpcAssociations",
          "ec2:DescribeImages",
          "ec2:DescribeImageAttribute",
          "ec2:ListImagesInRecycleBin",
          "ec2:DescribeAddresses",
          "ec2:DescribeLaunchTemplates",
          "ec2:DescribeLaunchTemplateVersions",
          "ec2:DescribeVerifiedAccessInstances",
          "ec2:DescribeVerifiedAccessGroups",
          "ec2:DescribeVerifiedAccessTrustProviders",
          "ec2:DescribeClientVpnEndpoints",
          "ec2:DescribeClientVpnAuthorizationRules",
          "ec2:DescribeClientVpnConnections",
          "ec2:DescribeClientVpnRoutes",
          "ec2:DescribeVpnConnections",
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
          "ram:ListPrincipals",
          "ram:ListPermissions",
          "ram:GetResourceShares",
          "ram:GetResourceShareInvitations",
          "organizations:ListAccountsForParent",
          "organizations:ListOrganizationalUnitsForParent",
          "organizations:ListRoots"
        ],
        Resource = "*"
      },
      {
        Sid    = "LambdaChecks",
        Effect = "Allow",
        Action = [
          "lambda:GetAccountSettings",
          "lambda:GetFunctionConfiguration",
          "lambda:ListFunctions",
          "lambda:ListCapacityProviders",
          "lambda:ListFunctionVersionsByCapacityProvider",
          "lambda:ListNetworkConnectors",
          "lambda:ListMicrovmImages",
          "lambda:ListMicrovmImageVersions",
          "ec2:DescribeNetworkInterfaces",
          "lambda:GetPolicy",
          "lambda:ListAliases",
          "lambda:ListEventSourceMappings"
        ],
        Resource = "*"
      },
      {
        Sid    = "KmsChecks",
        Effect = "Allow",
        Action = [
          "kms:ListKeys",
          "kms:DescribeKey",
          "kms:ListAliases",
          "kms:ListGrants",
          "kms:DescribeCustomKeyStores",
          "kms:ListKeyRotations",
          "kms:GetKeyRotationStatus"
        ],
        Resource = "*"
      },
      {
        Sid    = "SsmChecks",
        Effect = "Allow",
        Action = [
          "ssm:DescribeParameters",
          "ssm:ListDocuments",
          "ssm:ListDocumentVersions",
          "ssm:ListAssociationVersions",
          "ssm:DescribeDocumentPermission",
          "ssm:DescribeMaintenanceWindows",
          "ssm:DescribePatchBaselines",
          "ssm:ListAssociations",
          "ssm:DescribePatchGroups"
        ],
        Resource = "*"
      },
      {
        Sid    = "Route53ResolverChecks",
        Effect = "Allow",
        Action = [
          "route53resolver:ListResolverEndpoints",
          "route53resolver:ListResolverRules",
          "route53resolver:ListResolverRuleAssociations",
          "route53resolver:ListFirewallDomainLists",
          "route53resolver:ListFirewallDomains",
          "route53resolver:ListFirewallRuleGroups"
          , "route53resolver:ListFirewallRuleGroupAssociations"
          , "route53resolver:ListFirewallRules"
        ],
        Resource = "*"
      },
      {
        Sid    = "AccountQuotaChecks",
        Effect = "Allow",
        Action = [
          "rds:DescribeAccountAttributes",
          "dms:DescribeAccountAttributes",
          "iam:GetAccountSummary"
          , "states:ListStateMachines"
          , "states:ListActivities"
          , "states:ListStateMachineVersions"
          , "states:ListStateMachineAliases"
          , "ecr:DescribeRepositories"
          , "ecr:DescribeImages"
          , "ecr:DescribePullThroughCacheRules"
          , "autoscaling:DescribeAutoScalingGroups"
          , "autoscaling:DescribeLifecycleHooks"
          , "autoscaling:DescribeNotificationConfigurations"
          , "autoscaling:DescribePolicies"
          , "autoscaling:DescribeScheduledActions"
          , "autoscaling:DescribeLaunchConfigurations"
          , "apigateway:GET"
          , "apigateway:ListPortals"
          , "apigateway:ListPortalProducts"
          , "apigateway:ListProductPages"
          , "apigateway:ListProductRestEndpointPages"
          , "apigateway:GetPortal"
          , "ecs:ListClusters"
          , "ecs:ListServices"
          , "ecs:DescribeServices"
          , "ecs:DescribeClusters"
          , "ecs:ListTaskDefinitionFamilies"
          , "ecs:ListTaskDefinitions"
          , "ecs:ListContainerInstances"
          , "eks:ListClusters"
          , "eks:ListNodegroups"
          , "eks:ListFargateProfiles"
          , "eks:DescribeCluster"
          , "eks:DescribeFargateProfile"
          , "eks:DescribeNodegroup"
          , "eks:ListAccessEntries"
          , "eks:ListEksAnywhereSubscriptions"
          , "firehose:ListDeliveryStreams"
          , "events:ListEventBuses"
          , "events:ListRules"
          , "events:ListTargetsByRule"
          , "cloudtrail:DescribeTrails"
          , "cloudtrail:ListEventDataStores"
          , "cloudtrail:ListChannels"
          , "cloudtrail:ListDashboards"
          , "sns:ListTopics"
          , "sns:ListSubscriptions"
          , "rtbfabric:ListRequesterGateways"
          , "rtbfabric:ListResponderGateways"
          , "rtbfabric:ListLinks"
          , "rtbfabric:ListCertificateAssociations"
          , "rtbfabric:ListLinkRoutingRules"
          , "tnb:ListSolFunctionPackages"
          , "tnb:ListSolNetworkPackages"
          , "tnb:ListSolNetworkInstances"
          , "tnb:ListSolNetworkOperations"
          , "interconnect:ListConnections"
          , "chime:ListAppInstances"
          , "chime:ListAppInstanceUsers"
          , "chime:ListAppInstanceAdmins"
          , "chime:ListAppInstanceUserEndpoints"
          , "chime:ListChannelFlows"
          , "chime:ListVoiceConnectors"
          , "chime:ListSipMediaApplications"
          , "chime:ListSipRules"
          , "chime:ListMediaPipelines"
          , "chime:GetMediaPipeline"
          , "chime:ListMediaPipelineKinesisVideoStreamPools"
          , "chime:ListMediaInsightsPipelineConfigurations"
          , "autoscaling-plans:DescribeScalingPlans"
          , "codecommit:ListRepositories"
          , "rum:ListAppMonitors"
          , "servicequotas:ListRequestedServiceQuotaChangeHistory"
          , "shield:ListProtections"
          , "translate:ListTerminologies"
          , "translate:ListTextTranslationJobs"
          , "greengrass:ListComponents"
          , "greengrass:ListComponentVersions"
          , "greengrass:ListCoreDevices"
          , "quicksight:ListApprovalPolicies"
          , "appflow:ListFlows"
          , "appflow:DescribeConnectorProfiles"
          , "connect-campaigns:ListCampaigns"
          , "connect-campaigns:GetCampaignStateBatch"
          , "inspector:ListAssessmentTargets"
          , "inspector:ListAssessmentTemplates"
          , "inspector:ListAssessmentRuns"
          , "license-manager-linux-subscriptions:ListLinuxSubscriptionInstances"
          , "migrationhub-orchestrator:ListWorkflows"
          , "migrationhub-orchestrator:ListWorkflowStepGroups"
          , "migrationhub-orchestrator:ListWorkflowSteps"
          , "ec2:DescribeFastLaunchImages"
          , "snowball:ListJobs"
          , "ec2:DescribeImportImageTasks"
          , "ec2:DescribeImportSnapshotTasks"
          , "ec2:DescribeExportImageTasks"
          , "ec2:DescribeConversionTasks"
          , "ec2:DescribeExportTasks"
          , "aco-automation:ListAutomationEvents"
          , "aidevops:ListAgentSpaces"
          , "organizations:ListRoots"
          , "organizations:ListDelegatedAdministrators"
          , "organizations:ListOrganizationalUnitsForParent"
          , "organizations:ListAccountsForParent"
          , "migrationhub-strategy:ListImportFileTask"
          , "migrationhub-strategy:ListServers"
          , "airflow-serverless:ListWorkflows"
          , "airflow-serverless:ListWorkflowVersions"
          , "airflow-serverless:ListWorkflowRuns"
          , "observabilityadmin:ListCentralizationRulesForOrganization"
          , "outposts:ListOutposts"
          , "s3-outposts:ListRegionalBuckets"
          , "s3-outposts:ListAccessPoints"
          , "securityagent:ListAgentSpaces"
          , "securityagent:ListCodeReviews"
          , "securityagent:ListCodeReviewJobsForCodeReview"
          , "securityagent:ListPentests"
          , "securityagent:ListPentestJobsForPentest"
          , "securityagent:ListThreatModels"
          , "securityagent:ListThreatModelJobs"
          , "snow-device-management:ListTasks"
          , "supportauthz:ListSupportPermits"
          , "medialive:ListInputs"
          , "medialive:ListInputSecurityGroups"
          , "medialive:ListChannels"
          , "medialive:ListMultiplexes"
          , "medialive:ListNetworks"
          , "medialive:ListReservations"
          , "medialive:ListSdiSources"
          , "medialive:ListSignalMaps"
          , "medialive:ListCloudWatchAlarmTemplateGroups"
          , "medialive:ListCloudWatchAlarmTemplates"
          , "medialive:ListEventBridgeRuleTemplateGroups"
          , "medialive:ListEventBridgeRuleTemplates"
          , "medialive:ListClusters"
          , "medialive:ListNodes"
          , "medialive:ListChannelPlacementGroups"
          , "dax:DescribeClusters"
          , "dax:DescribeParameterGroups"
          , "dax:DescribeSubnetGroups"
          , "license-manager-user-subscriptions:ListIdentityProviders"
          , "license-manager-user-subscriptions:ListInstances"
          , "license-manager-user-subscriptions:ListProductSubscriptions"
          , "license-manager-user-subscriptions:ListUserAssociations"
          , "textract:ListAdapterVersions"
          , "drs:DescribeSourceServers"
          , "drs:DescribeJobs"
          , "drs:DescribeLaunchConfigurationTemplates"
          , "drs:DescribeSourceNetworks"
          , "drs:ListLaunchActions"
          , "schemas:ListRegistries"
          , "schemas:ListSchemas"
          , "schemas:ListDiscoverers"
          , "launchwizard:ListDeployments"
          , "profile:ListDomains"
          , "profile:GetDomain"
          , "profile:ListProfileObjectTypes"
          , "profile:GetProfileObjectType"
          , "profile:ListDomainObjectTypes"
          , "profile:ListCalculatedAttributeDefinitions"
          , "profile:ListEventStreams"
          , "profile:ListEventTriggers"
          , "profile:ListIntegrations"
          , "profile:ListRecommenders"
          , "profile:ListRecommenderSchemas"
          , "profile:ListRecommenderFilters"
          , "sqs:ListQueues"
          , "sqs:GetQueueAttributes"
          , "sqs:ListQueueTags"
          , "secretsmanager:ListSecrets"
          , "secretsmanager:ListSecretVersionIds"
          , "access-analyzer:ListAnalyzers"
          , "access-analyzer:ListArchiveRules"
          , "guardduty:ListDetectors"
          , "guardduty:ListIPSets"
          , "guardduty:ListThreatIntelSets"
          , "guardduty:ListFilters"
          , "securityhub:ListAutomationRules"
          , "securityhub:DescribeActionTargets"
          , "securityhub:GetInsights"
          , "securityhub:ListMembers"
          , "securityhub:GetInvitationsCount"
          , "transfer:ListWebApps"
          , "transfer:ListProfiles"
          , "transfer:ListAccesses"
          , "transfer:DescribeProfile"
          , "transfer:ListWorkflows"
          , "transfer:ListAgreements"
          , "transfer:ListServers"
          , "transfer:ListCertificates"
          , "transfer:ListConnectors"
          , "macie2:ListCustomDataIdentifiers"
          , "macie2:ListFindingsFilters"
          , "macie2:ListMembers"
          , "macie2:GetInvitationsCount"
          , "macie2:ListClassificationJobs"
          , "macie2:DescribeClassificationJob"
          , "inspector2:ListFilters"
          , "elasticfilesystem:DescribeFileSystems"
          , "elasticfilesystem:DescribeAccessPoints"
          , "elasticfilesystem:DescribeMountTargets"
          , "elasticfilesystem:DescribeMountTargetSecurityGroups"
          , "fsx:DescribeFileSystems"
          , "fsx:DescribeFileCaches"
          , "fsx:DescribeBackups"
          , "lakeformation:ListResources"
          , "lakeformation:GetDataLakeSettings"
          , "lakeformation:ListLFTags"
          , "xray:GetGroups"
          , "xray:GetSamplingRules"
          , "appmesh:ListMeshes"
          , "workspaces-web:ListPortals"
          , "workspaces-web:ListTrustStores"
          , "workspaces-web:ListBrowserSettings"
          , "workspaces-web:ListUserSettings"
          , "workspaces-web:ListNetworkSettings"
          , "workspaces-web:ListIpAccessSettings"
          , "workspaces-web:ListDataProtectionSettings"
          , "workspaces-web:ListSessionLoggers"
          , "workspaces-web:ListUserAccessLoggingSettings"
          , "workspaces-web:ListIdentityProviders"
          , "workspaces-web:ListTrustStoreCertificates"
          , "groundstation:ListDataflowEndpointGroups"
          , "groundstation:GetDataflowEndpointGroup"
          , "mediapackage:ListOriginEndpoints"
          , "mediapackage:ListChannels"
          , "mediapackage:ListHarvestJobs"
          , "mediapackage-vod:ListPackagingGroups"
          , "mediapackage-vod:ListPackagingConfigurations"
          , "mediapackage-vod:ListAssets"
          , "mediaconnect:ListEntitlements"
          , "mediaconnect:ListFlows"
          , "mediaconnect:ListBridges"
          , "mediaconnect:DescribeFlow"
          , "mediaconnect:ListRouterInputs"
          , "mediaconnect:ListRouterOutputs"
          , "mediaconnect:ListRouterNetworkInterfaces"
          , "mediapackagev2:ListChannelGroups"
          , "mediapackagev2:ListChannels"
          , "mediapackagev2:ListOriginEndpoints"
          , "servicediscovery:ListNamespaces"
          , "geo:ListTrackers"
          , "geo:ListTrackerConsumers"
          , "geo:ListGeofences"
          , "geo:ListGeofenceCollections"
          , "geo:ListMaps"
          , "geo:ListKeys"
          , "geo:ListPlaceIndexes"
          , "geo:ListRouteCalculators"
          , "app-integrations:ListApplications"
          , "app-integrations:ListEventIntegrations"
          , "app-integrations:ListDataIntegrations"
          , "app-integrations:ListDataIntegrationAssociations"
          , "app-integrations:ListEventIntegrationAssociations"
          , "iotevents:ListAlarmModels"
          , "iotanalytics:ListPipelines"
          , "iotanalytics:ListChannels"
          , "iotanalytics:ListDatasets"
          , "iotanalytics:ListDatastores"
          , "pcs:ListClusters"
          , "grafana:ListWorkspaces"
          , "oam:ListLinks"
          , "networkmonitor:ListMonitors"
          , "gameliftstreams:ListApplications"
          , "gameliftstreams:ListStreamGroups"
          , "dsql:ListClusters"
          , "payment-cryptography:ListKeys"
          , "payment-cryptography:ListAliases"
          , "pca-connector-ad:ListConnectors"
          , "pca-connector-ad:ListTemplates"
          , "pca-connector-ad:ListTemplateGroupAccessControlEntries"
          , "pca-connector-scep:ListConnectors"
          , "pca-connector-scep:ListChallengeMetadata"
          , "serverlessrepo:ListApplications"
          , "swf:ListDomains"
          , "cloudhsm:DescribeClusters"
          , "kafka:ListConfigurations"
          , "kafka:ListConfigurationRevisions"
          , "kafka:ListReplicators"
          , "kinesisanalytics:ListApplications"
          , "kafka:ListClustersV2"
          , "license-manager:ListLicenseConfigurations"
          , "license-manager:ListLicenses"
          , "license-manager:ListLicenseAssetGroups"
          , "license-manager:ListLicenseAssetRulesets"
          , "license-manager:ListDistributedGrants"
          , "license-manager:ListTokens"
          , "license-manager:ListReceivedLicenses"
          , "license-manager:ListAssociationsForLicenseConfiguration"
          , "license-manager:ListLicenseManagerReportGenerators"
          , "proton:ListServices"
          , "proton:ListEnvironments"
          , "proton:ListEnvironmentTemplates"
          , "proton:ListServiceTemplates"
          , "proton:ListEnvironmentAccountConnections"
          , "proton:ListComponents"
          , "proton:ListEnvironmentTemplateVersions"
          , "proton:ListServiceTemplateVersions"
          , "proton:ListServiceInstances"
          , "imagebuilder:ListLifecyclePolicies"
          , "fms:ListPolicies"
          , "fms:GetPolicy"
          , "fms:ListAppsLists"
          , "fms:ListProtocolsLists"
          , "fms:ListResourceSets"
          , "fms:ListResourceSetResources"
          , "fms:ListAdminAccountsForOrganization"
          , "fms:ListMemberAccounts"
          , "network-firewall:DescribeRuleGroup"
          , "wafv2:GetRuleGroup"
          , "wafv2:DescribeManagedRuleGroup"
          , "kafkaconnect:ListCustomPlugins"
          , "rolesanywhere:ListProfiles"
          , "rolesanywhere:ListTrustAnchors"
          , "internetmonitor:ListMonitors"
          , "internetmonitor:GetMonitor"
          , "imagebuilder:ListComponents"
          , "imagebuilder:ListWorkflows"
          , "oam:ListSinks"
          , "route53profiles:ListProfiles"
          , "route53profiles:ListProfileAssociations"
          , "route53profiles:ListProfileResourceAssociations"
          , "docdb-elastic:ListClusters"
          , "databrew:ListProjects"
          , "databrew:ListDatasets"
          , "databrew:ListRulesets"
          , "databrew:ListSchedules"
          , "databrew:ListRecipes"
          , "cognito-identity:ListIdentityPools"
          , "wellarchitected:ListWorkloads"
          , "social-messaging:ListLinkedWhatsAppBusinessAccounts"
          , "ssm-quicksetup:ListConfigurationManagers"
          , "ssm-sap:ListApplications"
          , "sso:ListInstances"
          , "sso:ListPermissionSets"
          , "identitystore:ListUsers"
          , "identitystore:ListGroups"
          , "servicecatalog:ListApplications"
          , "servicecatalog:ListAttributeGroups"
          , "servicecatalog:ListAttributeGroupsForApplication"
          , "servicecatalog:ListAssociatedResources"
          , "scn:ListInstances"
          , "timestream-influxdb:ListDbInstances"
          , "workspaces:DescribeIpGroups"
          , "workspaces:DescribeWorkspaceDirectories"
          , "workspaces:DescribeConnectionAliases"
          , "s3:ListAllMyBuckets"
          , "s3:ListRegionalBuckets"
          , "s3:GetReplicationConfiguration"
          , "s3:GetLifecycleConfiguration"
          , "s3:GetBucketNotification"
          , "s3:GetBucketTagging"
          , "sns:GetSubscriptionAttributes"
          , "sns:ListSubscriptionsByTopic"
          , "wellarchitected:ListLenses"
          , "wellarchitected:ListReviewTemplates"
          , "ssm-contacts:ListContacts"
          , "ssm-contacts:ListRotations"
          , "ssm-contacts:GetContact"
          , "dataexchange:ListDataSets"
          , "dataexchange:ListEventActions"
          , "dataexchange:ListDataSetRevisions"
          , "dataexchange:ListRevisionAssets"
          , "dataexchange:ListJobs"
          , "dataexchange:ListDataGrants"
          , "cloudformation:ListStackInstances"
          , "cloudwatch:DescribeAnomalyDetectors"
          , "application-autoscaling:DescribeScalableTargets"
          , "application-autoscaling:DescribeScheduledActions"
          , "application-autoscaling:DescribeScalingPolicies"
          , "rbin:ListRules"
          , "rbin:GetRule"
          , "discovery:ListConfigurations"
          , "ssm-incidents:ListReplicationSets"
          , "workspaces-instances:ListWorkspaceInstances"
          , "repostspace:ListSpaces"
          , "evidently:ListProjects"
          , "ram:GetResourceShares"
          , "acm-pca:ListCertificateAuthorities"
          , "athena:ListWorkGroups"
          , "scheduler:ListSchedules"
          , "scheduler:ListScheduleGroups"
          , "application-signals:ListServiceLevelObjectives"
          , "cleanrooms:ListMembers"
          , "servicediscovery:ListServices"
          , "servicediscovery:GetInstance"
          , "iot:ListRoleAliases"
          , "wisdom:ListKnowledgeBases"
          , "wisdom:ListAssistants"
          , "wisdom:ListAssistantAssociations"
          , "wisdom:ListMessageTemplates"
          , "wisdom:ListMessageTemplateVersions"
          , "wisdom:ListContents"
          , "voiceid:ListWatchlists"
          , "voiceid:ListSpeakers"
          , "voiceid:ListFraudsterRegistrationJobs"
          , "voiceid:ListSpeakerEnrollmentJobs"
          , "ssm:DescribeMaintenanceWindowTasks"
          , "ssm:DescribeMaintenanceWindowTargets"
          , "swf:ListWorkflowTypes"
          , "swf:ListActivityTypes"
          , "swf:CountOpenWorkflowExecutions"
          , "vpc-lattice:ListListeners"
          , "vpc-lattice:ListRules"
          , "vpc-lattice:ListTargets"
          , "vpc-lattice:ListResourceConfigurations"
          , "vpc-lattice:ListResourceGateways"
          , "vpc-lattice:ListDomainVerifications"
          , "vpc-lattice:ListServiceNetworkServiceAssociations"
          , "vpc-lattice:ListServiceNetworkVpcAssociations"
          , "vpc-lattice:GetServiceNetworkVpcAssociation"
          , "vpc-lattice:ListServiceNetworkVpcEndpointAssociations"
          , "vpc-lattice:ListServiceNetworkResourceAssociations"
          , "wafv2:GetIPSet"
          , "wafv2:GetRegexPatternSet"
          , "wafv2:ListResourcesForWebACL"
          , "wafv2:GetWebACL"
          , "waf-regional:ListWebACLs"
          , "waf-regional:GetWebACL"
          , "waf-regional:ListRegexPatternSets"
          , "waf-regional:GetRegexPatternSet"
          , "waf-regional:ListRules"
          , "waf-regional:GetRule"
          , "waf-regional:ListRateBasedRules"
          , "waf-regional:ListGeoMatchSets"
          , "waf-regional:GetGeoMatchSet"
          , "waf-regional:ListIPSets"
          , "waf-regional:GetIPSet"
          , "waf-regional:ListSizeConstraintSets"
          , "waf-regional:GetSizeConstraintSet"
          , "waf-regional:ListSqlInjectionMatchSets"
          , "waf-regional:GetSqlInjectionMatchSet"
          , "waf-regional:ListXssMatchSets"
          , "waf-regional:GetXssMatchSet"
          , "waf-regional:ListByteMatchSets"
          , "waf-regional:GetByteMatchSet"
          , "waf-regional:ListRegexMatchSets"
          , "waf-regional:GetRegexMatchSet"
          , "waf-regional:ListLoggingConfigurations"
          , "servicediscovery:ListInstances"
          , "aps:ListWorkspaces"
          , "voiceid:ListDomains"
          , "aoss:ListSecurityConfigs"
          , "aoss:ListSecurityPolicies"
          , "aoss:ListAccessPolicies"
          , "aoss:GetSecurityConfig"
          , "aoss:GetSecurityPolicy"
          , "aoss:GetAccessPolicy"
          , "aoss:ListLifecyclePolicies"
          , "aoss:BatchGetLifecyclePolicy"
          , "aoss:ListCollectionGroups"
          , "aoss:GetAccountSettings"
          , "outposts:ListSites"
          , "vpc-lattice:ListServiceNetworks"
          , "vpc-lattice:ListServices"
          , "vpc-lattice:ListTargetGroups"
          , "thinclient:ListEnvironments"
          , "appmesh:ListVirtualServices"
          , "appmesh:ListVirtualGateways"
          , "appmesh:ListVirtualRouters"
          , "appmesh:ListVirtualNodes"
          , "appmesh:ListRoutes"
          , "appmesh:ListGatewayRoutes"
          , "redshift:DescribeClusters"
          , "redshift:DescribeClusterSnapshots"
          , "redshift:DescribeClusterParameterGroups"
          , "redshift:DescribeClusterSubnetGroups"
          , "redshift:DescribeEventSubscriptions"
          , "redshift:DescribeReservedNodes"
          , "timestream:ListDatabases"
          , "timestream:ListTables"
          , "timestream:ListScheduledQueries"
          , "rds:DescribeDBInstances"
          , "rds:DescribeDBEngineVersions"
          , "rds:DescribeDBClusters"
          , "rds:DescribeDBSubnetGroups"
          , "rds:DescribeDBProxies"
          , "rds:DescribeDBClusterParameterGroups"
          , "rds:DescribeDBParameterGroups"
          , "rds:DescribeOptionGroups"
          , "rds:DescribeDBSnapshots"
          , "rds:DescribeDBClusterSnapshots"
          , "rds:DescribeDBShardGroups"
          , "rds:DescribeDBClusterEndpoints"
          , "rds:DescribeEventSubscriptions"
          , "rds:DescribeDBSecurityGroups"
          , "rds:DescribeIntegrations"
          , "rds:DescribeReservedDBInstances"
          , "transcribe:ListVocabularies"
          , "transcribe:ListMedicalVocabularies"
          , "transcribe:ListVocabularyFilters"
          , "transcribe:ListLanguageModels"
          , "transcribe:ListTranscriptionJobs"
          , "transcribe:ListMedicalTranscriptionJobs"
          , "transcribe:ListCallAnalyticsJobs"
          , "transcribe:ListCallAnalyticsCategories"
          , "polly:ListLexicons"
          , "lex:ListBots"
          , "lex:ListBotVersions"
          , "lex:ListBotLocales"
          , "lex:ListIntents"
          , "lex:DescribeIntent"
          , "lex:ListSlots"
          , "lex:DescribeSlot"
          , "lex:ListSlotTypes"
          , "lex:DescribeSlotType"
          , "network-firewall:ListFirewalls"
          , "network-firewall:DescribeFirewall"
          , "network-firewall:ListFirewallPolicies"
          , "network-firewall:DescribeFirewallPolicy"
          , "network-firewall:ListRuleGroups"
          , "network-firewall:ListTLSInspectionConfigurations"
          , "network-firewall:DescribeTLSInspectionConfiguration"
          , "network-firewall:ListVpcEndpointAssociations"
          , "network-firewall:DescribeVpcEndpointAssociation"
          , "network-firewall:ListContainerAssociations"
          , "network-firewall:DescribeContainerAssociation"
          , "ec2:DescribeNetworkInsightsAccessScopes"
          , "ec2:DescribeNetworkInsightsAccessScopeAnalyses"
          , "ec2:DescribeNetworkInsightsPaths"
          , "ec2:DescribeNetworkInsightsAnalyses"
          , "ses:ListTenants"
          , "ses:ListConfigurationSets"
          , "connect:ListInstances"
          , "connect:ListContactFlows"
          , "connect:ListQueues"
          , "connect:ListQuickConnects"
          , "connect:ListSecurityProfiles"
          , "connect:ListHoursOfOperations"
          , "dlm:GetLifecyclePolicies"
          , "dlm:GetLifecyclePolicy"
          , "glacier:ListVaults"
          , "wellarchitected:GetReviewTemplate"
          , "wellarchitected:GetWorkload"
          , "wellarchitected:ListMilestones"
          , "connect:ListUserHierarchyGroups"
          , "connect:ListUsers"
          , "connect:ListRoutingProfiles"
          , "connect:ListPhoneNumbers"
          , "connect:ListPrompts"
          , "connect:ListContactFlowModules"
          , "connect:ListLexBots"
          , "connect:ListIntegrationAssociations"
          , "connect:ListBots"
          , "connect:ListLambdaFunctions"
          , "connect:ListDataTables"
          , "connect:ListDataTableValues"
          , "connect:ListAgentStatuses"
          , "connect:ListQueueEmailAddresses"
          , "connect:ListWorkspaces"
          , "connect:ListNotifications"
          , "connect:SearchEmailAddresses"
          , "connect:ListPredefinedAttributes"
          , "connect:ListHoursOfOperationOverrides"
          , "connect:ListUserProficiencies"
          , "connect:ListRoutingProfileQueues"
          , "connect:ListRoutingProfileManualAssignmentQueues"
          , "connect:ListDataTableAttributes"
          , "mobiletargeting:ListTemplates"
          , "mobiletargeting:ListTemplateVersions"
          , "auditmanager:ListAssessmentFrameworks"
          , "auditmanager:ListControls"
          , "auditmanager:ListAssessments"
          , "auditmanager:GetAssessment"
          , "auditmanager:GetAssessmentFramework"
          , "resiliencehub:ListApps"
          , "resiliencehub:ListResiliencyPolicies"
          , "resiliencehub:ListAppVersions"
          , "resiliencehub:ListAppVersionAppComponents"
          , "resiliencehub:ListAppVersionResources"
          , "resiliencehub:ListAppAssessments"
          , "resiliencehub:ListRecommendationTemplates"
          , "resiliencehub:ListServices"
          , "resiliencehub:ListSystems"
          , "resiliencehub:ListPolicies"
          , "resiliencehub:ListResources"
          , "resiliencehub:ListInputSources"
          , "resiliencehub:ListServiceFunctions"
          , "resiliencehub:ListFailureModeAssessments"
          , "resiliencehub:ListUserJourneys"
          , "storagegateway:ListGateways"
          , "storagegateway:ListVolumes"
          , "storagegateway:ListFileShares"
          , "storagegateway:ListTapes"
          , "storagegateway:DescribeCache"
          , "storagegateway:DescribeUploadBuffer"
          , "omics:ListWorkflows"
          , "omics:ListSequenceStores"
          , "omics:ListVariantStores"
          , "omics:ListAnnotationStores"
          , "omics:ListConfigurations"
          , "omics:ListRuns"
          , "omics:ListRunTasks"
          , "omics:ListReadSets"
          , "omics:ListReferenceStores"
          , "omics:ListReferences"
          , "omics:ListAnnotationStoreVersions"
          , "omics:ListShares"
          , "omics:ListVariantImportJobs"
          , "omics:ListAnnotationImportJobs"
          , "omics:ListReadSetImportJobs"
          , "omics:ListReferenceImportJobs"
          , "omics:ListReadSetExportJobs"
          , "omics:ListReadSetActivationJobs"
          , "iotfleetwise:ListVehicles"
          , "iotfleetwise:ListFleets"
          , "iotfleetwise:ListVehiclesInFleet"
          , "iotfleetwise:ListCampaigns"
          , "iotfleetwise:ListSignalCatalogs"
          , "iotfleetwise:ListModelManifests"
          , "iotfleetwise:ListDecoderManifests"
          , "iotfleetwise:ListStateTemplates"
          , "forecast:ListPredictors"
          , "forecast:ListDatasetImportJobs"
          , "forecast:DescribeDatasetGroup"
          , "forecast:ListDatasetGroups"
          , "forecast:ListDatasets"
          , "forecast:ListForecasts"
          , "forecast:ListExplainabilities"
          , "forecast:ListWhatIfAnalyses"
          , "forecast:ListWhatIfForecasts"
          , "forecast:ListForecastExportJobs"
          , "forecast:ListExplainabilityExports"
          , "forecast:ListWhatIfForecastExports"
          , "forecast:ListPredictorBacktestExportJobs"
          , "mobiletargeting:GetApps"
          , "mobiletargeting:GetCampaigns"
          , "mobiletargeting:ListJourneys"
          , "mobiletargeting:GetImportJobs"
          , "deadline:ListFarms"
          , "deadline:ListLimits"
          , "deadline:ListQueueFleetAssociations"
          , "deadline:ListQueueLimitAssociations"
          , "deadline:ListQueueEnvironments"
          , "deadline:ListFarmMembers"
          , "deadline:ListFleetMembers"
          , "deadline:ListQueueMembers"
          , "deadline:ListMonitors"
          , "deadline:ListLicenseEndpoints"
          , "deadline:ListFleets"
          , "deadline:ListQueues"
          , "deadline:ListWorkers"
          , "deadline:ListJobs"
          , "deadline:ListBudgets"
          , "deadline:ListStorageProfiles"
          , "appconfig:ListApplications"
          , "appconfig:ListDeploymentStrategies"
          , "appconfig:ListConfigurationProfiles"
          , "appconfig:ListEnvironments"
          , "resource-groups:ListGroups"
          , "cloudformation:ListStacks"
          , "cloudformation:ListStackSets"
          , "cloudformation:ListTypes"
          , "cloudformation:ListTypeVersions"
          , "cloudformation:GetTemplate"
          , "cloudformation:DescribeStackSet"
          , "cloudformation:ListStackSetOperations"
          , "fis:ListExperimentTemplates"
          , "fis:GetExperimentTemplate"
          , "fis:ListExperiments"
          , "fis:GetExperiment"
          , "fis:ListExperimentResolvedTargets"
          , "servicecatalog:ListPortfolios"
          , "servicecatalog:SearchProductsAsAdmin"
          , "wafv2:ListWebACLs"
          , "wafv2:ListIPSets"
          , "wafv2:ListRegexPatternSets"
          , "wafv2:ListRuleGroups"
          , "acm:ListCertificates"
          , "cognito-idp:ListUserPools"
          , "cognito-idp:ListUserPoolClients"
          , "cognito-idp:ListGroups"
          , "cognito-idp:ListIdentityProviders"
          , "cognito-idp:ListResourceServers"
          , "cognito-idp:DescribeUserPool"
          , "backup:ListBackupVaults"
          , "backup:ListBackupJobs"
          , "backup:ListCopyJobs"
          , "backup:ListBackupPlans"
          , "backup:ListFrameworks"
          , "backup:ListReportPlans"
          , "backup:DescribeFramework"
          , "backup:DescribeReportPlan"
          , "glue:GetCrawlers"
          , "glue:GetDatabases"
          , "glue:GetJobs"
          , "glue:ListWorkflows"
          , "glue:GetConnections"
          , "glue:GetTriggers"
          , "glue:GetTables"
          , "glue:GetTableVersions"
          , "glue:GetSecurityConfigurations"
          , "glue:GetMLTransforms"
          , "glue:ListRegistries"
          , "glue:ListSchemas"
          , "glue:ListSchemaVersions"
          , "glue:QuerySchemaVersionMetadata"
          , "glue:GetUserDefinedFunctions"
          , "glue:GetPartitions"
          , "glue:GetDevEndpoints"
          , "glue:GetCatalogs"
          , "glue:DescribeIntegrations"
          , "glue:ListDataQualityRulesets"
          , "glue:GetJobRuns"
          , "glue:GetMLTaskRuns"
          , "glue:ListDataQualityRulesetEvaluationRuns"
          , "glue:ListDataQualityRuleRecommendationRuns"
          , "glue:ListMaterializedViewRefreshTaskRuns"
          , "glue:ListColumnStatisticsTaskRuns"
          , "glue:GetColumnStatisticsTaskRun"
          , "lakeformation:ListLFTagExpressions"
          , "elasticmapreduce:ListClusters"
          , "datasync:ListTasks"
          , "sagemaker:ListNotebookInstances"
          , "sagemaker:ListPipelines"
          , "codebuild:ListProjects"
          , "codebuild:BatchGetProjects"
          , "codebuild:ListBuilds"
          , "codebuild:BatchGetBuilds"
          , "codepipeline:ListPipelines"
          , "codepipeline:GetPipeline"
          , "codepipeline:ListPipelineExecutions"
          , "codepipeline:ListActionTypes"
          , "codepipeline:ListWebhooks"
          , "codeartifact:ListDomains"
          , "codeartifact:ListRepositoriesInDomain"
          , "logs:DescribeLogGroups"
          , "logs:DescribeResourcePolicies"
          , "logs:DescribeSubscriptionFilters"
          , "logs:DescribeMetricFilters"
          , "dynamodb:ListTables"
          , "elasticache:DescribeCacheSubnetGroups"
          , "elasticache:DescribeUsers"
          , "elasticache:DescribeCacheParameterGroups"
          , "elasticache:DescribeUserGroups"
          , "elasticache:DescribeServerlessCaches"
          , "rekognition:ListProjectPolicies"
          , "rekognition:ListStreamProcessors"
          , "rekognition:DescribeStreamProcessor"
          , "rekognition:ListMediaAnalysisJobs"
          , "elasticmapreduce:ListInstanceGroups"
          , "redshift:DescribeClusterSecurityGroups"
          , "logs:ListLogAnomalyDetectors"
          , "kinesis:ListStreams"
          , "kinesis:ListShards"
          , "sagemaker:ListEndpoints"
          , "sagemaker:ListTrainingJobs"
          , "sagemaker:DescribeTrainingJob"
          , "sagemaker:ListProcessingJobs"
          , "sagemaker:DescribeProcessingJob"
          , "sagemaker:DescribeEndpointConfig"
          , "sagemaker:DescribeEndpoint"
          , "bedrock:ListKnowledgeBases"
          , "bedrock:ListAgents"
          , "bedrock:ListFlows"
          , "bedrock:ListFlowExecutions"
          , "bedrock:ListPrompts"
          , "bedrock:ListDataSources"
          , "bedrock:ListAgentAliases"
          , "bedrock:ListAgentActionGroups"
          , "bedrock:ListAgentKnowledgeBases"
          , "bedrock:ListAgentCollaborators"
          , "bedrock:GetAgentActionGroup"
          , "bedrock:ListFlowAliases"
          , "bedrock:ListFlowVersions"
          , "bedrock:ListBlueprints"
          , "bedrock:GetBlueprint"
          , "bedrock:ListDataAutomationProjects"
          , "bedrock:GetDataAutomationProject"
          , "bedrock:ListDataAutomationLibraries"
          , "bedrock:ListDataAutomationLibraryEntities"
          , "bedrock:ListCustomModels"
          , "bedrock:ListModelInvocationJobs"
          , "bedrock:GetInferenceProfile"
          , "bedrock:GetCustomModel"
          , "bedrock:GetFoundationModel"
          , "bedrock:ListGuardrails"
          , "bedrock:GetGuardrail"
          , "bedrock:GetFlow"
          , "bedrock:GetFlowVersion"
          , "bedrock:ListImportedModels"
          , "bedrock:ListInferenceProfiles"
          , "bedrock:ListAdvancedPromptOptimizationJobs"
          , "bedrock:ListAutomatedReasoningPolicies"
          , "bedrock:ListAutomatedReasoningPolicyBuildWorkflows"
          , "bedrock:ListProvisionedModelThroughputs"
          , "bedrock:ListIngestionJobs"
          , "bedrock:ExportAutomatedReasoningPolicyVersion"
          , "bedrock:ListAutomatedReasoningPolicyTestCases"
          , "bedrock:ListEvaluationJobs"
          , "bedrock:GetEvaluationJob"
          , "bedrock:ListModelImportJobs"
          , "rekognition:DescribeProjects"
          , "rekognition:DescribeProjectVersions"
          , "comprehend:ListEndpoints"
          , "comprehend:ListDocumentClassificationJobs"
          , "comprehend:ListDominantLanguageDetectionJobs"
          , "comprehend:ListEntitiesDetectionJobs"
          , "comprehend:ListEventsDetectionJobs"
          , "comprehend:ListKeyPhrasesDetectionJobs"
          , "comprehend:ListPiiEntitiesDetectionJobs"
          , "comprehend:ListSentimentDetectionJobs"
          , "comprehend:ListTargetedSentimentDetectionJobs"
          , "comprehend:ListTopicsDetectionJobs"
          , "comprehend:ListDocumentClassifiers"
          , "comprehend:ListEntityRecognizers"
          , "comprehend:ListFlywheels"
          , "comprehend:ListDatasets"
          , "comprehend:ListFlywheelIterationHistory"
          , "textract:ListAdapters"
          , "directconnect:DescribeDirectConnectGateways"
          , "directconnect:DescribeLags"
          , "directconnect:DescribeConnections"
          , "directconnect:DescribeVirtualInterfaces"
          , "iot:ListThingGroups"
          , "iot:ListJobTemplates"
          , "iot:ListScheduledAudits"
          , "iot:ListMitigationActions"
          , "iot:ListCustomMetrics"
          , "iot:ListStreams"
          , "iot:ListFleetMetrics"
          , "iot:DescribeFleetMetric"
          , "iot:GetIndexingConfiguration"
          , "iot:ListProvisioningTemplates"
          , "iot:ListProvisioningTemplateVersions"
          , "iot:ListPolicies"
          , "iot:ListPolicyVersions"
          , "iot:ListAuthorizers"
          , "iot:ListTopicRules"
          , "iot:GetTopicRule"
          , "iot:ListDomainConfigurations"
          , "iot:ListTopicRuleDestinations"
          , "iot:ListV2LoggingLevels"
          , "iot:ListThingRegistrationTasks"
          , "iot:DescribeThingGroup"
          , "iot:ListJobs"
          , "iot:DescribeJob"
          , "iot:ListCommands"
          , "iot:GetCommand"
          , "iot:ListCommandExecutions"
          , "iot:ListDimensions"
          , "iot:ListSecurityProfiles"
          , "iot:DescribeSecurityProfile"
          , "iot:ListTargetsForSecurityProfile"
          , "iot:DescribeStream"
          , "iot:ListAuditTasks"
          , "gamelift:DescribeFleetAttributes"
          , "gamelift:DescribeRuntimeConfiguration"
          , "gamelift:DescribeFleetLocationAttributes"
          , "gamelift:ListCompute"
          , "gamelift:ListGameServers"
          , "gamelift:ListGameServerGroups"
          , "gamelift:ListBuilds"
          , "gamelift:DescribeGameSessionQueues"
          , "gamelift:ListAliases"
          , "gamelift:ListScripts"
          , "gamelift:ListLocations"
          , "gamelift:DescribeMatchmakingConfigurations"
          , "gamelift:DescribeMatchmakingRuleSets"
          , "appstream:DescribeFleets"
          , "appstream:DescribeStacks"
          , "appstream:DescribeImages"
          , "appstream:DescribeImageBuilders"
          , "appstream:DescribeAppBlockBuilders"
          , "appstream:DescribeImagePermissions"
          , "appstream:DescribeUsers"
          , "appstream:ListAssociatedStacks"
          , "appstream:DescribeSessions"
          , "bedrock-agentcore:GetMemory"
          , "bedrock-agentcore:ListAgentRuntimeEndpoints"
          , "bedrock-agentcore:ListAgentRuntimeVersions"
          , "bedrock-agentcore:ListAgentRuntimes"
          , "bedrock-agentcore:ListApiKeyCredentialProviders"
          , "bedrock-agentcore:ListBrowserProfiles"
          , "bedrock-agentcore:ListBrowserSessions"
          , "bedrock-agentcore:ListBrowsers"
          , "bedrock-agentcore:ListCodeInterpreterSessions"
          , "bedrock-agentcore:ListCodeInterpreters"
          , "bedrock-agentcore:ListGatewayRateLimits"
          , "bedrock-agentcore:ListGatewayTargets"
          , "bedrock-agentcore:ListGateways"
          , "bedrock-agentcore:ListMemories"
          , "bedrock-agentcore:ListOauth2CredentialProviders"
          , "bedrock-agentcore:ListPaymentConnectors"
          , "bedrock-agentcore:ListPaymentCredentialProviders"
          , "bedrock-agentcore:ListPaymentManagers"
          , "bedrock-agentcore:ListPolicies"
          , "bedrock-agentcore:ListPolicyEngines"
          , "bedrock-agentcore:ListPolicyGenerations"
          , "bedrock-agentcore:ListWorkloadIdentities"
          , "appsync:ListGraphqlApis"
          , "appsync:ListApis"
          , "appsync:ListApiKeys"
          , "appsync:ListTypes"
          , "appsync:ListResolvers"
          , "appsync:ListChannelNamespaces"
          , "appsync:ListSourceApiAssociations"
          , "config:DescribeConfigRules"
          , "dms:DescribeEndpoints"
          , "dms:DescribeReplicationInstances"
          , "dms:DescribeReplicationTasks"
          , "dms:DescribeCertificates"
          , "dms:DescribeReplicationSubnetGroups"
          , "dms:DescribeMigrationProjects"
          , "dms:DescribeDataProviders"
          , "dms:DescribeDataMigrations"
          , "dms:DescribeEventSubscriptions"
          , "dms:DescribeReplications"
          , "dms:DescribeFleetAdvisorCollectors"
          , "dms:DescribeInstanceProfiles"
          , "mgn:ListApplications"
          , "mgn:ListWaves"
          , "mgn:DescribeSourceServers"
          , "mgn:DescribeJobs"
          , "mgn:ListSourceServerActions"
          , "mgn:DescribeLaunchConfigurationTemplates"
          , "mgn:ListTemplateActions"
          , "mgn:ListNetworkMigrationDefinitions"
          , "groundstation:ListConfigs"
          , "groundstation:ListMissionProfiles"
          , "iotsitewise:ListAssetModels"
          , "iotsitewise:ListPortals"
          , "iotsitewise:ListProjects"
          , "iotsitewise:ListDashboards"
          , "iotsitewise:ListProjectAssets"
          , "iotsitewise:ListGateways"
          , "iotsitewise:DescribeAssetModel"
          , "iotsitewise:ListAssetModelProperties"
          , "iotsitewise:ListAssetModelCompositeModels"
          , "iotsitewise:DescribeAssetModelCompositeModel"
          , "iotsitewise:ListCompositionRelationships"
          , "iotsitewise:ListInterfaceRelationships"
          , "iotsitewise:ListAssets"
          , "iotsitewise:ListAssociatedAssets"
          , "iotsitewise:ListBulkImportJobs"
          , "iotsitewise:ListWorkspaces"
          , "iotsitewise:ListEnrichmentJobs"
          , "iottwinmaker:ListWorkspaces"
          , "iottwinmaker:ListEntities"
          , "iottwinmaker:ListScenes"
          , "iottwinmaker:ListComponentTypes"
          , "iottwinmaker:GetComponentType"
          , "robomaker:ListSimulationApplications"
          , "robomaker:ListRobotApplications"
          , "workspaces:DescribeWorkspaceImages"
          , "workspaces:DescribeWorkspaceBundles"
          , "workspaces:DescribeWorkspaces"
          , "finspace:ListKxEnvironments"
          , "finspace:ListKxClusters"
          , "finspace:GetKxCluster"
          , "finspace:ListKxClusterNodes"
          , "finspace:ListKxScalingGroups"
          , "finspace:ListKxUsers"
          , "finspace:ListKxVolumes"
          , "finspace:GetKxVolume"
          , "finspace:ListKxDatabases"
          , "finspace:ListKxDataviews"
          , "imagebuilder:ListImageRecipes"
          , "imagebuilder:GetImageRecipe"
          , "imagebuilder:ListContainerRecipes"
          , "imagebuilder:GetContainerRecipe"
          , "imagebuilder:ListDistributionConfigurations"
          , "imagebuilder:GetDistributionConfiguration"
          , "imagebuilder:ListImagePipelines"
          , "imagebuilder:ListInfrastructureConfigurations"
          , "imagebuilder:GetComponent"
          , "imagebuilder:GetWorkflow"
          , "m2:ListApplications"
          , "m2:ListEnvironments"
          , "entityresolution:ListMatchingWorkflows"
          , "entityresolution:ListMatchingJobs"
          , "entityresolution:ListIdMappingJobs"
          , "entityresolution:ListIdMappingWorkflows"
          , "entityresolution:ListIdNamespaces"
          , "entityresolution:ListSchemaMappings"
          , "datazone:ListDomains"
          , "datazone:Search"
          , "datazone:SearchTypes"
          , "datazone:ListEnvironments"
          , "datazone:ListProjects"
          , "datazone:ListConnections"
          , "apprunner:ListServices"
          , "apprunner:ListConnections"
          , "apprunner:ListAutoScalingConfigurations"
          , "apprunner:ListVpcIngressConnections"
          , "apprunner:ListObservabilityConfigurations"
          , "apprunner:ListVpcConnectors"
          , "amplify:ListApps"
          , "amplify:ListBackendEnvironments"
          , "amplify:ListDomainAssociations"
          , "amplify:ListBranches"
          , "amplify:ListWebhooks"
          , "cases:ListDomains"
          , "cases:ListTemplates"
          , "cases:ListCaseRules"
          , "cases:ListFields"
          , "cases:ListFieldOptions"
          , "cases:ListLayouts"
          , "cases:GetLayout"
          , "cases:SearchAllRelatedItems"
          , "cases:BatchGetCaseRule"
          , "cases:GetTemplate"
          , "airflow:ListEnvironments"
          , "amplifyuibuilder:ListThemes"
          , "amplifyuibuilder:ListViews"
          , "amplifyuibuilder:ListComponents"
          , "amplifyuibuilder:ListForms"
          , "evs:ListEnvironments"
          , "evs:ListEnvironmentHosts"
          , "servicecatalog:ListServiceActions"
          , "servicecatalog:ListProvisioningArtifacts"
          , "servicecatalog:ListServiceActionsForProvisioningArtifact"
          , "servicecatalog:ListPortfolioAccess"
          , "servicecatalog:ListPrincipalsForPortfolio"
          , "servicecatalog:ListTagOptions"
          , "servicecatalog:DescribePortfolio"
          , "servicecatalog:DescribeProductAsAdmin"
          , "lightsail:GetInstances"
          , "lightsail:GetRelationalDatabases"
          , "lightsail:GetContainerServices"
          , "lightsail:GetDistributions"
          , "lightsail:GetLoadBalancers"
          , "lightsail:GetBuckets"
          , "lightsail:GetCertificates"
          , "lightsail:GetDisks"
          , "lightsail:GetContainerServiceDeployments"
          , "lightsail:GetContainerImages"
          , "mediastore:ListContainers"
          , "mediatailor:ListSourceLocations"
          , "mediatailor:DescribeSourceLocation"
          , "mediatailor:ListPlaybackConfigurations"
          , "mediatailor:ListChannels"
          , "kinesisvideo:ListStreams"
          , "kinesisvideo:ListSignalingChannels"
          , "codedeploy:ListApplications"
          , "codedeploy:ListDeploymentGroups"
          , "codedeploy:GetDeploymentGroup"
          , "codedeploy:ListDeployments"
          , "codedeploy:ListDeploymentConfigs"
          , "codedeploy:BatchGetDeployments"
          , "codedeploy:ListDeploymentTargets"
          , "codedeploy:ListGitHubAccountTokenNames"
          , "cassandra:ListTables"
          , "cassandra:ListKeyspaces"
          , "cassandra:ListTypes"
          , "cassandra:GetType"
          , "qldb:ListLedgers"
          , "refactor-spaces:ListEnvironments"
          , "refactor-spaces:ListApplications"
          , "refactor-spaces:ListServices"
          , "refactor-spaces:ListRoutes"
          , "cloud9:ListEnvironments"
          , "resource-explorer-2:ListViews"
          , "neptune-graph:ListGraphs"
          , "mq:ListBrokers"
          , "mq:DescribeBroker"
          , "mq:ListConfigurations"
          , "mq:ListConfigurationRevisions"
          , "elasticloadbalancing:DescribeAccountLimits"
          , "elasticloadbalancing:DescribeLoadBalancers"
          , "elasticloadbalancing:DescribeTargetGroups"
          , "elasticloadbalancing:DescribeListeners"
          , "elasticloadbalancing:DescribeRules"
          , "elasticloadbalancing:DescribeTargetHealth"
          , "elasticloadbalancing:DescribeListenerCertificates"
          , "elasticloadbalancing:DescribeTrustStores"
          , "elasticloadbalancing:DescribeTrustStoreRevocations"
          , "elasticloadbalancing:DescribeTrustStoreAssociations"
          , "elasticloadbalancing:DescribeCapacityReservation"
          , "ds:DescribeDirectories"
          , "es:ListDomainNames"
          , "es:ListApplications"
          , "elasticbeanstalk:DescribeApplications"
          , "elasticbeanstalk:DescribeEnvironments"
          , "elasticbeanstalk:DescribeApplicationVersions"
          , "elasticbeanstalk:ListPlatformVersions"
          , "batch:DescribeJobQueues"
          , "batch:DescribeComputeEnvironments"
          , "s3:ListAccessPoints"
          , "s3:ListMultiRegionAccessPoints"
          , "codeguru-profiler:ListProfilingGroups"
          , "memorydb:DescribeClusters"
          , "memorydb:DescribeACLs"
          , "memorydb:DescribeUsers"
          , "memorydb:DescribeSubnetGroups"
          , "memorydb:DescribeParameterGroups"
          , "personalize:ListDatasetGroups"
          , "personalize:ListCampaigns"
          , "personalize:ListSolutions"
          , "personalize:ListRecommenders"
          , "personalize:ListSchemas"
          , "personalize:ListFilters"
          , "personalize:ListBatchInferenceJobs"
          , "personalize:ListSolutionVersions"
          , "personalize:ListDataDeletionJobs"
          , "sagemaker:ListMlflowTrackingServers"
          , "sagemaker:ListSpaces"
          , "sagemaker:ListProjects"
          , "sagemaker:ListModelPackages"
          , "sagemaker:ListModelPackageGroups"
          , "sagemaker:ListDomains"
          , "sagemaker:ListUserProfiles"
          , "sagemaker:ListWorkteams"
          , "sagemaker:ListHumanTaskUis"
          , "sagemaker:ListFlowDefinitions"
          , "sagemaker:ListExperiments"
          , "sagemaker:ListTrials"
          , "sagemaker:ListImages"
          , "sagemaker:ListMonitoringSchedules"
          , "mediaconvert:ListQueues"
          , "mediaconvert:ListPresets"
          , "mediaconvert:ListJobTemplates"
          , "ivs:ListChannels"
          , "ivs:ListRecordingConfigurations"
          , "ivs:ListStorageConfigurations"
          , "ivs:ListEncoderConfigurations"
          , "ivs:ListIngestConfigurations"
          , "ivs:ListStreamKeys"
          , "ivs:ListPlaybackKeyPairs"
          , "ivs:ListPlaybackRestrictionPolicies"
          , "ivs:ListAdConfigurations"
          , "ivs:ListStages"
          , "ivs:ListPublicKeys"
          , "ivs:ListCompositions"
          , "ivs:ListParticipants"
          , "cleanrooms:ListCollaborations"
          , "cleanrooms:ListMemberships"
          , "cleanrooms-ml:ListTrainedModels"
          , "cleanrooms-ml:ListTrainedModelVersions"
          , "cleanrooms-ml:GetTrainedModel"
          , "cleanrooms-ml:ListTrainedModelInferenceJobs"
          , "cleanrooms-ml:ListMLInputChannels"
          , "cleanrooms-ml:ListConfiguredModelAlgorithmAssociations"
          , "cleanrooms-ml:ListAudienceModels"
          , "cleanrooms-ml:ListAudienceGenerationJobs"
          , "cleanrooms-ml:ListAudienceExportJobs"
          , "cleanrooms:ListConfiguredTables"
          , "cleanrooms:ListAnalysisTemplates"
          , "cleanrooms:ListConfiguredTableAssociations"
          , "cleanrooms:ListIdNamespaceAssociations"
          , "cleanrooms:ListIdMappingTables"
          , "cleanrooms:ListConfiguredAudienceModelAssociations"
          , "cleanrooms:ListCollaborationPrivacyBudgetTemplates"
          , "verifiedpermissions:ListPolicyStores"
          , "verifiedpermissions:ListPolicyTemplates"
          , "transfer:ListUsers"
          , "transfer:DescribeUser"
          , "backup:ListRecoveryPointsByBackupVault"
          , "backup:ListBackupPlanVersions"
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
