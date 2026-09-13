from modules.qmcore.aws import CheckContext, maximum, session_from_env
def deployment_groups_per_application(c):
 vals=[]
 for app in c.call('codedeploy','list_applications','applications'):
  groups=c.call('codedeploy','list_deployment_groups','deploymentGroups',applicationName=app)
  vals.append((app,len(groups),None))
 return maximum(vals,'Application','codedeploy:ListDeploymentGroups')
CHECKS=[('L-3F19B6A5','Applications associated per account per region',lambda c:dict(usage=len(c.call('codedeploy','list_applications','applications')),source='codedeploy:ListApplications',method='ACCOUNT_COUNT')),
('L-D9088B77','Deployment groups associated with a single application',deployment_groups_per_application)]
def get_current_quotastatus_codedeploy(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env())
 return c.run('codedeploy',CHECKS,skip) if any(s=='codedeploy' for s,_ in c.quotas) else []
