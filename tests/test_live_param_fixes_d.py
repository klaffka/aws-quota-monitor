"""Request parameters rejected by the live APIs, pinned against the models.

botocore validates neither enums nor the Data Automation rule that a list
request takes one filter, so a Stubber alone let both errors through.
"""
import boto3
import botocore.session
import pytest
from botocore.stub import Stubber

from modules.qmchecks import auditmanager, bedrock, bedrock_data_automation as bda
from modules.qmcore.aws import CheckContext

MODELS = botocore.session.get_session()


def context(service):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': 'L-00000000', 'Value': 100}],
                        account='123456789012')


def recorded(service, calls, fn):
    """Run fn against an empty stubbed inventory and return its request parameters."""
    ctx = context(service)
    client = ctx.client(bda.SERVICE if service == 'bedrock' else service)
    seen = []
    client.meta.events.register('before-parameter-build.*.*', lambda params, model, **_: seen.append(
        (model.name, dict(params))))
    with Stubber(client) as stub:
        for method, key in calls:
            stub.add_response(method, {key: []})
        fn(ctx)
    return seen


@pytest.mark.parametrize('fn, operation, member', [
    (auditmanager.custom_frameworks, 'ListAssessmentFrameworks', 'frameworkType'),
    (auditmanager.custom_controls, 'ListControls', 'controlType'),
])
def test_auditmanager_type_filter_is_a_model_enum_value(fn, operation, member):
    method = {'ListAssessmentFrameworks': ('list_assessment_frameworks', 'frameworkMetadataList'),
              'ListControls': ('list_controls', 'controlMetadataList')}[operation]
    (name, params), = recorded('auditmanager', [method], fn)
    enum = MODELS.get_service_model('auditmanager').operation_model(name).input_shape.members[member].enum
    assert params[member] in enum
    assert params[member] == 'Custom'


EXCLUSIVE = {'resourceOwner', 'blueprintStageFilter', 'projectStageFilter', 'blueprintArn',
             'projectFilter', 'blueprintFilter', 'libraryFilter'}


@pytest.mark.parametrize('fn, calls', [
    (bda.blueprint_inventory, [('list_blueprints', 'blueprints')]),
    (lambda ctx: bda.versions(ctx, 'arn:aws:bedrock:eu-central-1:123456789012:blueprint/a'),
     [('list_blueprints', 'blueprints')]),
    (bda.project_blueprint_types, [('list_data_automation_projects', 'projects')]),
    (bedrock.blueprint_count, [('list_blueprints', 'blueprints')]),
])
def test_data_automation_lists_send_one_filter(fn, calls):
    for _name, params in recorded('bedrock', calls, fn):
        assert len(EXCLUSIVE & set(params)) == 1, params


def test_account_inventories_keep_both_stages():
    # The stage filter is the one filter kept: LIVE alone would miss drafts.
    for fn, calls in [(bda.blueprint_inventory, [('list_blueprints', 'blueprints')]),
                      (bda.project_blueprint_types, [('list_data_automation_projects', 'projects')])]:
        (_name, params), = recorded('bedrock', calls, fn)
        assert 'ALL' in params.values()
