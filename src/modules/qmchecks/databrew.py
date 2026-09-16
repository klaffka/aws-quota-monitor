"""AWS Glue DataBrew regional project counts."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def _per_account(ctx, method, key):
    return dict(usage=len(ctx.call('databrew', method, key)),
                source=f'databrew:{method}', method='ACCOUNT_COUNT')

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
           lambda c: _per_account(c, 'list_recipes', 'Recipes'))]


def get_current_quotastatus_databrew(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'databrew' for service, _ in context.quotas): return []
    return context.run('databrew', CHECKS, skip)
