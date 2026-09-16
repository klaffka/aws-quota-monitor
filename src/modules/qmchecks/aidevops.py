"""AWS DevOps agent space inventory.

The concurrency quotas count evaluations, investigations and on-demand
invocations in flight, which the API reports only per task execution.
`memories-per-memory-store` and `memory-stores-per-agent-space` have no listing
operation.
"""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

DEVOPS = 'devops-agent'


def agent_spaces(ctx):
    found = set()
    for space in ctx.call(DEVOPS, 'list_agent_spaces', 'agentSpaces'):
        identity = space.get('agentSpaceId')
        if not isinstance(identity, str) or not identity:
            raise NoData('DevOps agent space is missing its identity')
        found.add(identity)
    return found


CHECKS = [('L-510AF4A9', 'agent-spaces-per-account-per-region',
           lambda ctx: dict(usage=len(agent_spaces(ctx)),
                            source='devops-agent:ListAgentSpaces',
                            method='ACCOUNT_COUNT'))]


def get_current_quotastatus_aidevops(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'aidevops' for service, _ in context.quotas):
        return []
    return context.run('aidevops', CHECKS, skip)
