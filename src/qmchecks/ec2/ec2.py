import boto3
import time

def get_current_quotastatus_ec2(session=None):
    ec2Quotas = []
    accountId = session.client('sts').get_caller_identity().get('Account')
    if session is None:
        session = boto3.Session()
    quotasClient = session.client('service-quotas')
    utalizationReport = quota_utilization_report_ec2(session=session)
    for quota in utalizationReport['Quotas']:
        quota_entry = {
            "PK": f"QUOTA#{accountId}#{quota['ServiceCode']}#{quota['QuotaCode']}",
            "SK": f"TS#{utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')}",
            "accountId": accountId,
            "region": session.region_name,
            "serviceCode": quota['ServiceCode'],
            "quotaCode": quota['QuotaCode'],
            "quotaName": quota['QuotaName'],
            "scopeType": "ACCOUNT_REGION",
            "limitValue": quota['AppliedValue'],
            "usageValue": quota['Utilization']/100 * quota['AppliedValue'] if quota['AppliedValue'] > 0 else 0,
            "utilizationPct": quota['Utilization'],
            "unit": None,
            "maxResourceType": None,
            "maxResourceId": None,
            "maxResourceMeta": None,
            "collectorType": "QUOTA_UTILIZATION_REPORT",
            "dataSource": "service-quotas: GetQuotaUtilizationReport",
            "calculationMethod": "QUOTA_UTILIZATION_REPORT",
            "collectedAt": utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            "ttl": int(time.time()) + 64 * 24 * 3600  # 64 days TTL

        }

        ec2Quotas.append(quota_entry)
    # L-70015FFA AMI Sharing
    quota_entry = {}
    amiSharings = AMI_Sharing_quota_check(session=session)
    quota_entry['PK'] = f"QUOTA#{accountId}#ec2#L-70015FFA"
    quota_entry['SK'] = f"TS#{utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')}"
    quota_entry['accountId'] = accountId
    quota_entry['region'] = session.region_name
    quota_entry['serviceCode'] = 'ec2'
    quota_entry['quotaCode'] = 'L-70015FFA'
    quota_entry['quotaName'] = 'AMI Sharing'
    quota_entry['scopeType'] = 'ACCOUNT_REGION'
    quota_entry['limitValue'] = max([ami['currentLimit'] for ami in amiSharings]) if amiSharings else 0
    quota_entry['usageValue'] = max([ami['usage']/100 * ami['currentLimit'] if ami['currentLimit'] > 0 else 0 for ami in amiSharings]) if amiSharings else 0
    quota_entry['utilizationPct'] = max([ami['usage']/100 * ami['currentLimit'] if ami['currentLimit'] > 0 else 0 for ami in amiSharings]) if amiSharings else 0
    quota_entry['unit'] = 'Count'
    quota_entry['maxResourceType'] = 'AMI'
    quota_entry['maxResourceId'] = max(amiSharings, key=lambda x: x['usage'])['ImageId'] if amiSharings else None
    quota_entry['maxResourceMeta'] = None
    quota_entry['collectorType'] = 'PER_RESOURCE_MAX'
    quota_entry['dataSource'] = 'ec2:DescribeImageAttribute'
    quota_entry['calculationMethod'] = 'PER_RESOURCE_MAX'
    quota_entry['collectedAt'] = utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')
    quota_entry['ttl'] = int(time.time()) + 64 * 24 * 3600  # 64 days TTL
    ec2Quotas.append(quota_entry)
    # L-6DA43717 Attachments per VPC (deprecated, but still in use)
    #vpcAttachments = VPC_Attachments_quota_check(session=session)
    #ec2Quotas['L-6DA43717'] = vpcAttachments
    # L-9A1BC94B Authrization rules per Client VPN endpoint
    quota_entry = {}
    clientVpnAuthRules = Client_VPN_Authorization_Rules_quota_check(session=session)
    quota_entry['PK'] = f"QUOTA#{accountId}#ec2#L-9A1BC94B"
    quota_entry['SK'] = f"TS#{utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')}"
    quota_entry['accountId'] = accountId
    quota_entry['region'] = session.region_name
    quota_entry['serviceCode'] = 'ec2'
    quota_entry['quotaCode'] = 'L-9A1BC94B'
    quota_entry['quotaName'] = 'Authorization rules per Client VPN endpoint'
    quota_entry['scopeType'] = 'ACCOUNT_REGION'
    quota_entry['limitValue'] = clientVpnAuthRules['currentLimit']
    quota_entry['usageValue'] = clientVpnAuthRules['usage']
    quota_entry['utilizationPct'] = clientVpnAuthRules['usage']/100 * clientVpnAuthRules['currentLimit'] if clientVpnAuthRules['currentLimit'] > 0 else 0
    quota_entry['unit'] = 'Count'
    quota_entry['maxResourceType'] = None
    quota_entry['maxResourceId'] = None
    quota_entry['maxResourceMeta'] = None
    quota_entry['collectorType'] = 'PER_RESOURCE_MAX'
    quota_entry['dataSource'] = 'ec2:DescribeClientVpnAuthorizationRules'
    quota_entry['calculationMethod'] = 'PER_RESOURCE_MAX'
    quota_entry['collectedAt'] = utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')
    quota_entry['ttl'] = int(time.time()) + 64 * 24 * 3600  # 64 days TTL
    ec2Quotas.append(quota_entry)
    # L-8EA77D34 Client VPN endpoints
    quota_entry = {}
    clientVpnEndpoints = Client_VPN_Endpoints_quota_check(session=session)
    quota_entry['PK'] = f"QUOTA#{accountId}#ec2#L-8EA77D34"
    quota_entry['SK'] = f"TS#{utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')}"
    quota_entry['accountId'] = accountId
    quota_entry['region'] = session.region_name
    quota_entry['serviceCode'] = 'ec2'
    quota_entry['quotaCode'] = 'L-8EA77D34'
    quota_entry['quotaName'] = 'Client VPN endpoints'
    quota_entry['scopeType'] = 'ACCOUNT_REGION'
    quota_entry['limitValue'] = clientVpnEndpoints['currentLimit']
    quota_entry['usageValue'] = clientVpnEndpoints['usage']
    quota_entry['utilizationPct'] = clientVpnEndpoints['usage']/100 * clientVpnEndpoints['currentLimit'] if clientVpnEndpoints['currentLimit'] > 0 else 0
    quota_entry['unit'] = 'Count'
    quota_entry['maxResourceType'] = None
    quota_entry['maxResourceId'] = None
    quota_entry['maxResourceMeta'] = None
    quota_entry['collectorType'] = 'PER_RESOURCE_MAX'
    quota_entry['dataSource'] = 'ec2:DescribeClientVpnEndpoints'
    quota_entry['calculationMethod'] = 'PER_RESOURCE_MAX'
    quota_entry['collectedAt'] = utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')
    quota_entry['ttl'] = int(time.time()) + 64 * 24 * 3600  # 64 days TTL
    ec2Quotas.append(quota_entry)
    # L-2C8F52B3 Concurrent P4d Capacity Blocks per account
    quota_entry = {}
    p4dBlocks = P4d_Blocks_quota_check(session=session)
    quota_entry['PK'] = f"QUOTA#{accountId}#ec2#L-2C8F52B3"
    quota_entry['SK'] = f"TS#{utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')}"
    quota_entry['accountId'] = accountId
    quota_entry['region'] = session.region_name
    quota_entry['serviceCode'] = 'ec2'
    quota_entry['quotaCode'] = 'L-2C8F52B3'
    quota_entry['quotaName'] = 'Concurrent P4d Capacity Blocks per account'
    quota_entry['scopeType'] = 'ACCOUNT_REGION'
    quota_entry['limitValue'] = p4dBlocks['currentLimit']
    quota_entry['usageValue'] = p4dBlocks['usage']
    quota_entry['utilizationPct'] = p4dBlocks['usage']/100 * p4dBlocks['currentLimit'] if p4dBlocks['currentLimit'] > 0 else 0
    quota_entry['unit'] = 'Count'
    quota_entry['maxResourceType'] = None
    quota_entry['maxResourceId'] = None
    quota_entry['maxResourceMeta'] = None
    quota_entry['collectorType'] = 'PER_RESOURCE_MAX'
    quota_entry['dataSource'] = 'ec2:DescribeInstances'
    quota_entry['calculationMethod'] = 'PER_RESOURCE_MAX'
    quota_entry['collectedAt'] = utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')
    quota_entry['ttl'] = int(time.time()) + 64 * 24 * 3600  # 64 days TTL
    ec2Quotas.append(quota_entry)
  
    # L-CFF3E941 Concurrent P4de Capacity Blocks per account
    quota_entry = {}
    p4deBlocks = P4de_Blocks_quota_check(session=session)
    quota_entry['PK'] = f"QUOTA#{accountId}#ec2#L-CFF3E941"
    quota_entry['SK'] = f"TS#{utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')}"
    quota_entry['accountId'] = accountId
    quota_entry['region'] = session.region_name
    quota_entry['serviceCode'] = 'ec2'
    quota_entry['quotaCode'] = 'L-CFF3E941'
    quota_entry['quotaName'] = 'Concurrent P4de Capacity Blocks per account'
    quota_entry['scopeType'] = 'ACCOUNT_REGION'
    quota_entry['limitValue'] = p4deBlocks['currentLimit']
    quota_entry['usageValue'] = p4deBlocks['usage']
    quota_entry['utilizationPct'] = p4deBlocks['usage']/100 * p4deBlocks['currentLimit'] if p4deBlocks['currentLimit'] > 0 else 0
    quota_entry['unit'] = 'Count'
    quota_entry['maxResourceType'] = None
    quota_entry['maxResourceId'] = None
    quota_entry['maxResourceMeta'] = None
    quota_entry['collectorType'] = 'PER_RESOURCE_MAX'
    quota_entry['dataSource'] = 'ec2:DescribeInstances'
    quota_entry['calculationMethod'] = 'PER_RESOURCE_MAX'
    quota_entry['collectedAt'] = utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')
    quota_entry['ttl'] = int(time.time()) + 64 * 24 * 3600  # 64 days TTL
    ec2Quotas.append(quota_entry)
    return ec2Quotas

