import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import resiliencehub
from modules.qmcore.aws import CheckContext, NoData

SERVICE = 'arn:aws:resiliencehub:eu-central-1:123456789012:service/one'
OTHER = 'arn:aws:resiliencehub:eu-central-1:123456789012:service/two'
SYSTEM = 'arn:aws:resiliencehub:eu-central-1:123456789012:system/one'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'resiliencehub', 'QuotaCode': code,
                          'Value': 50}], account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in resiliencehub.CHECKS if candidate == code)


def service(arn, systems=(), regions=('eu-central-1',)):
    return {'serviceArn': arn, 'name': arn.rsplit('/', 1)[1],
            'associatedSystems': [{'systemArn': system} for system in systems],
            'regions': list(regions)}


def test_the_service_summary_answers_the_system_and_region_limits():
    ctx = context('L-358A975C')
    with Stubber(ctx.client('resiliencehubv2')) as stub:
        stub.add_response('list_services', {'serviceSummaries': [
            service(SERVICE, systems=[SYSTEM, SYSTEM + '-2'], regions=['eu-central-1']),
            service(OTHER, systems=[SYSTEM], regions=['eu-west-1', 'us-east-1'])]}, {})
        systems = check('L-358A975C')(ctx)
        assert (systems['usage'], systems['resource_id']) == (2, SERVICE)
        regions = check('L-3C215170')(ctx)
        assert (regions['usage'], regions['resource_id']) == (2, OTHER)
        assert check('L-FC254984')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_only_unfinished_assessments_count_per_service():
    ctx = context('L-FCCEDB4B')
    with Stubber(ctx.client('resiliencehubv2')) as stub:
        stub.add_response('list_services',
                          {'serviceSummaries': [service(SERVICE)]}, {})
        stub.add_response('list_failure_mode_assessments', {'assessmentSummaries': [
            {'assessmentId': '11111111-1111-1111-1111-111111111111', 'serviceArn': SERVICE,
             'assessmentStatus': 'IN_PROGRESS'},
            {'assessmentId': '22222222-2222-2222-2222-222222222222', 'serviceArn': SERVICE,
             'assessmentStatus': 'SUCCESS'}]}, {'serviceArn': SERVICE})
        result = check('L-FCCEDB4B')(ctx)
        assert (result['usage'], result['resource_id']) == (1, SERVICE)
        stub.assert_no_pending_responses()


def test_an_unknown_assessment_status_raises_nodata():
    ctx = context('L-FCCEDB4B')
    with Stubber(ctx.client('resiliencehubv2')) as stub:
        stub.add_response('list_services',
                          {'serviceSummaries': [service(SERVICE)]}, {})
        stub.add_response('list_failure_mode_assessments', {'assessmentSummaries': [
            {'assessmentId': '11111111-1111-1111-1111-111111111111', 'serviceArn': SERVICE,
             'assessmentStatus': 'PAUSED'}]}, {'serviceArn': SERVICE})
        with pytest.raises(NoData, match='unknown status'):
            check('L-FCCEDB4B')(ctx)


def test_journeys_are_counted_from_the_system_summary():
    ctx = context('L-EB92175D')
    with Stubber(ctx.client('resiliencehubv2')) as stub:
        stub.add_response('list_systems', {'systemSummaries': [
            {'systemId': 'one', 'systemArn': SYSTEM, 'name': 'one',
             'userJourneysCount': 3},
            {'systemId': 'two', 'systemArn': SYSTEM + '-2', 'name': 'two',
             'userJourneysCount': 1}]}, {})
        result = check('L-EB92175D')(ctx)
        assert (result['usage'], result['resource_id']) == (3, SYSTEM)
        stub.assert_no_pending_responses()


def test_services_are_counted_for_each_user_journey():
    ctx = context('L-ED7E6FFD')
    with Stubber(ctx.client('resiliencehubv2')) as stub:
        stub.add_response('list_systems', {'systemSummaries': [
            {'systemId': 'one', 'systemArn': SYSTEM, 'name': 'one'}]}, {})
        stub.add_response('list_user_journeys', {'userJourneySummaries': [
            {'userJourneyId': 'uj-1', 'name': 'checkout'}]}, {'systemArn': SYSTEM})
        stub.add_response('list_services', {'serviceSummaries': [
            service(SERVICE), service(OTHER)]},
            {'systemArn': SYSTEM, 'userJourneyId': 'uj-1'})
        result = check('L-ED7E6FFD')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'uj-1')
        stub.assert_no_pending_responses()


def test_input_source_tags_are_reported_per_source():
    ctx = context('L-04E7C378')
    with Stubber(ctx.client('resiliencehubv2')) as stub:
        stub.add_response('list_services',
                          {'serviceSummaries': [service(SERVICE)]}, {})
        stub.add_response('list_input_sources', {'inputSourceSummaries': [
            {'inputSourceId': 'is-1', 'type': 'CFN_STACK',
             'resourceTags': [{'key': 'a', 'values': ['1']}, {'key': 'b', 'values': ['2']}]},
            {'inputSourceId': 'is-2', 'type': 'CFN_STACK'}]}, {'serviceArn': SERVICE})
        result = check('L-04E7C378')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'is-1')
        stub.assert_no_pending_responses()
