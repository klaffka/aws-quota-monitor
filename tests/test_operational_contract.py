"""Keep safety-critical deployment and operations assumptions reviewable."""
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_event_targets_use_published_aliases_and_keep_failed_events():
    hcl = (ROOT / 'deployment/main.tf').read_text()
    assert 'arn       = aws_lambda_alias.live["collector"].arn' in hcl
    assert 'arn       = aws_lambda_alias.live["reporting"].arn' in hcl
    assert hcl.count('arn = aws_sqs_queue.failed_events.arn') == 2
    assert '"time":<scheduled_time>' in hcl


def test_run_history_protection_is_enabled_and_pitr_is_opt_in():
    variables = (ROOT / 'deployment/variables.tf').read_text()
    table = (ROOT / 'deployment/main.tf').read_text()
    assert 'default     = true' in variables[variables.index('variable "enable_data_deletion_protection"'):]
    assert 'default     = false' in variables[variables.index('variable "enable_dynamodb_pitr"'):]
    assert 'deletion_protection_enabled = var.enable_data_deletion_protection' in table
    assert 'enabled = var.enable_dynamodb_pitr' in table


def test_reporter_role_cannot_enumerate_aws_resources_or_publish_alerts():
    operations = (ROOT / 'deployment/operations.tf').read_text()
    reporting = operations.split('resource "aws_iam_role_policy" "reporting"', 1)[1].split('\n}', 1)[0]
    for forbidden in ('List*', 'Describe*', 'Get*', 'sns:Publish', 'ec2:', 's3:'):
        assert forbidden not in reporting
    assert 'servicequotas:ListServices' in reporting
    assert 'cloudwatch:GetMetricData' in reporting
    assert 'dynamodb:Scan' in reporting


def test_security_scanner_digest_and_exception_are_narrow_and_expiring():
    workflow = (ROOT / '.github/workflows/ci.yml').read_text()
    scanner = (ROOT / 'scripts/security_scan.sh').read_text()
    exception = yaml_load(ROOT / '.trivyignore.yaml')
    assert 'bash scripts/security_scan.sh' in workflow
    assert '@sha256:' in scanner
    misconfigs = exception['misconfigurations']
    assert {item['id'] for item in misconfigs} == {'AVD-AWS-0132', 'AVD-AWS-0095'}
    for item in misconfigs:
        assert item['paths'] == ['deployment/main.tf']
        expiry = item['expired_at']
        expiry = datetime.fromisoformat(expiry).date() if isinstance(expiry, str) else expiry
        expiry = expiry.date() if isinstance(expiry, datetime) else expiry
        assert item['statement'] and expiry > date.today()
    assert exception['secrets'] == [] and exception['vulnerabilities'] == []


def yaml_load(path):
    import yaml
    return yaml.safe_load(path.read_text())


def test_live_validation_is_opt_in_and_documents_its_side_effects():
    script = (ROOT / 'scripts/live_acceptance.py').read_text()
    operations = (ROOT / 'docs/operations.md').read_text()
    assert "parser.add_argument('--execute', action='store_true'" in script
    assert "if not args.execute:" in script
    assert 'incurs the usual collector API costs' in operations
    assert 'restore-drill-' in (ROOT / 'scripts/restore_drill.sh').read_text()
