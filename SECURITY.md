# Security policy

Security fixes target the current stable release and main. Upgrade to the current
release before reporting a fixed vulnerability. Report sensitive issues through
the repository's private vulnerability reporting feature if enabled; otherwise
contact the repository owner privately. Do not publish credentials or account
exports in an issue. Rotate an exposed credential before investigating its use.

CI scans source for secrets, Python dependency advisories, and Terraform
misconfigurations. HIGH/CRITICAL findings block releases. The scanner is pinned
to a reviewed image digest; advisory databases remain current. The source scan
does not audit Git history or AWS runtime configuration. Keep GitHub's secret
scanning/push protection enabled where available; account settings are separate
from this repository's CI.

Exceptions live in `.trivyignore.yaml` and require a specific finding ID, the
narrowest applicable paths, a written justification and an expiration; the
repository owner reviews each one before it expires.
Do not suppress a whole scanner or use `continue-on-error`. An expired exception
must be re-evaluated. New scanner releases and dependency updates go through CI.

The current S3 exception accepts AWS's default SSE-S3 encryption at rest for
low-sensitivity report CSVs. The SNS exception leaves the alert topic
unencrypted at rest, because CloudWatch alarms cannot publish to a topic
encrypted with the AWS-managed SNS key, and avoids adding a customer-managed
key and its ongoing cost; notification bodies contain quota names, resource identifiers,
and percentages only. Both exceptions expire and must be re-reviewed.

Collector inventory permissions necessarily include account-wide list operations.
Reporting has its own role and cannot enumerate application resources or publish
quota alerts. Both roles write only monitor-owned operational data. Failure
queues contain events/error records: restrict human read/replay permissions.