def P4de_Blocks_quota_check(session=None):
    # check P4de Blocks quota
    ec2Client = session.client('ec2')
    quotasClient = session.client('service-quotas')
    response = quotasClient.get_service_quota(
        ServiceCode='ec2',
        QuotaCode='L-CFF3E941'  
    )
    current_quota_value = response['Quota']['Value']

    quota_info = {}
    quota_info['currentLimit'] = current_quota_value
    quota_info['usage'] = 0

    allInstances = ec2Client.describe_instances(
        Filters=[
            {
                'Name': 'instance-type',
                'Values': ['p4de.24xlarge']
            },
        ]
    )
    instance_count = 0
    for reservation in allInstances['Reservations']:
        instance_count += len(reservation['Instances'])
    quota_info['usage'] = instance_count // 8  
    return quota_info

def P4d_Blocks_quota_check(session=None):
    # check P4d Blocks quota
    ec2Client = session.client('ec2')
    quotasClient = session.client('service-quotas')
    response = quotasClient.get_service_quota(
        ServiceCode='ec2',
        QuotaCode='L-2C8F52B3'  
    )
    current_quota_value = response['Quota']['Value']

    quota_info = {}
    quota_info['currentLimit'] = current_quota_value
    quota_info['usage'] = 0

    allInstances = ec2Client.describe_instances(
        Filters=[
            {
                'Name': 'instance-type',
                'Values': ['p4d.24xlarge']
            },
        ]
    )
    instance_count = 0
    for reservation in allInstances['Reservations']:
        instance_count += len(reservation['Instances'])
    quota_info['usage'] = instance_count // 8  
    return quota_info

