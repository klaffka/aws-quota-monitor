"""Amazon Personalize regional resource inventories."""
from collections import Counter
from modules.qmcore.aws import CheckContext, session_from_env


def max_per_group(items):
    counts = Counter(item.get('datasetGroupArn') for item in items)
    return max(counts.values(), default=0)


CHECKS = [
    ('L-14011066', 'Active dataset groups',
     lambda c: dict(usage=len(c.call('personalize', 'list_dataset_groups', 'datasetGroups')),
                    source='personalize:ListDatasetGroups', method='ACCOUNT_COUNT')),
    ('L-052ECD67', 'Active campaigns per dataset group',
     lambda c: dict(usage=max_per_group(c.call('personalize', 'list_campaigns', 'campaigns')),
                    source='personalize:ListCampaigns', method='ACCOUNT_COUNT')),
    ('L-D9DD83B7', 'Active solutions per dataset group',
     lambda c: dict(usage=max_per_group(c.call('personalize', 'list_solutions', 'solutions')),
                    source='personalize:ListSolutions', method='ACCOUNT_COUNT')),
    ('L-4D685096', 'Maximum number of recommenders per dataset group',
     lambda c: dict(usage=max_per_group(c.call('personalize', 'list_recommenders', 'recommenders')),
                    source='personalize:ListRecommenders', method='ACCOUNT_COUNT')),
    ('L-037D5A71', 'Number of schemas',
     lambda c: dict(usage=len(c.call('personalize', 'list_schemas', 'schemas')),
                    source='personalize:ListSchemas', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_personalize(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'personalize' for service, _ in context.quotas):
        return []
    return context.run('personalize', CHECKS, skip)
