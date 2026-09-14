from modules.qmcore.aws import CheckContext, maximum, session_from_env
def access_points_per_file_system(ctx):
    values=[]
    for fs in ctx.call('elasticfilesystem','describe_file_systems','FileSystems'):
        fid=fs['FileSystemId']; aps=ctx.call('elasticfilesystem','describe_access_points','AccessPoints',FileSystemId=fid)
        values.append((fid,len(aps),None))
    return maximum(values,'FileSystem','elasticfilesystem:DescribeAccessPoints')
CHECKS=[('L-848C634D','File systems per account',lambda c:dict(usage=len(c.call('elasticfilesystem','describe_file_systems','FileSystems')),source='elasticfilesystem:DescribeFileSystems',method='ACCOUNT_COUNT')),
        ('L-4CCB99B3','Access points per file system',access_points_per_file_system)]
def get_current_quotastatus_efs(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env()); return c.run('elasticfilesystem',CHECKS,skip) if any(s=='elasticfilesystem' for s,_ in c.quotas) else []
