"""Census of the quotas that hold both a custom check and an official metric.

`main.py` builds `official` from the live catalog and passes it to every
collector as `skip`, so wherever AWS publishes a compatible usage metric the
custom check does not run: the metric is the single source of truth. A check
registered for such a quota is therefore not dead, but it is a fallback rather
than the measurement -- it only runs in an account or Region whose catalog
carries no metric for that quota.

That distinction is easy to lose. A check written for a quota AWS already
publishes a metric for looks finished, counts towards `implemented`, passes the
smoke harness, and holds an IAM grant, while never producing the number anyone
reads. The census below is what makes the choice deliberate: a new overlap
fails this test until it is listed here with the reason it is wanted.

The set may only shrink on its own. An entry that stops being an overlap --
because the check went, or because AWS withdrew the metric -- has to be removed
in the same change.
"""
import json

import pytest

from modules.qmcore.metrics import compatible
from modules.qmcore.registry import custom_keys

CATALOG = 'tests/fixtures/quota-catalog-union.json'

# Quotas measured by a custom check that AWS also publishes a compatible usage
# metric for. Each is a fallback for a catalog that does not carry the metric.
OVERLAP = frozenset({
    # appconfig (4)
    ('appconfig', 'L-A52E46BE'),  # Maximum number of environments per application
    ('appconfig', 'L-EEB0151E'),  # Maximum number of applications
    ('appconfig', 'L-F59D302B'),  # Maximum number of deployment strategies
    ('appconfig', 'L-FA210A1F'),  # Maximum number of configuration profiles per application
    # appsync (1)
    ('appsync', 'L-4DFA3D2F'),  # GraphQL APIs - APIs per region
    # aps (1)
    ('aps', 'L-8873DB23'),  # Workspaces per region per account
    # athena (1)
    ('athena', 'L-FD9D80C2'),  # Maximum number of workgroups per account
    # autoscaling (1)
    ('autoscaling', 'L-CDE20ADC'),  # Auto Scaling groups per region
    # bedrock (5)
    ('bedrock', 'L-21EE8B55'),  # (Data Automation) CreateBlueprintVersion - Max number o...
    ('bedrock', 'L-23CF4444'),  # (Data Automation) CreateBlueprint - Max number of bluep...
    ('bedrock', 'L-B783C50B'),  # (Prompt management) Prompts per account
    ('bedrock', 'L-D321719B'),  # (Flows) Flows per account
    ('bedrock', 'L-DAF06DBA'),  # (Automated Reasoning) Policies per account
    # cloudformation (5)
    ('cloudformation', 'L-0485CB21'),  # Stacks
    ('cloudformation', 'L-24E9F9ED'),  # Hooks per account
    ('cloudformation', 'L-9DE8E4FB'),  # Resource limit per account
    ('cloudformation', 'L-DCC58E6D'),  # Module limit per account
    ('cloudformation', 'L-EC62D81A'),  # Stack sets per administrator account
    # cloudhsm (1)
    ('cloudhsm', 'L-4B16B391'),  # Clusters per AWS Region and AWS account
    # cloudtrail (4)
    ('cloudtrail', 'L-1568E18E'),  # Trails per region
    ('cloudtrail', 'L-422D51DD'),  # Channels
    ('cloudtrail', 'L-F5FAD268'),  # Custom Dashboards per region
    ('cloudtrail', 'L-FAC66D2D'),  # Event data stores
    # cloudwatchpredictions (1)
    ('cloudwatchpredictions', 'L-58896C49'),  # CloudWatch Anomaly Detection models
    # directconnect (3)
    ('directconnect', 'L-42DEC0EF'),  # LAGs per Region
    ('directconnect', 'L-62B7491E'),  # Direct Connect gateways per account
    ('directconnect', 'L-A2659207'),  # Dedicated connections per location
    # dsql (1)
    ('dsql', 'L-B3A4E51E'),  # Single-Region clusters
    # dynamodb (1)
    ('dynamodb', 'L-F98FE922'),  # Maximum number of tables
    # ec2 (7)
    ('ec2', 'L-0E3CBAB9'),  # Public AMIs
    ('ec2', 'L-3E6EC3A3'),  # VPN connections per region
    ('ec2', 'L-4FB7FF5D'),  # Customer gateways per region
    ('ec2', 'L-7029FAB6'),  # Virtual private gateways per region
    ('ec2', 'L-A2478D36'),  # Transit gateways per account
    ('ec2', 'L-B665C33B'),  # AMIs
    ('ec2', 'L-B91E5754'),  # VPN connections per VGW
    # elasticache (5)
    ('elasticache', 'L-3E7F7726'),  # Subnet groups per Region
    ('elasticache', 'L-3F15A733'),  # Parameter groups per Region
    ('elasticache', 'L-80E085C7'),  # Users per Region
    ('elasticache', 'L-AD484FC5'),  # User Groups per Region
    ('elasticache', 'L-BBCDAECC'),  # Serverless Caches per Region
    # elasticloadbalancing (15)
    ('elasticloadbalancing', 'L-52964454'),  # Certificates per Network Load Balancer
    ('elasticloadbalancing', 'L-53DA6B97'),  # Application Load Balancers per Region
    ('elasticloadbalancing', 'L-57A373D6'),  # Listeners per Network Load Balancer
    ('elasticloadbalancing', 'L-69A177A2'),  # Network Load Balancers per Region
    ('elasticloadbalancing', 'L-723DCCB6'),  # Reserved Network Load Balancer Capacity Units (LCU) per...
    ('elasticloadbalancing', 'L-7E6692B2'),  # Targets per Application Load Balancer
    ('elasticloadbalancing', 'L-7EED9B64'),  # Rules per Application Load Balancer
    ('elasticloadbalancing', 'L-822D1B1B'),  # Target Groups per Application Load Balancer
    ('elasticloadbalancing', 'L-9365A611'),  # Certificates per Application Load Balancer
    ('elasticloadbalancing', 'L-A0D0B863'),  # Targets per Target Group per Region
    ('elasticloadbalancing', 'L-B211E961'),  # Targets per Availability Zone per Network Load Balancer
    ('elasticloadbalancing', 'L-B22855CB'),  # Target Groups per Region
    ('elasticloadbalancing', 'L-B6DF7632'),  # Listeners per Application Load Balancer
    ('elasticloadbalancing', 'L-E9E9831D'),  # Classic Load Balancers per Region
    ('elasticloadbalancing', 'L-EEF1AD04'),  # Targets per Network Load Balancer
    # evs (2)
    ('evs', 'L-27E780D9'),  # Environment count per AWS account
    ('evs', 'L-96A49955'),  # Host count per EVS environment
    # firehose (1)
    ('firehose', 'L-14BB0BE7'),  # Delivery streams
    # gameliftstreams (2)
    ('gameliftstreams', 'L-C9680889'),  # Applications
    ('gameliftstreams', 'L-E84C6A80'),  # Stream groups
    # kinesis (1)
    ('kinesis', 'L-0918CF54'),  # Shards per Region
    # kms (2)
    ('kms', 'L-C2F1777E'),  # Customer Master Keys (CMKs)
    ('kms', 'L-F33DCFEB'),  # Custom Key Stores
    # lightsail (1)
    ('lightsail', 'L-4259AF9B'),  # Instances
    # neptune-graph (1)
    ('neptune-graph', 'L-D31591F1'),  # Maximum Graphs
    # networkmonitor (1)
    ('networkmonitor', 'L-A4298AB9'),  # Number of monitors per account per AWS region
    # pcs (1)
    ('pcs', 'L-0ADE95E3'),  # Clusters
    # rds (21)
    ('rds', 'L-272F1212'),  # Manual DB instance snapshots
    ('rds', 'L-48C6BF61'),  # DB subnet groups
    ('rds', 'L-5BC124EF'),  # Read replicas per primary
    ('rds', 'L-6F3ACC36'),  # Subnets per DB subnet group
    ('rds', 'L-732153D0'),  # Security groups
    ('rds', 'L-75AC651F'),  # DB shard groups
    ('rds', 'L-78E853F4'),  # Reserved DB instances
    ('rds', 'L-7ADDB58A'),  # Total storage for all DB instances
    ('rds', 'L-7B6409FD'),  # DB instances
    ('rds', 'L-9372BAB3'),  # Custom endpoints per DB cluster
    ('rds', 'L-952B80B8'),  # DB clusters
    ('rds', 'L-9B510759'),  # Manual DB cluster snapshots
    ('rds', 'L-9FA33840'),  # Option groups
    ('rds', 'L-A399AC0B'),  # Custom engine versions
    ('rds', 'L-AA8B1026'),  # Authorizations per DB security group
    ('rds', 'L-CB9BE6F8'),  # Integrations
    ('rds', 'L-D94C7EA3'),  # Proxies
    ('rds', 'L-DD2301CA'),  # IAM roles per DB instance
    ('rds', 'L-DE55804A'),  # Parameter groups
    ('rds', 'L-E094F43D'),  # IAM roles per DB cluster
    ('rds', 'L-E4C808A8'),  # DB cluster parameter groups
    # resource-groups (1)
    ('resource-groups', 'L-2BAA18A0'),  # Resource groups per account
    # robomaker (2)
    ('robomaker', 'L-D6554FB1'),  # Simulation applications
    ('robomaker', 'L-E5D0EA7D'),  # Robot applications
    # sagemaker (16)
    ('sagemaker', 'L-04CE2E67'),  # Total number of notebook instances
    ('sagemaker', 'L-3036C9CA'),  # Maximum number of A2I human task UIs
    ('sagemaker', 'L-5CED4195'),  # Maximum number of SageMaker Projects allowed per account
    ('sagemaker', 'L-6BC1B1A9'),  # Maximum number of MLflow Tracking Servers
    ('sagemaker', 'L-73C1B556'),  # Maximum number of A2I flow definitions
    ('sagemaker', 'L-7A3DF611'),  # Number of instances across active endpoints
    ('sagemaker', 'L-8E5333B4'),  # Maximum number of Studio spaces allowed per account
    ('sagemaker', 'L-9966108C'),  # Total Monitoring Schedules
    ('sagemaker', 'L-9A82FBCA'),  # Maximum number of SageMaker Model Package allowed per a...
    ('sagemaker', 'L-A0C828DC'),  # Total number of experiments allowed, excluding those au...
    ('sagemaker', 'L-AC46C40F'),  # Maximum number of Studio user profiles allowed per account
    ('sagemaker', 'L-B683BCB0'),  # Total domains
    ('sagemaker', 'L-BC8DC54C'),  # Maximum number of SageMaker Model Package Groups allowe...
    ('sagemaker', 'L-DDDC1D15'),  # Maximum number of SageMakerImage images allowed per acc...
    ('sagemaker', 'L-E1A153C2'),  # Total number of trials allowed in a single experiment, ...
    ('sagemaker', 'L-E8EADE50'),  # Maximum number of pipelines allowed per account
    # ses (2)
    ('ses', 'L-10E24536'),  # Configuration set count
    ('ses', 'L-E7F21B4C'),  # Tenant count
    # sns (3)
    ('sns', 'L-1A43D3DB'),  # Pending Subscriptions per Account
    ('sns', 'L-4126E74A'),  # Filter Policies per Account
    ('sns', 'L-61103206'),  # Topics per Account
    # social-messaging (1)
    ('social-messaging', 'L-8479D5F2'),  # WhatsApp Business Accounts per account
    # ssm (7)
    ('ssm', 'L-01B74EDA'),  # Concurrent State Manager associations per region
    ('ssm', 'L-218CDBD4'),  # Patch baselines
    ('ssm', 'L-527D1CD8'),  # Advanced parameters
    ('ssm', 'L-60D2045D'),  # Systems Manager SSM documents
    ('ssm', 'L-7727CE5B'),  # Maintenance Windows
    ('ssm', 'L-C3B871CB'),  # Standard parameters
    ('ssm', 'L-E7B4BBE8'),  # Systems Manager document public shares
    # ssm-sap (1)
    ('ssm-sap', 'L-C8103580'),  # SAP applications per Region in account
    # states (2)
    ('states', 'L-A9562A73'),  # Registered activities
    ('states', 'L-B66B0F91'),  # Registered state machines
    # thinclient (1)
    ('thinclient', 'L-64C2BDF4'),  # Number of Environments
    # timestream (3)
    ('timestream', 'L-1222731D'),  # Tables per account
    ('timestream', 'L-F1AC16A2'),  # Scheduled queries per account
    ('timestream', 'L-FD5A0C1A'),  # Databases per account
    # vpc (4)
    ('vpc', 'L-29B6F2EB'),  # Interface VPC endpoints per VPC
    ('vpc', 'L-83CA0A9D'),  # IPv4 CIDR blocks per VPC
    ('vpc', 'L-93826ACB'),  # Routes per route table
    ('vpc', 'L-F678F1CE'),  # VPCs per Region
    # wafv2 (4)
    ('wafv2', 'L-2EC3DE7B'),  # Maximum web ACLs per account in WAF for regional
    ('wafv2', 'L-BF0029B0'),  # Maximum regex pattern sets per account in WAF for regional
    ('wafv2', 'L-C5BCD850'),  # Maximum rule groups per account in WAF for regional
    ('wafv2', 'L-D6DA96AE'),  # Maximum IP sets per account in WAF for regional
    # workspaces (6)
    ('workspaces', 'L-0798A2C9'),  # Connection aliases
    ('workspaces', 'L-0E312A12'),  # IP access control groups
    ('workspaces', 'L-18CE281C'),  # Images
    ('workspaces', 'L-34278094'),  # WorkSpaces
    ('workspaces', 'L-843E43DA'),  # Bundles
    ('workspaces', 'L-EEB759DE'),  # Directories
    # workspaces-instances (1)
    ('workspaces-instances', 'L-7D173EC3'),  # WorkSpaces Managed Instances
    # workspaces-web (11)
    ('workspaces-web', 'L-122C6700'),  # Number of DataProtectionSettings
    ('workspaces-web', 'L-149BA3AD'),  # Number of Portals
    ('workspaces-web', 'L-21C7999E'),  # Number of SessionLoggers
    ('workspaces-web', 'L-36965BD1'),  # Number of BrowserSettings
    ('workspaces-web', 'L-3A62D5A9'),  # Number of UserSettings
    ('workspaces-web', 'L-3A76276F'),  # Number of TrustStores
    ('workspaces-web', 'L-787608AB'),  # Number of NetworkSettings
    ('workspaces-web', 'L-78A0B046'),  # Number of IpAccessSettings
    ('workspaces-web', 'L-8BD59015'),  # Number of UserAccessLoggingSettings
    ('workspaces-web', 'L-B30615E2'),  # Number of Certificates per TrustStore
    ('workspaces-web', 'L-DFC864EF'),  # Number of IdentityProviders per Portal
})


