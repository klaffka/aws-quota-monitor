"""Data Automation blueprint and vocabulary configuration quotas."""
import re

from modules.qmcore.aws import NoData, maximum


SERVICE = 'bedrock-data-automation'


def required_id(item, field):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'Data Automation inventory is missing {field}')
    return value


# The list APIs accept one filter per request: resourceOwner, the stage filter
# and blueprintArn are mutually exclusive ("Invalid List filter combination").
# Without resourceOwner only account-owned resources are listed, so the stage
# filter alone yields the complete account inventory across both stages.
def blueprint_inventory(ctx):
    return ctx.call(SERVICE, 'list_blueprints', 'blueprints', blueprintStageFilter='ALL')


def versions(ctx, arn):
    result = set()
    for item in ctx.call(SERVICE, 'list_blueprints', 'blueprints', blueprintArn=arn):
        if item.get('blueprintArn') != arn:
            raise NoData('Blueprint version inventory contains a different parent')
        version = required_id(item, 'blueprintVersion')
        if not re.fullmatch(r'[1-9][0-9]*', version):
            raise NoData('Blueprint version inventory has an unresolved version')
        result.add(version)
    return sorted(result, key=int)


def blueprint_versions(ctx):
    arns = {required_id(item, 'blueprintArn') for item in blueprint_inventory(ctx)}
    return maximum([(arn, len(versions(ctx, arn)), None) for arn in sorted(arns)],
                   'Blueprint', 'bedrock-data-automation:ListBlueprints')


def blueprint_size(ctx):
    stages = {}
    for item in blueprint_inventory(ctx):
        arn = required_id(item, 'blueprintArn')
        stage = item.get('blueprintStage')
        if stage not in {'LIVE', 'DEVELOPMENT'}:
            raise NoData('Blueprint inventory has an unknown stage')
        stages.setdefault(arn, set()).add(stage)
    values = []
    for arn, current_stages in sorted(stages.items()):
        requests = [('blueprintStage', stage) for stage in sorted(current_stages)]
        requests += [('blueprintVersion', version) for version in versions(ctx, arn)]
        for selector, value in requests:
            data = ctx.call(SERVICE, 'get_blueprint', blueprintArn=arn, **{selector: value}).get('blueprint')
            if not isinstance(data, dict) or data.get('blueprintArn') != arn or data.get(selector) != value:
                raise NoData('Blueprint detail does not match its requested identity')
            schema = data.get('schema')
            if not isinstance(schema, str) or not schema:
                raise NoData('Blueprint detail has no schema text')
            # Count the returned JSON text in characters, preserving whitespace
            # and Unicode. Re-serialization would change the measured size.
            values.append((f'{arn}/{selector}/{value}', len(schema), None))
    return maximum(values, 'BlueprintConfiguration', 'bedrock-data-automation:GetBlueprint')


# The project lists its blueprints by ARN alone; only the blueprint detail
# names the modality, and the catalog bounds each modality separately.
MODALITIES = {'AUDIO': 'Audios', 'DOCUMENT': 'Documents',
              'IMAGE': 'Images', 'VIDEO': 'Videos'}
SOURCE_PROJECTS = (SERVICE + ':ListDataAutomationProjects'
                   '+GetDataAutomationProject+GetBlueprint')


def project_blueprint_types(ctx):
    """Return {project stage: {modality: blueprint count}} for every project."""
    counts = {}
    # One filter only, as for blueprints; the stage filter keeps service
    # projects out and both stages in.
    for summary in ctx.call(SERVICE, 'list_data_automation_projects', 'projects',
                            projectStageFilter='ALL'):
        arn = required_id(summary, 'projectArn')
        stage = summary.get('projectStage')
        if stage not in {'LIVE', 'DEVELOPMENT'}:
            raise NoData('Data Automation project inventory has an unknown stage')
        identity = f'{arn}/{stage}'
        if identity in counts:
            continue
        # A project with no blueprints still holds the quota at zero, so the
        # tally is created before its contents are read.
        tally = counts.setdefault(identity, dict.fromkeys(MODALITIES, 0))
        project = ctx.call(SERVICE, 'get_data_automation_project', projectArn=arn,
                           projectStage=stage).get('project')
        if not isinstance(project, dict) or project.get('projectArn') != arn:
            raise NoData('Data Automation project detail does not match its requested identity')
        for entry in (project.get('customOutputConfiguration') or {}).get('blueprints') or []:
            blueprint = required_id(entry, 'blueprintArn')
            detail = ctx.call(SERVICE, 'get_blueprint', blueprintArn=blueprint).get('blueprint')
            if not isinstance(detail, dict) or detail.get('blueprintArn') != blueprint:
                raise NoData('Blueprint detail does not match its requested identity')
            kind = detail.get('type')
            if kind not in MODALITIES:
                raise NoData('Blueprint detail names no recognised modality')
            tally[kind] += 1
    return counts


def blueprints_per_project(ctx, modality):
    counts = project_blueprint_types(ctx)
    return maximum([(identity, tally[modality], None)
                    for identity, tally in sorted(counts.items())],
                   'DataAutomationProject', SOURCE_PROJECTS)


def libraries(ctx):
    items = ctx.call(SERVICE, 'list_data_automation_libraries', 'libraries')
    return sorted({required_id(item, 'libraryArn') for item in items})


def library_count(ctx):
    return dict(usage=len(libraries(ctx)), source='bedrock-data-automation:ListDataAutomationLibraries', method='ACCOUNT_COUNT')


def vocabulary_phrases(ctx):
    values = []
    for arn in libraries(ctx):
        counts = {}
        for item in ctx.call(SERVICE, 'list_data_automation_library_entities', 'entities',
                             libraryArn=arn, entityType='VOCABULARY'):
            if not isinstance(item, dict) or set(item) != {'vocabulary'} or not isinstance(item['vocabulary'], dict):
                raise NoData('Data Automation library returned an unknown entity type')
            vocabulary = item['vocabulary']
            identity = required_id(vocabulary, 'entityId')
            count = vocabulary.get('numOfPhrases')
            if type(count) is not int or count < 0:
                raise NoData('Data Automation vocabulary has no valid phrase count')
            if identity in counts and counts[identity] != count:
                raise NoData('Data Automation vocabulary changed during pagination')
            counts[identity] = count
        # The quota applies across all languages in one library, not to the
        # largest language/entity. Summaries suffice; phrase text is not read.
        values.append((arn, sum(counts.values()), None))
    return maximum(values, 'DataAutomationLibrary', 'bedrock-data-automation:ListDataAutomationLibraryEntities')


CHECKS = [
    ('L-21EE8B55', 'Versions per blueprint', blueprint_versions),
    ('L-D3894D44', 'JSON blueprint size in characters', blueprint_size),
    ('L-B370112A', 'Data automation libraries per account', library_count),
    ('L-EA764586', 'Vocabulary phrases per library', vocabulary_phrases),
    ('L-6BF35027', '(Data Automation) Maximum Blueprints per Project (Audios)',
     lambda ctx: blueprints_per_project(ctx, 'AUDIO')),
    ('L-A938DC68', '(Data Automation) Maximum Blueprints per Project (Documents)',
     lambda ctx: blueprints_per_project(ctx, 'DOCUMENT')),
    ('L-15868B7E', '(Data Automation) Maximum Blueprints per Project (Images)',
     lambda ctx: blueprints_per_project(ctx, 'IMAGE')),
    ('L-F5FD68DB', '(Data Automation) Maximum Blueprints per Project (Videos)',
     lambda ctx: blueprints_per_project(ctx, 'VIDEO')),
]
