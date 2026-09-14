import json
from pathlib import Path

import pytest

from modules.qmcore.aws import Unsupported
from modules.qmcore.metrics import metric_spec, normalize_usage_metric


FIXTURE = Path(__file__).parent / 'fixtures' / 'usage_metrics.json'


def cases():
    return json.loads(FIXTURE.read_text())


def test_valid_usage_metric_fixtures_normalize_without_aws():
    valid = {case['name']: case['quota'] for case in cases()}
    normalized = normalize_usage_metric(valid['resource_count_maximum'])
    assert normalized['Namespace'] == 'AWS/Usage'
    assert normalized['MetricName'] == 'ResourceCount'
    assert normalized['Dimensions'] == [
        {'Name': 'Class', 'Value': 'Standard/OnDemand'},
        {'Name': 'Service', 'Value': 'EC2'},
    ]
    spec, unit, _ = metric_spec(valid['rate_sum_minute'])
    assert spec['Stat'] == 'Sum'
    assert spec['Period'] == 60
    assert unit == 'Count'


@pytest.mark.parametrize('name', [
    'unresolved_dimension', 'unsupported_unit', 'unsupported_statistic', 'invalid_dimensions',
])
def test_invalid_usage_metric_fixtures_are_unsupported(name):
    quota = next(case['quota'] for case in cases() if case['name'] == name)
    with pytest.raises(Unsupported):
        metric_spec(quota)
