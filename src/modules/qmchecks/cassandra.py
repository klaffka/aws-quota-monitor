from modules.qmcore.aws import CheckContext, session_from_env
def count(c,m,k): return dict(usage=len(c.call('cassandra',m,k)),source=f'cassandra:{m}',method='ACCOUNT_COUNT')
CHECKS=[('L-BF48748A','Tables per region',lambda c:count(c,'list_tables','tables')),('L-677FFD22','Keyspaces per region',lambda c:count(c,'list_keyspaces','keyspaces'))]
def get_current_quotastatus_cassandra(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env()); return c.run('cassandra',CHECKS,skip) if any(s=='cassandra' for s,_ in c.quotas) else []
