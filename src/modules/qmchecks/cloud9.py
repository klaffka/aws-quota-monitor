from modules.qmcore.aws import CheckContext, session_from_env
CHECKS=[('L-8ECD6BDB','EC2 development environments for this account',lambda c:dict(usage=len(c.call('cloud9','list_environments','environmentIds')),source='cloud9:ListEnvironments',method='ACCOUNT_COUNT'))]
def get_current_quotastatus_cloud9(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env()); return c.run('cloud9',CHECKS,skip) if any(s=='cloud9' for s,_ in c.quotas) else []
