from modules.qmcore.aws import CheckContext, session_from_env
CHECKS=[('L-CD70CADB','Ledgers',lambda c:dict(usage=len(c.call('qldb','list_ledgers','Ledgers')),source='qldb:ListLedgers',method='ACCOUNT_COUNT'))]
def get_current_quotastatus_qldb(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env()); return c.run('qldb',CHECKS,skip) if any(s=='qldb' for s,_ in c.quotas) else []
