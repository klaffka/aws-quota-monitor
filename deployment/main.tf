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
          "ec2:DescribeHosts",
          "ec2:DescribeTransitGateways",
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
          , "autoscaling:DescribeLaunchConfigurations"
          , "apigateway:GET"
          , "apigateway:ListPortals"
          , "apigateway:ListPortalProducts"
          , "apigateway:ListProductPages"
          , "apigateway:ListProductRestEndpointPages"
          , "apigateway:GetPortal"
          , "ecs:ListClusters"
          , "ecs:ListServices"
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
          , "securityhub:GetMembers"
          , "securityhub:GetInvitationsCount"
          , "transfer:ListWebApps"
          , "transfer:ListProfiles"
          , "transfer:ListWorkflows"
          , "transfer:ListAgreements"
          , "transfer:ListServers"
          , "transfer:ListCertificates"
          , "transfer:ListConnectors"
          , "macie2:ListCustomDataIdentifiers"
          , "macie2:ListFindingsFilters"
          , "macie2:ListMembers"
          , "macie2:GetInvitationsCount"
          , "inspector2:ListFilters"
          , "elasticfilesystem:DescribeFileSystems"
          , "elasticfilesystem:DescribeAccessPoints"
          , "elasticfilesystem:DescribeMountTargets"
          , "elasticfilesystem:DescribeMountTargetSecurityGroups"
          , "fsx:DescribeFileSystems"
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
          , "medialive:ListChannels"
          , "medialive:ListClusters"
          , "medialive:ListCloudWatchAlarmTemplates"
          , "medialive:ListEventBridgeRuleTemplates"
          , "groundstation:ListDataflowEndpointGroups"
          , "groundstation:GetDataflowEndpointGroup"
          , "mediapackage:ListOriginEndpoints"
          , "mediapackage:ListChannels"
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
          , "cloudhsmv2:DescribeClusters"
          , "kafka:ListConfigurations"
          , "kafka:ListConfigurationRevisions"
          , "kafka:ListReplicators"
          , "kinesisanalytics:ListApplications"
          , "kafka:ListClustersV2"
          , "license-manager:ListLicenseConfigurations"
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
          , "internetmonitor:ListMonitoredResources"
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
          , "socialmessaging:ListLinkedWhatsAppBusinessAccounts"
          , "ssm-quicksetup:ListConfigurationManagers"
          , "ssm-sap:ListApplications"
          , "sso-admin:ListInstances"
          , "sso-admin:ListPermissionSets"
          , "identitystore:ListUsers"
          , "identitystore:ListGroups"
          , "servicecatalog-appregistry:ListApplications"
          , "supplychain:ListInstances"
          , "timestream-influxdb:ListDbInstances"
          , "workspaces:DescribeIpGroups"
          , "workspaces:DescribeWorkspaceDirectories"
          , "workspaces:DescribeConnectionAliases"
          , "s3:ListAllMyBuckets"
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
          , "dataexchange:ListDataSets"
          , "dataexchange:ListEventActions"
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
          , "wisdom:ListContents"
          , "voice-id:ListWatchlists"
          , "voice-id:ListSpeakers"
          , "voice-id:ListFraudsterRegistrationJobs"
          , "voice-id:ListSpeakerEnrollmentJobs"
          , "ssm:DescribeMaintenanceWindowTasks"
          , "ssm:DescribeMaintenanceWindowTargets"
          , "swf:ListWorkflowTypes"
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
          , "waf-regional:ListWebACLs"
          , "waf-regional:GetWebACL"
          , "waf-regional:ListRegexPatternSets"
          , "waf-regional:GetRegexPatternSet"
          , "servicediscovery:ListInstances"
          , "amp:ListWorkspaces"
          , "voice-id:ListDomains"
          , "opensearchserverless:ListSecurityConfigs"
          , "opensearchserverless:ListSecurityPolicies"
          , "opensearchserverless:ListAccessPolicies"
          , "opensearchserverless:GetSecurityConfig"
          , "opensearchserverless:GetSecurityPolicy"
          , "opensearchserverless:GetAccessPolicy"
          , "opensearchserverless:ListLifecyclePolicies"
          , "opensearchserverless:BatchGetLifecyclePolicy"
          , "opensearchserverless:ListCollectionGroups"
          , "opensearchserverless:GetAccountSettings"
          , "outposts:ListSites"
          , "outposts:ListOutposts"
          , "vpc-lattice:ListServiceNetworks"
          , "vpc-lattice:ListServices"
          , "vpc-lattice:ListTargetGroups"
          , "workspaces-thin-client:ListEnvironments"
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
          , "dataexchange:ListDataSets"
          , "rbin:ListRules"
          , "rbin:GetRule"
          , "ssm-contacts:ListContacts"
          , "ssm-contacts:ListRotations"
          , "wellarchitected:ListReviewTemplates"
          , "wellarchitected:ListLenses"
          , "wellarchitected:ListWorkloads"
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
          , "connect:ListWorkspaces"
          , "connect:ListNotifications"
          , "connect:SearchEmailAddresses"
          , "connect:ListPredefinedAttributes"
          , "connect:ListHoursOfOperationOverrides"
          , "connect:ListUserProficiencies"
          , "connect:ListRoutingProfileQueues"
          , "connect:ListRoutingProfileManualAssignmentQueues"
          , "connect:ListDataTableAttributes"
          , "pinpoint:ListTemplates"
          , "pinpoint:ListTemplateVersions"
          , "auditmanager:ListAssessmentFrameworks"
          , "auditmanager:ListControls"
          , "auditmanager:ListAssessments"
          , "auditmanager:GetAssessment"
          , "auditmanager:GetAssessmentFramework"
          , "resiliencehub:ListApps"
          , "resiliencehub:ListResiliencyPolicies"
          , "storagegateway:ListGateways"
          , "storagegateway:ListVolumes"
          , "storagegateway:ListFileShares"
          , "omics:ListWorkflows"
          , "omics:ListSequenceStores"
          , "omics:ListVariantStores"
          , "omics:ListAnnotationStores"
          , "iotfleetwise:ListVehicles"
          , "iotfleetwise:ListFleets"
          , "iotfleetwise:ListVehiclesInFleet"
          , "iotfleetwise:ListCampaigns"
          , "iotfleetwise:ListSignalCatalogs"
          , "iotfleetwise:ListModelManifests"
          , "iotfleetwise:ListDecoderManifests"
          , "iotfleetwise:ListStateTemplates"
          , "forecast:ListPredictors"
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
          , "mobiletargeting:GetJourneys"
          , "deadline:ListFarms"
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
          , "scheduler:ListSchedules"
          , "scheduler:ListScheduleGroups"
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
          , "appconfig:ListApplications"
          , "appconfig:ListEnvironments"
          , "appconfig:ListConfigurationProfiles"
          , "appconfig:ListDeploymentStrategies"
          , "servicecatalog:ListPortfolios"
          , "servicecatalog:SearchProductsAsAdmin"
          , "wafv2:ListWebACLs"
          , "wafv2:ListIPSets"
          , "wafv2:ListRegexPatternSets"
          , "wafv2:ListRuleGroups"
          , "acm:ListCertificates"
          , "cognito-idp:ListUserPools"
          , "cognito-idp:DescribeUserPool"
          , "backup:ListBackupVaults"
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
          , "codepipeline:ListPipelines"
          , "codeartifact:ListDomains"
          , "codeartifact:ListRepositories"
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
          , "docdb:DescribeDBClusters"
          , "docdb:DescribeDBInstances"
          , "docdb:DescribeDBSubnetGroups"
          , "neptune:DescribeDBClusters"
          , "neptune:DescribeDBInstances"
          , "neptune:DescribeDBSubnetGroups"
          , "neptune:DescribeDBClusterSnapshots"
          , "neptune:DescribeDBClusterEndpoints"
          , "neptune:DescribeDBParameterGroups"
          , "neptune:DescribeDBClusterParameterGroups"
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
          , "sagemaker:DescribeEndpointConfig"
          , "sagemaker:DescribeEndpoint"
          , "bedrock:ListKnowledgeBases"
          , "bedrock:ListAgents"
          , "bedrock:ListFlows"
          , "bedrock:ListPrompts"
          , "bedrock:ListDataSources"
          , "bedrock:ListAgentAliases"
          , "bedrock:ListAgentActionGroups"
          , "bedrock:ListAgentKnowledgeBases"
          , "bedrock:ListFlowAliases"
          , "bedrock:ListFlowVersions"
          , "bedrock:ListBlueprints"
          , "bedrock:GetBlueprint"
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
          , "bedrock:ListAutomatedReasoningPolicies"
          , "bedrock:ExportAutomatedReasoningPolicyVersion"
          , "bedrock:ListAutomatedReasoningPolicyTestCases"
          , "bedrock:ListEvaluationJobs"
          , "bedrock:GetEvaluationJob"
          , "bedrock:ListModelImportJobs"
          , "rekognition:DescribeProjects"
          , "rekognition:DescribeProjectVersions"
          , "comprehend:ListEndpoints"
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
          , "iot:ListProvisioningTemplates"
          , "iot:ListProvisioningTemplateVersions"
          , "iot:ListPolicies"
          , "iot:ListPolicyVersions"
          , "iot:ListRoleAliases"
          , "iot:ListAuthorizers"
          , "iot:ListTopicRules"
          , "gamelift:ListFleets"
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
          , "bedrock-agentcore:ListWorkloadIdentities"
          , "appsync:ListGraphqlApis"
          , "config:DescribeConfigRules"
          , "dms:DescribeEndpoints"
          , "dms:DescribeReplicationInstances"
          , "dms:DescribeReplicationTasks"
          , "dms:DescribeCertificates"
          , "dms:DescribeReplicationSubnetGroups"
          , "dms:DescribeMigrationProjects"
          , "dms:DescribeDataProviders"
          , "dms:DescribeDataMigrations"
          , "dms:DescribeInstanceProfiles"
          , "mgn:DescribeApplications"
          , "groundstation:ListConfigs"
          , "groundstation:ListMissionProfiles"
          , "iotsitewise:ListAssetModels"
          , "iotsitewise:ListPortals"
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
          , "robomaker:ListSimulationApplications"
          , "robomaker:ListRobotApplications"
          , "workspaces:DescribeWorkspaceImages"
          , "workspaces:DescribeWorkspaceBundles"
          , "workspaces:DescribeWorkspaces"
          , "workspaces:DescribeWorkspaceDirectories"
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
          , "entityresolution:ListIdMappingWorkflows"
          , "entityresolution:ListIdNamespaces"
          , "entityresolution:ListSchemaMappings"
          , "datazone:ListDomains"
          , "datazone:ListAssets"
          , "datazone:ListGlossaries"
          , "datazone:ListAssetTypes"
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
          , "amplify:ListDomainAssociations"
          , "amplify:ListBranches"
          , "amplify:ListWebhooks"
          , "connectcases:ListDomains"
          , "connectcases:ListTemplates"
          , "connectcases:ListCaseRules"
          , "connectcases:ListFields"
          , "connectcases:ListFieldOptions"
          , "connectcases:ListLayouts"
          , "connectcases:GetLayout"
          , "connectcases:SearchAllRelatedItems"
          , "connectcases:BatchGetCaseRule"
          , "connectcases:GetTemplate"
          , "airflow:ListEnvironments"
          , "amplifyuibuilder:ListThemes"
          , "amplifyuibuilder:ListViews"
          , "amplifyuibuilder:ListComponents"
          , "amplifyuibuilder:ListForms"
          , "evs:ListEnvironments"
          , "evs:ListEnvironmentHosts"
          , "servicecatalog:ListServiceActions"
          , "lightsail:GetInstances"
          , "lightsail:GetRelationalDatabases"
          , "lightsail:GetContainerServices"
          , "mediastore:ListContainers"
          , "mediatailor:ListSourceLocations"
          , "mediatailor:ListChannels"
          , "kinesisvideo:ListStreams"
          , "kinesisvideo:ListSignalingChannels"
          , "codedeploy:ListApplications"
          , "codedeploy:ListDeploymentGroups"
          , "cassandra:ListTables"
          , "cassandra:ListKeyspaces"
          , "qldb:ListLedgers"
          , "refactor-spaces:ListEnvironments"
          , "refactor-spaces:ListApplications"
          , "refactor-spaces:ListServices"
          , "refactor-spaces:ListRoutes"
          , "cloud9:ListEnvironments"
          , "resource-explorer-2:ListViews"
          , "neptune-graph:ListGraphs"
          , "eks:ListClusters"
          , "eks:ListNodegroups"
          , "redshift:DescribeClusters"
          , "elasticfilesystem:DescribeFileSystems"
          , "mq:ListBrokers"
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
          , "elasticloadbalancing:DescribeLoadBalancers"
          , "elasticloadbalancing:DescribeTargetGroups"
          , "elasticloadbalancing:DescribeListeners"
          , "elasticloadbalancing:DescribeRules"
          , "elasticloadbalancing:DescribeTargetHealth"
          , "elasticloadbalancing:DescribeLoadBalancers"
          , "mq:ListBrokers"
          , "ds:DescribeDirectories"
          , "es:ListDomainNames"
          , "es:ListApplications"
          , "elasticbeanstalk:DescribeApplications"
          , "elasticbeanstalk:DescribeEnvironments"
          , "elasticbeanstalk:DescribeApplicationVersions"
          , "elasticbeanstalk:ListPlatformVersions"
          , "batch:DescribeJobQueues"
          , "batch:DescribeComputeEnvironments"
          , "s3control:ListAccessPoints"
          , "s3control:ListMultiRegionAccessPoints"
          , "codedeploy:ListApplications"
          , "codedeploy:ListDeploymentGroups"
          , "codeguruprofiler:ListProfilingGroups"
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
          , "sagemaker:ListNotebookInstances"
          , "sagemaker:ListPipelines"
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
          , "mediaconvert:ListJobTemplates"
          , "ivs:ListChannels"
          , "ivs:ListRecordingConfigurations"
          , "ivs-realtime:ListStorageConfigurations"
          , "ivs-realtime:ListEncoderConfigurations"
          , "ivs-realtime:ListIngestConfigurations"
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
          , "appmesh:ListMeshes"
          , "transfer:ListUsers"
          , "transfer:DescribeUser"
          , "backup:ListRecoveryPointsByBackupVault"
          , "backup:ListBackupVaults"
          , "backup:ListBackupPlans"
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