def _catalog():
    with open(CATALOG, encoding='utf-8') as handle:
        return json.load(handle)


def overlap():
    implemented = {(service.lower(), code) for service, code in custom_keys()}
    return {(quota['ServiceCode'], quota['QuotaCode']) for quota in _catalog()
            if compatible(quota)
            and (quota['ServiceCode'].lower(), quota['QuotaCode']) in implemented}


def test_no_unlisted_check_is_registered_for_a_quota_with_an_official_metric():
    """A new overlap is a decision, not an accident: list it or drop the check."""
    unlisted = sorted(overlap() - OVERLAP)
    assert not unlisted, (
        'these quotas gained a custom check that the collector will skip '
        f'wherever the metric is published: {unlisted[:8]}')


def test_every_listed_overlap_is_still_one():
    """The census may only shrink; a stale entry hides a check that has gone."""
    stale = sorted(OVERLAP - overlap())
    assert not stale, f'no longer both measured and published: {stale[:8]}'


@pytest.mark.parametrize('key', sorted(OVERLAP), ids=lambda value: '/'.join(value))
def test_each_listed_overlap_names_a_quota_the_catalog_still_has(key):
    """A census entry that names nothing in the catalog would never be checked."""
    catalog = {(quota['ServiceCode'], quota['QuotaCode']) for quota in _catalog()}
    assert key in catalog
