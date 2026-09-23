# Deploying AWS Quota Monitor

Deployment is a manual, reviewed Terraform apply from `main`. Neither CI nor the
release workflow touches AWS. This runbook is what the 2026-09-23 redeploy and
its validation runs actually needed.

## Before planning

- Set `aws_account_id` in `deployment/terraform.tfvars`. With it, the provider
  refuses credentials for any other account instead of planning a bucket
  replacement.
- Estimate what the change costs per month. `GetMetricData` has no free tier:
  every run requests each compatible usage metric (about 2,500 in eu-central-1,
  $0.01 per 1,000), so the schedule decides most of the bill. At `rate(1 day)`
  the collector costs roughly $1 a month; at `rate(10 minutes)` it was about
  $110. DynamoDB on-demand writes (one per measurement, about 5,000 a run) come
  second. Lambda, alarms, the heartbeat metric and logs stay in the free tier.

## Plan

```bash
bash deployment/build_layer.sh
.venv/bin/python scripts/verify_package.py
terraform -chdir=deployment plan -input=false -out=deploy.tfplan
terraform -chdir=deployment show -json deploy.tfplan \
  | jq -r '.resource_changes[] | select(.change.actions != ["no-op"] and .change.actions != ["read"])
           | "\(.change.actions | join("+"))\t\(.address)"'
```

Read every `delete` before applying:

- `aws_lambda_layer_version` replaces itself on each dependency change;
  `skip_destroy` keeps the old version in AWS as a rollback target.
- The report bucket, the DynamoDB table and the SNS topic must never appear.
- Setting a log group's `retention_in_days` for the first time deletes every
  older log event in it.

`tests/test_iam_action_prefixes.py` asserts that all inline policies on the
role stay under AWS's 10,240-character limit. `terraform validate` does not
check that, and an apply over it fails with `LimitExceeded`.

## Apply

```bash
terraform -chdir=deployment apply deploy.tfplan
terraform -chdir=deployment plan -input=false   # expect "No changes"
```

A log group that already exists in AWS but not in the state makes the apply
fail with `ResourceAlreadyExistsException`; import it first, for example
`terraform -chdir=deployment import 'aws_cloudwatch_log_group.lambda["collector"]' /aws/lambda/qm-quota-collector`.

## Validate

Invoke the collector synchronously. An asynchronous invocation is retried
twice on failure, which triples the metric cost of a failing run.

```bash
aws lambda invoke --function-name qm-quota-collector \
  --invocation-type RequestResponse --cli-read-timeout 960 \
  --cli-binary-format raw-in-base64-out --payload '{"source":"manual-validation"}' out.json
```

Then read the run record, which lists every check error:

```bash
aws dynamodb query --table-name qm-quotalog \
  --key-condition-expression 'PK = :p' \
  --expression-attribute-values '{":p":{"S":"RUN#<account>#<region>"}}' \
  --no-scan-index-forward --limit 1
```

A run with any error sends no heartbeat. To tell a missing IAM grant from a
service the account has not set up, repeat the failing call with administrator
credentials: the same answer means no grant will help, and the check should
report `NO_DATA` or `UNSUPPORTED` (`NOT_SET_UP` in `src/modules/qmcore/aws.py`).
Confirm a new grant with `aws iam simulate-custom-policy` before applying it.

The `REPORT` line in the collector's log group gives duration and peak memory;
a full run took about 180 s and 593 MB of its 1,024 MB on 2026-09-23.

`qm-collector-no-success` evaluates hourly periods about 30 minutes after each
hour closes, so it returns to `OK` up to 90 minutes after a successful run.