def Client_VPN_Endpoints_quota_check(session=None):
    # check Client VPN Endpoints quota
    ec2Client = session.client('ec2')
    quotasClient = session.client('service-quotas')
    response = quotasClient.get_service_quota(
        ServiceCode='ec2',
        QuotaCode='L-8EA77D34'  
    )
    current_quota_value = response['Quota']['Value']

    quota_info = {}
    quota_info['currentLimit'] = current_quota_value
    quota_info['usage'] = 0

    allClientVpnEndpoints = ec2Client.describe_client_vpn_endpoints()
    quota_info['usage'] = len(allClientVpnEndpoints['ClientVpnEndpoints'])
    return quota_info

def Client_VPN_Authorization_Rules_quota_check(session=None):
    # check Client VPN Authorization Rules quota
    ec2Client = session.client('ec2')
    quotasClient = session.client('service-quotas')
    response = quotasClient.get_service_quota(
        ServiceCode='ec2',
        QuotaCode='L-9A1BC94B'  
    )
    current_quota_value = response['Quota']['Value']

    quota_info = {}
    quota_info['currentLimit'] = current_quota_value
    quota_info['usage'] = 0

    allClientVpnEndpoints = ec2Client.describe_client_vpn_endpoints()
    for endpoint in allClientVpnEndpoints['ClientVpnEndpoints']:
        response = ec2Client.describe_client_vpn_authorization_rules(
            ClientVpnEndpointId=endpoint['ClientVpnEndpointId']
        )
        quota_info['usage'] += len(response['AuthorizationRules'])
    return quota_info

