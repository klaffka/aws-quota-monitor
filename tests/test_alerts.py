from datetime import datetime, timedelta, UTC
from unittest.mock import Mock
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import pytest
from modules.qmalerting.alerting import QuotaAlert, AlertBusy
from modules.qmcore.model import measurement

NOW = datetime(2026, 3, 1, tzinfo=UTC)


def entry(usage=90, seconds=0, **kwargs):
    return measurement('123456789012', 'eu-central-1', 'ec2', 'q', 'quota', 100, usage,
                       now=NOW+timedelta(seconds=seconds), **kwargs)


def setup(aws_db):
    session, db = aws_db
    clock = Mock(return_value=int(NOW.timestamp()))
    alert = QuotaAlert(session, sns_topic_arn='arn:aws:sns:eu-central-1:123456789012:test', db=db, clock=clock)
    alert.sns_client = Mock()
    return alert, clock


def test_breach_reminder_recovery_and_stale_observations(aws_db):
    alert, clock = setup(aws_db)
    assert alert.check_and_alert(entry())
    assert not alert.check_and_alert(entry(seconds=600))
    clock.return_value += 86399
    assert not alert.check_and_alert(entry(seconds=86399))
    clock.return_value += 1
    assert alert.check_and_alert(entry(seconds=86400))
    assert not alert.check_and_alert(entry(10, seconds=86401, status='NO_DATA'))
    assert alert.check_and_alert(entry(10, seconds=86402))
    assert not alert.check_and_alert(entry(10, seconds=86403))
    assert not alert.check_and_alert(entry(90, seconds=1))
    assert alert.sns_client.publish.call_count == 3


def test_send_failure_does_not_commit_transition(aws_db):
    alert, _ = setup(aws_db)
    alert.sns_client.publish.side_effect = RuntimeError('SNS unavailable')
    with pytest.raises(RuntimeError, match='SNS unavailable'):
        alert.check_and_alert(entry())
    alert.sns_client.publish.side_effect = None
    assert alert.check_and_alert(entry())
    alert.sns_client.publish.side_effect = RuntimeError('SNS unavailable')
    with pytest.raises(RuntimeError):
        alert.check_and_alert(entry(10, 600))
    alert.sns_client.publish.side_effect = None
    assert alert.check_and_alert(entry(10, 600))


def test_concurrent_invocations_send_once(aws_db):
    alert, _ = setup(aws_db)
    entered, release = Event(), Event()
    def publish(**kwargs):
        entered.set()
        assert release.wait(5)
        return {'MessageId': 'sent'}
    alert.sns_client.publish.side_effect = publish
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(alert.check_and_alert, entry())
        assert entered.wait(5)
        try:
            with pytest.raises(AlertBusy):
                alert.check_and_alert(entry())
        finally:
            release.set()
        assert first.result()
    assert not alert.check_and_alert(entry())
    assert alert.sns_client.publish.call_count == 1


def test_old_version_and_invalid_limits_never_alert(aws_db):
    alert, _ = setup(aws_db)
    legacy = entry()
    legacy['calculationVersion'] = 1
    assert not alert.check_and_alert(legacy)
    invalid = entry()
    invalid['limitValue'] = 0
    assert not alert.check_and_alert(invalid)
    alert.sns_client.publish.assert_not_called()


@pytest.mark.parametrize('threshold', [0, -1, 101, 'nan', True])
def test_threshold_validation(aws_db, threshold):
    with pytest.raises(ValueError):
        QuotaAlert(aws_db[0], threshold_pct=threshold, db=aws_db[1])
