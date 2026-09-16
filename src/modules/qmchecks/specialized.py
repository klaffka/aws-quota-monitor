"""Resource-count quotas for Clean Rooms, Verified Permissions and App Mesh."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env

# A protected query or job occupies its slot until it reaches a terminal state.
# ListProtectedQueries filters by one status per request, so asking for the
# ongoing ones costs three bounded calls instead of reading the whole history.
ONGOING_QUERY_STATES = ('SUBMITTED', 'STARTED', 'CANCELLING')
ONGOING_JOB_STATES = ('SUBMITTED', 'STARTED', 'CANCELLING')

CUSTOM_KEYS = {
    ('cleanrooms', code) for code in ('L-F60C2030', 'L-99A163CB', 'L-7CEACCA0',
                                      'L-AF88CE55', 'L-25AC34A7', 'L-6359BE00',
                                      'L-DBDCEC0D', 'L-4596E0C1', 'L-6FE25843',
                                      'L-F7B26AF5', 'L-40165B7B', 'L-F04AAAFE',
                                      'L-B45D79BC', 'L-844B7ECC')
} | {('verifiedpermissions', code) for code in ('L-919F2C9C', 'L-97BDA0CF')}


def cleanrooms_checks(ctx):
    def membership_max(method, key, quota_name):
        def check(c):
            values = []
            for membership in c.call('cleanrooms', 'list_memberships', 'membershipSummaries'):
                mid = membership.get('id')
                values.append((mid, len(c.call('cleanrooms', method, key,
                                               membershipIdentifier=mid)), None))
            return maximum(values, 'Membership', f'cleanrooms:{method}')
        return check
    def collaboration_privacy_templates(c):
        values = []
        for collaboration in c.call('cleanrooms', 'list_collaborations', 'collaborationList'):
            cid = collaboration.get('id')
            values.append((cid, len(c.call('cleanrooms', 'list_collaboration_privacy_budget_templates',
                                            'collaborationPrivacyBudgetTemplateSummaries',
                                            collaborationIdentifier=cid)), None))
        return maximum(values, 'Collaboration', 'cleanrooms:ListCollaborationPrivacyBudgetTemplates')
    def invited_members_per_collaboration(c):
        values = []
        for collaboration in c.call('cleanrooms', 'list_collaborations', 'collaborationList'):
            cid = collaboration.get('id')
            if cid:
                invited = [member for member in c.call(
                    'cleanrooms', 'list_members', 'memberSummaries',
                    collaborationIdentifier=cid) if member.get('status') == 'INVITED']
                values.append((cid, len(invited), None))
        return maximum(values, 'Collaboration', 'cleanrooms:ListMembers(status=INVITED)')
    def ongoing_per_membership(c, method, key, states):
        """Return (membership, ongoing count) for every membership."""
        values = []
        for membership in c.call('cleanrooms', 'list_memberships', 'membershipSummaries'):
            mid = membership.get('id')
            if not mid:
                continue
            ongoing = sum(len(c.call('cleanrooms', method, key,
                                     membershipIdentifier=mid, status=state))
                          for state in states)
            values.append((mid, ongoing))
        return values

    def ongoing_account(method, key, states, source):
        def check(c):
            values = ongoing_per_membership(c, method, key, states)
            return dict(usage=sum(count for _mid, count in values),
                        source=source, method='ACCOUNT_SUM')
        return check

    def ongoing_membership(method, key, states, source):
        def check(c):
            values = ongoing_per_membership(c, method, key, states)
            return maximum([(mid, count, None) for mid, count in values],
                           'Membership', source)
        return check

    queries = ('list_protected_queries', 'protectedQueries', ONGOING_QUERY_STATES,
               'cleanrooms:ListProtectedQueries(ongoing)')
    jobs = ('list_protected_jobs', 'protectedJobs', ONGOING_JOB_STATES,
            'cleanrooms:ListProtectedJobs(ongoing)')
    return [
        ('L-40165B7B', 'Concurrent SQL queries per account', ongoing_account(*queries)),
        ('L-F04AAAFE', 'Concurrent ongoing queries per membership', ongoing_membership(*queries)),
        ('L-B45D79BC', 'Concurrent PySpark jobs per account', ongoing_account(*jobs)),
        ('L-844B7ECC', 'Concurrent ongoing job per membership', ongoing_membership(*jobs)),
        ('L-F60C2030', 'Collaborations created per account',
         lambda c: dict(usage=len(c.call('cleanrooms', 'list_collaborations', 'collaborationList')),
                        source='cleanrooms:ListCollaborations', method='ACCOUNT_COUNT')),
        ('L-99A163CB', 'Memberships per account',
         lambda c: dict(usage=len(c.call('cleanrooms', 'list_memberships', 'membershipSummaries')),
                        source='cleanrooms:ListMemberships', method='ACCOUNT_COUNT')),
        ('L-7CEACCA0', 'Configured tables per account',
         lambda c: dict(usage=len(c.call('cleanrooms', 'list_configured_tables', 'configuredTableSummaries')),
                        source='cleanrooms:ListConfiguredTables', method='ACCOUNT_COUNT')),
        ('L-AF88CE55', 'Analysis templates per membership',
         membership_max('list_analysis_templates', 'analysisTemplateSummaries', 'AnalysisTemplate')),
        ('L-25AC34A7', 'Table associations per membership',
         membership_max('list_configured_table_associations', 'configuredTableAssociationSummaries', 'TableAssociation')),
        ('L-6359BE00', 'ID namespace associations per membership',
         membership_max('list_id_namespace_associations', 'idNamespaceAssociationSummaries', 'IdNamespaceAssociation')),
        ('L-DBDCEC0D', 'ID mapping tables per membership',
         membership_max('list_id_mapping_tables', 'idMappingTableSummaries', 'IdMappingTable')),
        ('L-4596E0C1', 'Configured audience model associations per membership',
         membership_max('list_configured_audience_model_associations', 'configuredAudienceModelAssociationSummaries', 'AudienceModelAssociation')),
        ('L-6FE25843', 'Privacy budget templates for access budgets per collaboration',
         collaboration_privacy_templates),
        ('L-F7B26AF5', 'Members invited per collaboration', invited_members_per_collaboration),
    ]


def verified_checks(ctx):
    def templates(c):
        values = []
        for store in c.call('verifiedpermissions', 'list_policy_stores', 'policyStores'):
            sid = store.get('policyStoreId')
            values.append((sid, len(c.call('verifiedpermissions', 'list_policy_templates', 'policyTemplates',
                                            policyStoreId=sid)), None))
        return maximum(values, 'PolicyStore', 'verifiedpermissions:ListPolicyTemplates')
    return [
        ('L-919F2C9C', 'Policy stores per Region per account',
         lambda c: dict(usage=len(c.call('verifiedpermissions', 'list_policy_stores', 'policyStores')),
                        source='verifiedpermissions:ListPolicyStores', method='ACCOUNT_COUNT')),
        ('L-97BDA0CF', 'Policy templates per policy store', templates),
    ]


def get_current_quotastatus_specialized(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    entries = []
    if any(service == 'cleanrooms' for service, _ in context.quotas):
        entries.extend(context.run('cleanrooms', cleanrooms_checks(context), skip))
    if any(service == 'verifiedpermissions' for service, _ in context.quotas):
        entries.extend(context.run('verifiedpermissions', verified_checks(context), skip))
    return entries
