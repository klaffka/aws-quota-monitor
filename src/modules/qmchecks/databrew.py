"""AWS Glue DataBrew regional counts and ruleset scopes.

`Concurrent jobs` and `Node capacity` stay in the audit: both bound what is
running right now, and a job run reports its capacity only while it lasts.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def _per_account(ctx, method, key):
    return dict(usage=len(ctx.call('databrew', method, key)),
                source=f'databrew:{method}', method='ACCOUNT_COUNT')

def _rulesets(ctx):
    """ListRulesets carries both the rule count and the dataset it targets."""
    for entry in ctx.call('databrew', 'list_rulesets', 'Rulesets'):
        name = entry.get('Name')
        if not isinstance(name, str) or not name:
            raise NoData('DataBrew ruleset is missing its name')
        yield name, entry


def rules_per_ruleset(ctx):
    values = []
    for name, entry in _rulesets(ctx):
        rules = entry.get('RuleCount')
        if not isinstance(rules, int):
            raise NoData('DataBrew ruleset reports no rule count')
        values.append((name, rules, None))
    return maximum(values, 'DataBrewRuleset', 'databrew:ListRulesets')


def rulesets_per_dataset(ctx):
    counts = {}
    for _name, entry in _rulesets(ctx):
        target = entry.get('TargetArn')
        if not isinstance(target, str) or not target:
            raise NoData('DataBrew ruleset names no target dataset')
        counts[target] = counts.get(target, 0) + 1
    return maximum([(target, count, None) for target, count in sorted(counts.items())],
                   'DataBrewDataset', 'databrew:ListRulesets')


def open_projects(ctx):
    """A project is open while DataBrew records who opened it."""
    projects = ctx.call('databrew', 'list_projects', 'Projects')
    return dict(usage=sum(bool(project.get('OpenedBy')) for project in projects),
                source='databrew:ListProjects', method='ACCOUNT_COUNT')


def versions_per_recipe(ctx):
    values = []
    for recipe in ctx.call('databrew', 'list_recipes', 'Recipes'):
        name = recipe.get('Name')
        if not isinstance(name, str) or not name:
            raise NoData('DataBrew recipe is missing its name')
        values.append((name, len(ctx.call('databrew', 'list_recipe_versions', 'Recipes',
                                          Name=name)), None))
    return maximum(values, 'DataBrewRecipe', 'databrew:ListRecipeVersions')


CHECKS = [('L-CE9E9D8D', 'Projects per AWS account',
           lambda c: dict(usage=len(c.call('databrew', 'list_projects', 'Projects')),
                          source='databrew:ListProjects', method='ACCOUNT_COUNT')),
          ('L-940C8930', 'Datasets per AWS account',
           lambda c: _per_account(c, 'list_datasets', 'Datasets')),
          ('L-955A1FA6', 'Rulesets per AWS account',
           lambda c: _per_account(c, 'list_rulesets', 'Rulesets')),
          ('L-BF3E0A94', 'Schedules per AWS account',
           lambda c: _per_account(c, 'list_schedules', 'Schedules')),
          ('L-EE2782A4', 'Recipes per AWS account',
           lambda c: _per_account(c, 'list_recipes', 'Recipes')),
          ('L-0D2C4DFC', 'Jobs per AWS account',
           lambda c: _per_account(c, 'list_jobs', 'Jobs')),
          ('L-5748848E', 'Open projects per AWS account', open_projects),
          ('L-640ABD4F', 'Rules per ruleset', rules_per_ruleset),
          ('L-131D2768', 'Rulesets per dataset', rulesets_per_dataset),
          ('L-A386FCB8', 'Versions per recipe', versions_per_recipe)]


def get_current_quotastatus_databrew(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'databrew' for service, _ in context.quotas): return []
    return context.run('databrew', CHECKS, skip)
