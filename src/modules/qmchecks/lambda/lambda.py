import boto3

def get_current_quotastatus_lambda(session=None):
    """Get current quota status for AWS Lambda service"""
    if session is None:
        session = boto3.Session()
    
    accountId = session.client('sts').get_caller_identity().get('Account')
    
    # Filter for Lambda service quotas
    lambdaQuotas = [quota for quota in lambdaQuotas if quota['serviceCode'] == 'lambda']
    
    return lambdaQuotas

def Async_invocation_request_throughput_on_Lambda_Managed_Instances_quota_check(session=None):
    """Check the usage quota for Asynchronous invocation request throughput on Lambda Managed Instances"""
    if session is None:
        session = boto3.Session()
    
    lambdaClient = session.client('lambda')
    quotasClient = session.client('service-quotas')
    cloudwatchClient = session.client('cloudwatch')
    
    # Get the quota limit
    response = quotasClient.get_service_quota(
        ServiceCode='lambda',
        QuotaCode='L-A723F9CC'
    )
    current_quota_value = response['Quota']['Value']
    
    quota_info = {}
    quota_info['currentLimit'] = current_quota_value
    quota_info['usage'] = 0
    
    # Get asynchronous invocation metrics from CloudWatch
    # This metric represents the throughput of asynchronous invocations
    try:
        response = cloudwatchClient.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='AsyncInvocations',
            StartTime=boto3.client('sts').get_caller_identity(),
            Period=300,
            Statistics=['Sum']
        )
        if response['Datapoints']:
            # Get the most recent metric value
            quota_info['usage'] = int(response['Datapoints'][-1]['Sum'])
    except:
        # If metric is not available, usage remains 0
        quota_info['usage'] = 0
    
    return quota_info

"""
AWS Lambda Quota Codes:
L-A723F9CC Asynchronous invocation request throughput on Lambda Managed Instances
L-7C0F49F9
L-F864D568
L-A1AFA3CF
L-8E39F3F1
L-75F48B05
L-E49FF7B8
L-560437FE
L-7E8754C7
L-6581F036
L-438DAE3B
L-2ACBD22F
L-A0D6E196
L-01237738
L-07A00131
L-9FEEFFC0
L-2713A7D4
L-C952DDE4
L-2EBBB6B4
L-42D0A120
L-ABBF0CF3
L-77C8EE9D
L-DF87A8A6
L-9B52FC60
L-BA29C22B
L-50EA21A9
L-37540937
L-4273958C
L-6A3611ED
L-88CBC2FA
L-133D658A
L-B82A30EA
L-4C4550DE
L-B2AA0F47
L-0A4FC1E6
L-5C4B2C97
L-AD930C90
"""