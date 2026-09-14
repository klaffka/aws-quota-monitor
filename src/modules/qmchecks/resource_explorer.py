from modules.qmcore.aws import CheckContext, session_from_env
CHECKS=[('L-AE5C2578','Views',lambda c:dict(usage=len(c.call('resource-explorer-2','list_views','Views')),source='resource-explorer-2:ListViews',method='ACCOUNT_COUNT'))]
def get_current_quotastatus_resource_explorer(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env()); return c.run('resource-explorer-2',CHECKS,skip) if any(s=='resource-explorer-2' for s,_ in c.quotas) else []
