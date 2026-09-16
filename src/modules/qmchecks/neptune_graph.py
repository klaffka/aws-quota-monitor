from modules.qmcore.aws import CheckContext, session_from_env
CHECKS=[('L-D31591F1','Maximum Graphs',lambda c:dict(usage=len(c.call('neptune-graph','list_graphs','graphs')),source='neptune-graph:ListGraphs',method='ACCOUNT_COUNT'))]
def get_current_quotastatus_neptune_graph(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env()); return c.run('neptune-graph',CHECKS,skip) if any(s=='neptune-graph' for s,_ in c.quotas) else []
