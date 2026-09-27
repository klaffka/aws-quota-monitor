# Operations and recovery

The monitor writes quota history every day. A scheduled run is keyed by its
EventBridge timestamp. The DynamoDB execution lease prevents overlap: a
delivery that arrives while another invocation holds the lease, or after the run
completed, returns without collecting. Failed executions can retry the same
24-hour metric window and overwrite the same quota observation key.

Only a run whose quota catalog is missing or incomplete, or whose measurements
could not be stored, fails and is retried. Errors from individual checks do not:
retrying repeats every `GetMetricData` query, and a check that failed once
usually fails again. Such a run stores its measurements, records the errors in
its `RUN#` item with `qualityStatus` `ERROR`, completes, and sends no heartbeat,
so `qm-collector-no-success` reports it after 25 hours. `collectedAt` on inventory checks
continues to show when AWS was actually queried. Replays older than 26 hours do
not send quota notifications or the current-run heartbeat; events older than 14
days are rejected. Inspect the `RUN#` record and CloudWatch log before replaying.

## Failed events

EventBridge target delivery failures and Lambda handler failures (the retryable
failures above) both go to the
encrypted `qm-failed-events` SQS queue. EventBridge keeps retrying target
delivery for up to one day; Lambda retries handler failures twice, with an event
age limit of six hours. The queue retains messages for 14 days and its alarm
notifies the existing SNS topic when a message arrives.

Inspect a message before redriving it. A collector event can be replayed through
the `live` alias with its original `source` and `time`; the execution lease makes
duplicate scheduled messages safe. Replay a reporting event with its original
month. Do not replay poison events without first fixing the recorded error.
Restrict SQS read/delete access because failed invocation records include input
events and error details. Purge or delete only after each message is resolved.

## Rollback

Functions publish immutable versions and the EventBridge rules invoke the `live`
aliases. Check available versions and their code/layer configuration:

```bash
aws lambda list-versions-by-function --function-name qm-quota-collector \
  --query 'Versions[?Version!=`$LATEST`].[Version,LastModified,CodeSize,Layers[*].Arn]'
aws lambda list-versions-by-function --function-name qm-reporting \
  --query 'Versions[?Version!=`$LATEST`].[Version,LastModified,CodeSize,Layers[*].Arn]'
```

Plan a rollback to the last known-good published pair, review the Terraform plan,
and apply it:

```bash
terraform -chdir=deployment plan -input=false \
  -var='lambda_version_overrides={collector="<VERSION>",reporting="<VERSION>"}' \
  -out=rollback.tfplan
terraform -chdir=deployment show rollback.tfplan
terraform -chdir=deployment apply rollback.tfplan
```

The aliases move atomically per function. Roll back both when their code/layer
contracts changed together. To return to the newest published code, remove the
override from `terraform.tfvars` and plan again. Old Lambda versions and layer
versions are retained so a previous deployment stays available.

## History protection and restore drill

Deletion protection is enabled by default. Point-in-time recovery is configurable
because AWS charges for it and it is not needed by every deployment:

```hcl
enable_data_deletion_protection = true
enable_dynamodb_pitr             = true
```

Deletion protection must be explicitly set to `false` in a reviewed Terraform
plan before intentionally destroying the production history table. PITR protects
against accidental writes/deletes and restores into a **new** table;
it does not overwrite the production table. After enabling it, run a drill with a
recent point inside the recovery window:

```bash
bash scripts/restore_drill.sh --source qm-quotalog \
  --target qm-restore-drill-20260926 --region eu-central-1 \
  --restore-time 2026-09-25T00:00:00Z
bash scripts/restore_drill.sh --source qm-quotalog \
  --target qm-restore-drill-20260926 --region eu-central-1 \
  --restore-time 2026-09-25T00:00:00Z --execute
```

The first command validates the exact target and time without writing. The second
creates a separate table and waits for it to become available. Verify representative
`QUOTA#`, `RUN#`, `COVERAGE#`, `ALERT#`, and `CATALOG#` records before declaring the
drill successful. Keep the restored table until reviewed, then delete only the exact
drill table after its retention/cost impact is understood. Do not point production
functions at the restored table as part of the drill.

## Live acceptance

Unit tests use stubs and cannot verify deployed IAM grants or live API behavior. The
optional acceptance script invokes the collector synchronously through `live`, checks
the caller account, requires a complete run record and positive measurement count,
and disables alerts and the current-run heartbeat for that validation run. It writes
quota/run records and incurs the usual collector API costs:

```bash
.venv/bin/python scripts/live_acceptance.py --expected-account 123456789012 \
  --region eu-central-1 --execute
```

For a meaningful populated-account acceptance, add `--require-service SERVICE` for
each service with known live resources; the script requires a positive valid custom
inventory measurement for each requested service. This does not prove every quota
check in that service is populated. Save the printed run ID and inspect its `RUN#`
record, errors, duration, API calls, and per-module check timings. Run this after
deploying and record the result in the release/change review.

## Runtime and cost review

Each `RUN#` item records elapsed time, per-service API counts/errors/retries and
per-module check duration. Compare several successful runs before changing memory,
parallelism, or service schedules. API service counters include failed attempts;
API duration includes SDK backoff/retry time. The Lambda REPORT line remains the
source for billed duration and peak memory. Avoid adding per-service CloudWatch
metrics: `GetMetricData` and the existing daily schedule already dominate the
known recurring monitor cost.
