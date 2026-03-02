# AWS Quota Monitor

AWS Service Quotas monitoring with:
- scheduled quota collection (Quota Collector),
- storage in DynamoDB,
- SNS alerting on threshold breaches,
- monthly CSV reporting to S3.

## Architecture

The solution deploys two Lambda functions:
- `qm-quota-collector`: collects quota and usage data and stores it in DynamoDB.
- `qm-reporting`: generates a CSV quota report and uploads it to S3.

Infrastructure and scheduling are managed with Terraform (`deployment/`).

## Relevant Project Structure

```text
.
├── src/
│   ├── functions/
│   │   ├── quota-collector/main.py
│   │   └── reporting/main.py
│   └── modules/
│       ├── qmalerting/alerting.py
│       ├── qmchecks/ec2/ec2.py
│       ├── qmchecks/general/utilization_report.py
│       └── qmdb/db.py
├── deployment/
│   ├── main.tf
│   ├── data.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── version.tf
│   └── terraform.tfvars.example
├── tests/
│   ├── test_quota_collector.py
│   └── test_reporting.py
└── requirements.txt
```

## Prerequisites

- AWS account with IAM permissions for:
  - Lambda, IAM, EventBridge, DynamoDB, SNS, S3
  - Service Quotas, CloudWatch metrics, EC2 read APIs
- AWS CLI configured (`aws configure` or named profile)
- Terraform >= 1.0
- Python 3.14 recommended locally (Lambda runtime is `python3.14`)

## Usage (Local)

### 1) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Set AWS context

```bash
export AWS_PROFILE=<your-profile>
export AWS_REGION=eu-central-1
```

Optional:
- `QM_AWS_PROFILE`: alternative to `AWS_PROFILE`
- `QM_ALERT_THRESHOLD`: alert threshold in percent (default: `80`)

### 3) Run Quota Collector locally

```bash
python src/functions/quota-collector/main.py
```

### 4) Run Reporting locally

For local reporting, set a target bucket:

```bash
export QM_REPORT_BUCKET=<reports-bucket-name>
export QM_REPORT_DAYS=30
python src/functions/reporting/main.py
```

## Deployment (Terraform)

### 1) Prepare `terraform.tfvars`

In `deployment/`, create `terraform.tfvars` (for example based on `terraform.tfvars.example`):

```hcl
tags = {
  scope = "BA"
  env   = "prod"
}

alert_threshold_pct   = 80
alert_email           = "alerts@example.com"
report_bucket_name    = ""
report_retention_days = 90
report_days_back      = 30
```

Notes:
- `alert_email` is optional. If set, SNS sends a subscription confirmation email.
- `report_bucket_name = ""` auto-generates `qm-reports-<account-id>`.

### 2) Initialize and deploy

```bash
cd deployment
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

### 3) Validate outputs

```bash
terraform output
```

Key outputs:
- `quota_collector_function_name`
- `reporting_function_name`
- `dynamodb_table_name`
- `sns_topic_arn`
- `reports_bucket_name`

## Runtime Behavior

- EventBridge schedules:
  - Collector: every 10 minutes
  - Reporting: monthly on day 1 at 00:00 UTC
- Quota data is stored in DynamoDB table `qm-quotalog`.
- Reports are uploaded as CSV to `s3://<bucket>/reports/`.

## Manual Invocation in AWS

### Collector

```bash
aws lambda invoke \
  --function-name qm-quota-collector \
  --payload '{}' \
  collector-response.json
cat collector-response.json
```

### Reporting

```bash
aws lambda invoke \
  --function-name qm-reporting \
  --payload '{"days_back":30}' \
  reporting-response.json
cat reporting-response.json
```

### View logs

```bash
aws logs tail /aws/lambda/qm-quota-collector --follow
aws logs tail /aws/lambda/qm-reporting --follow
```

## Important Configuration

Lambda environment variables (set by Terraform):
- `QM_QUOTA_TABLE`
- `QM_ALERT_TOPIC_ARN`
- `QM_ALERT_THRESHOLD`
- `QM_REPORT_BUCKET`
- `QM_REPORT_DAYS`

Terraform variables (`deployment/variables.tf`):
- `tags`
- `alert_threshold_pct`
- `alert_email`
- `report_bucket_name`
- `report_retention_days`
- `report_days_back`

## Tests

```bash
pytest -q
```

## Troubleshooting

- No SNS email received:
  - Confirm the subscription via the SNS confirmation email.
- Reporting returns no output:
  - Check `QM_REPORT_BUCKET` and Lambda logs.
- Terraform layer build fails:
  - Verify local Python/pip setup, then run `terraform apply` again.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