def VPC_Attachments_quota_check(session=None):
    # check VPC Attachments quota
    ec2Client = session.client('ec2')
    quotasClient = session.client('service-quotas')
    response = quotasClient.get_service_quota(
        ServiceCode='ec2',
        QuotaCode='L-6DA43717'  
    )
    current_quota_value = response['Quota']['Value']

    quota_info = {}
    quota_info['currentLimit'] = current_quota_value
    quota_info['usage'] = 0

    allVpcs = ec2Client.describe_vpcs()
    for vpc in allVpcs['Vpcs']:
        response = ec2Client.describe_vpc_attachments(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [vpc['VpcId']]
                },
            ]
        )
        quota_info['usage'] += len(response['VpcAttachments'])
    return quota_info

def AMI_Sharing_quota_check(session=None):
    # check AMI Sharing quota and report the AMI with the most shared accounts
    ec2Client = session.client('ec2')
    quotasClient = session.client('service-quotas')
    response = quotasClient.get_service_quota(
        ServiceCode='ec2',
        QuotaCode='L-70015FFA'  
    )
    current_quota_value = response['Quota']['Value']

    quota=[]
    allImages = ec2Client.describe_images(Owners=['self'])
    for image in allImages['Images']:
        image_info = {}
        image_info['ImageId'] = image['ImageId']
        image_info['region'] = session.region_name
        image_info['currentLimit'] = current_quota_value
        image_info['usage'] = 0
        response = ec2Client.describe_image_attribute(
            ImageId=image['ImageId'],
            Attribute='launchPermission'
        )
        if 'LaunchPermissions' in response:
            for lp in response['LaunchPermissions']:
                if 'UserId' in lp:
                    image_info['usage'] = image_info['usage'] + 1
                if 'OrganizationArn' in lp:
                    image_info['usage'] = image_info['usage'] + 1
                if 'OrganizationalUnitArn' in lp:
                    image_info['usage'] = image_info['usage'] + 1
                if lp.get('Group','') == 'all':
                    image_info['usage'] = image_info['usage'] + 1
        quota.append(image_info)
    return quota

def quota_utilization_report_ec2(session=None):
        # Generate a quota utilization report for EC2 quotas
        if session is None:
            session = boto3.Session()
        client = session.client('service-quotas')
        response = client.start_quota_utilization_report()
        report_id = response['ReportId']
        while response['Status'] != 'COMPLETED':
            time.sleep(1)
            response = client.get_quota_utilization_report(ReportId=report_id)
        response = client.get_quota_utilization_report(ReportId=report_id)
        return response