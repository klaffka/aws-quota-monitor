import json
import logging
import os
import sys
from pathlib import Path
from datetime import timedelta

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.qmchecks.ec2.ec2 import get_current_quotastatus_ec2
from modules.qmchecks.ebs import get_current_quotastatus_ebs
from modules.qmchecks.ec2_ipam import get_current_quotastatus_ec2_ipam
from modules.qmchecks.customer_profiles import get_current_quotastatus_customer_profiles
from modules.qmchecks.chime import get_current_quotastatus_chime
from modules.qmchecks.interconnect import get_current_quotastatus_interconnect
from modules.qmchecks.rtbfabric import get_current_quotastatus_rtbfabric
from modules.qmchecks.tnb import get_current_quotastatus_tnb
from modules.qmchecks.drs import get_current_quotastatus_drs
from modules.qmchecks.schemas import get_current_quotastatus_schemas
from modules.qmchecks.launchwizard import get_current_quotastatus_launchwizard
from modules.qmchecks.vpc.vpc import get_current_quotastatus_vpc
from modules.qmchecks.lambda_checks.lambda_checks import get_current_quotastatus_lambda
from modules.qmchecks.account_services import get_current_quotastatus_account_services
from modules.qmchecks.elb import get_current_quotastatus_elb
from modules.qmchecks.stepfunctions import get_current_quotastatus_stepfunctions
from modules.qmchecks.ecr import get_current_quotastatus_ecr
from modules.qmchecks.autoscaling import get_current_quotastatus_autoscaling
from modules.qmchecks.apigateway import get_current_quotastatus_apigateway
from modules.qmchecks.ecs import get_current_quotastatus_ecs
from modules.qmchecks.firehose import get_current_quotastatus_firehose
from modules.qmchecks.eventbridge import get_current_quotastatus_eventbridge
from modules.qmchecks.cloudtrail import get_current_quotastatus_cloudtrail
from modules.qmchecks.sns import get_current_quotastatus_sns
from modules.qmchecks.sqs import get_current_quotastatus_sqs
from modules.qmchecks.secretsmanager import get_current_quotastatus_secretsmanager
from modules.qmchecks.access_analyzer import get_current_quotastatus_access_analyzer
from modules.qmchecks.guardduty import get_current_quotastatus_guardduty
from modules.qmchecks.securityhub import get_current_quotastatus_securityhub
from modules.qmchecks.transfer import get_current_quotastatus_transfer
from modules.qmchecks.macie import get_current_quotastatus_macie
from modules.qmchecks.inspector import get_current_quotastatus_inspector
from modules.qmchecks.efs import get_current_quotastatus_efs
from modules.qmchecks.fsx import get_current_quotastatus_fsx
from modules.qmchecks.lakeformation import get_current_quotastatus_lakeformation
from modules.qmchecks.xray import get_current_quotastatus_xray
from modules.qmchecks.appmesh import get_current_quotastatus_appmesh
from modules.qmchecks.redshift import get_current_quotastatus_redshift
from modules.qmchecks.timestream import get_current_quotastatus_timestream
from modules.qmchecks.rds_resources import get_current_quotastatus_rds_resources
from modules.qmchecks.transcribe import get_current_quotastatus_transcribe
from modules.qmchecks.polly import get_current_quotastatus_polly
from modules.qmchecks.lex import get_current_quotastatus_lex
from modules.qmchecks.network_firewall import get_current_quotastatus_network_firewall
from modules.qmchecks.networkinsights import get_current_quotastatus_networkinsights
from modules.qmchecks.ses import get_current_quotastatus_ses
from modules.qmchecks.connect import get_current_quotastatus_connect
from modules.qmchecks.auditmanager import get_current_quotastatus_auditmanager
from modules.qmchecks.resiliencehub import get_current_quotastatus_resiliencehub
from modules.qmchecks.storagegateway import get_current_quotastatus_storagegateway
from modules.qmchecks.omics import get_current_quotastatus_omics
from modules.qmchecks.iotfleetwise import get_current_quotastatus_iotfleetwise
from modules.qmchecks.iotcore import get_current_quotastatus_iotcore
from modules.qmchecks.forecast import get_current_quotastatus_forecast
from modules.qmchecks.pinpoint import get_current_quotastatus_pinpoint
from modules.qmchecks.deadline import get_current_quotastatus_deadline
from modules.qmchecks.scheduler import get_current_quotastatus_scheduler
from modules.qmchecks.resource_groups import get_current_quotastatus_resource_groups
from modules.qmchecks.cloudformation import get_current_quotastatus_cloudformation
from modules.qmchecks.cloudwatchpredictions import get_current_quotastatus_cloudwatchpredictions
from modules.qmchecks.application_autoscaling import get_current_quotastatus_application_autoscaling
from modules.qmchecks.kms import get_current_quotastatus_kms
from modules.qmchecks.ssm import get_current_quotastatus_ssm
from modules.qmchecks.misc_counts import get_current_quotastatus_misc
from modules.qmchecks.route53resolver import get_current_quotastatus_route53resolver
from modules.qmchecks.mq import get_current_quotastatus_mq
from modules.qmchecks.directoryservice import get_current_quotastatus_directoryservice
from modules.qmchecks.opensearch import get_current_quotastatus_opensearch
from modules.qmchecks.outposts import get_current_quotastatus_outposts
from modules.qmchecks.elasticbeanstalk import get_current_quotastatus_elasticbeanstalk
from modules.qmchecks.batch import get_current_quotastatus_batch
from modules.qmchecks.s3 import get_current_quotastatus_s3
from modules.qmchecks.codeguruprofiler import get_current_quotastatus_codeguruprofiler
from modules.qmchecks.memorydb import get_current_quotastatus_memorydb
from modules.qmchecks.personalize import get_current_quotastatus_personalize
from modules.qmchecks.sagemaker_resources import get_current_quotastatus_sagemaker_resources
from modules.qmchecks.mediaconvert import get_current_quotastatus_mediaconvert
from modules.qmchecks.ivs import get_current_quotastatus_ivs
from modules.qmchecks.specialized import get_current_quotastatus_specialized
from modules.qmchecks.workspaces_web import get_current_quotastatus_workspaces_web
from modules.qmchecks.streaming import get_current_quotastatus_streaming
from modules.qmchecks.media_extra import get_current_quotastatus_media_extra
from modules.qmchecks.management_counts import get_current_quotastatus_management_counts
from modules.qmchecks.rest_counts import get_current_quotastatus_rest_counts
from modules.qmchecks.new_services import get_current_quotastatus_new_services
from modules.qmchecks.appconfig import get_current_quotastatus_appconfig
from modules.qmchecks.servicecatalog import get_current_quotastatus_servicecatalog
from modules.qmchecks.wafv2 import get_current_quotastatus_wafv2
from modules.qmchecks.waf_regional import get_current_quotastatus_waf_regional
from modules.qmchecks.acm import get_current_quotastatus_acm
from modules.qmchecks.cognito import get_current_quotastatus_cognito
from modules.qmchecks.backup import get_current_quotastatus_backup
from modules.qmchecks.glue import get_current_quotastatus_glue
from modules.qmchecks.emr import get_current_quotastatus_emr
from modules.qmchecks.datasync import get_current_quotastatus_datasync
from modules.qmchecks.codebuild import get_current_quotastatus_codebuild
from modules.qmchecks.codepipeline import get_current_quotastatus_codepipeline
from modules.qmchecks.codeartifact import get_current_quotastatus_codeartifact
from modules.qmchecks.logs import get_current_quotastatus_logs
from modules.qmchecks.dynamodb import get_current_quotastatus_dynamodb
from modules.qmchecks.elasticache import get_current_quotastatus_elasticache
from modules.qmchecks.docdb import get_current_quotastatus_docdb
from modules.qmchecks.neptune import get_current_quotastatus_neptune
from modules.qmchecks.bedrock import get_current_quotastatus_bedrock
from modules.qmchecks.cleanrooms_ml import get_current_quotastatus_cleanrooms_ml
from modules.qmchecks.appstream import get_current_quotastatus_appstream
from modules.qmchecks.bedrock_agentcore import get_current_quotastatus_bedrock_agentcore
from modules.qmchecks.rekognition import get_current_quotastatus_rekognition
from modules.qmchecks.comprehend import get_current_quotastatus_comprehend
from modules.qmchecks.textract import get_current_quotastatus_textract
from modules.qmchecks.directconnect import get_current_quotastatus_directconnect
from modules.qmchecks.iot import get_current_quotastatus_iot
from modules.qmchecks.appsync import get_current_quotastatus_appsync
from modules.qmchecks.config_service import get_current_quotastatus_config
from modules.qmchecks.dms_resources import get_current_quotastatus_dms_resources
from modules.qmchecks.mgn import get_current_quotastatus_mgn
from modules.qmchecks.groundstation import get_current_quotastatus_groundstation
from modules.qmchecks.sitewise import get_current_quotastatus_sitewise
from modules.qmchecks.twinmaker import get_current_quotastatus_twinmaker
from modules.qmchecks.robomaker import get_current_quotastatus_robomaker
from modules.qmchecks.workspaces import get_current_quotastatus_workspaces
from modules.qmchecks.finspace import get_current_quotastatus_finspace
from modules.qmchecks.m2 import get_current_quotastatus_m2
from modules.qmchecks.entityresolution import get_current_quotastatus_entityresolution
from modules.qmchecks.datazone import get_current_quotastatus_datazone
from modules.qmchecks.apprunner import get_current_quotastatus_apprunner
from modules.qmchecks.amplify import get_current_quotastatus_amplify
from modules.qmchecks.cases import get_current_quotastatus_cases
from modules.qmchecks.airflow import get_current_quotastatus_airflow
from modules.qmchecks.amplifyuibuilder import get_current_quotastatus_amplifyuibuilder
from modules.qmchecks.evs import get_current_quotastatus_evs
from modules.qmchecks.lightsail import get_current_quotastatus_lightsail
from modules.qmchecks.mediastore import get_current_quotastatus_mediastore
from modules.qmchecks.mediatailor import get_current_quotastatus_mediatailor
from modules.qmchecks.kinesisvideo import get_current_quotastatus_kinesisvideo
from modules.qmchecks.eks import get_current_quotastatus_eks
from modules.qmchecks.codedeploy import get_current_quotastatus_codedeploy
from modules.qmchecks.cassandra import get_current_quotastatus_cassandra
from modules.qmchecks.qldb import get_current_quotastatus_qldb
from modules.qmchecks.cloud9 import get_current_quotastatus_cloud9
from modules.qmchecks.resource_explorer import get_current_quotastatus_resource_explorer
from modules.qmchecks.neptune_graph import get_current_quotastatus_neptune_graph
from modules.qmchecks.location import get_current_quotastatus_location
from modules.qmchecks.appintegrations import get_current_quotastatus_appintegrations
from modules.qmchecks.iotevents import get_current_quotastatus_iotevents
from modules.qmchecks.iotanalytics import get_current_quotastatus_iotanalytics
from modules.qmchecks.pcs import get_current_quotastatus_pcs
from modules.qmchecks.grafana import get_current_quotastatus_grafana
from modules.qmchecks.oam import get_current_quotastatus_oam
from modules.qmchecks.networkmonitor import get_current_quotastatus_networkmonitor
from modules.qmchecks.gameliftstreams import get_current_quotastatus_gameliftstreams
from modules.qmchecks.gamelift import get_current_quotastatus_gamelift
from modules.qmchecks.dsql import get_current_quotastatus_dsql
from modules.qmchecks.payment_cryptography import get_current_quotastatus_payment_cryptography
from modules.qmchecks.pca_connector_ad import get_current_quotastatus_pca_connector_ad
from modules.qmchecks.pca_connector_scep import get_current_quotastatus_pca_connector_scep
from modules.qmchecks.serverlessrepo import get_current_quotastatus_serverlessrepo
from modules.qmchecks.swf import get_current_quotastatus_swf
from modules.qmchecks.cloudhsm import get_current_quotastatus_cloudhsm
from modules.qmchecks.kafka import get_current_quotastatus_kafka
from modules.qmchecks.proton import get_current_quotastatus_proton
from modules.qmchecks.imagebuilder import get_current_quotastatus_imagebuilder
from modules.qmchecks.fms import get_current_quotastatus_fms
from modules.qmchecks.kafkaconnect import get_current_quotastatus_kafkaconnect
from modules.qmchecks.rolesanywhere import get_current_quotastatus_rolesanywhere
from modules.qmchecks.internetmonitor import get_current_quotastatus_internetmonitor
from modules.qmchecks.kinesisanalytics import get_current_quotastatus_kinesisanalytics
from modules.qmchecks.kinesis_resources import get_current_quotastatus_kinesis_resources
from modules.qmchecks.license_manager import get_current_quotastatus_license_manager
from modules.qmchecks.route53profiles import get_current_quotastatus_route53profiles
from modules.qmchecks.refactor_spaces import get_current_quotastatus_refactor_spaces
from modules.qmchecks.docdb_elastic import get_current_quotastatus_docdb_elastic
from modules.qmchecks.databrew import get_current_quotastatus_databrew
from modules.qmchecks.cognito_identity import get_current_quotastatus_cognito_identity
from modules.qmchecks.wellarchitected import get_current_quotastatus_wellarchitected
from modules.qmchecks.ssm_contacts import get_current_quotastatus_ssm_contacts
from modules.qmchecks.dataexchange import get_current_quotastatus_dataexchange
from modules.qmchecks.rbin import get_current_quotastatus_rbin
from modules.qmchecks.discovery import get_current_quotastatus_discovery
from modules.qmchecks.ssm_incidents import get_current_quotastatus_ssm_incidents
from modules.qmchecks.workspaces_instances import get_current_quotastatus_workspaces_instances
from modules.qmchecks.repostspace import get_current_quotastatus_repostspace
from modules.qmchecks.evidently import get_current_quotastatus_evidently
from modules.qmchecks.applicationsignals import get_current_quotastatus_applicationsignals
from modules.qmchecks.ram import get_current_quotastatus_ram
from modules.qmchecks.fis import get_current_quotastatus_fis
from modules.qmchecks.aoss import get_current_quotastatus_aoss
from modules.qmcore.aws import CheckContext, session_from_env
from modules.qmcore.catalog import account_catalog, get_catalog
from modules.qmcore.coverage import build_coverage
from modules.qmcore.metrics import compatible, fetch_metrics
from modules.qmcore.model import iso
from modules.qmalerting.alerting import QuotaAlert
from modules.qmdb.db import QuotaLogDb

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    session = session_from_env()
    db = QuotaLogDb(session)
    alerts = QuotaAlert(session, threshold_pct=os.getenv('QM_ALERT_THRESHOLD', '80'), db=db)
    ctx = CheckContext(session)
    errors = []
    try:
        quotas, catalog_errors = get_catalog(ctx, db)
        errors.extend(catalog_errors)
    except Exception as exc:
        quotas = []
        errors.append(f'catalog: {exc}')
    # Never transition alert state from a partial or missing catalog. A
    # partial snapshot can otherwise look like a valid low-usage observation
    # and emit a false recovery for quotas omitted by the failed refresh.
    catalog_usable = bool(quotas) and not catalog_errors if 'catalog_errors' in locals() else False
    if not catalog_usable:
        errors.append('catalog: empty or incomplete quota catalog')
    ctx.quotas = {(q['ServiceCode'], q['QuotaCode']): q for q in account_catalog(quotas)}
    official = {(q['ServiceCode'], q['QuotaCode']) for q in quotas if compatible(q)}
    entries = []
    for collector in (get_current_quotastatus_ec2, get_current_quotastatus_vpc,
                      get_current_quotastatus_lambda):
        # Each collector isolates checks and inventories through CheckContext.
        entries.extend(collector(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_ebs(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_ec2_ipam(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_customer_profiles(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_chime(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_interconnect(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_rtbfabric(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_tnb(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_drs(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_schemas(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_launchwizard(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_account_services(ctx, skip=official))
    entries.extend(get_current_quotastatus_elb(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_stepfunctions(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_ecr(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_autoscaling(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_apigateway(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_ecs(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_firehose(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_eventbridge(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_cloudtrail(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_sns(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_sqs(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_secretsmanager(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_access_analyzer(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_guardduty(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_securityhub(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_transfer(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_macie(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_inspector(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_efs(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_fsx(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_lakeformation(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_xray(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_appmesh(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_redshift(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_timestream(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_rds_resources(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_transcribe(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_polly(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_lex(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_network_firewall(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_networkinsights(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_ses(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_connect(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_auditmanager(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_resiliencehub(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_storagegateway(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_omics(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_iotfleetwise(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_iotcore(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_forecast(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_pinpoint(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_deadline(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_scheduler(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_resource_groups(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_cloudformation(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_cloudwatchpredictions(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_application_autoscaling(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_kms(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_ssm(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_misc(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_route53resolver(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_mq(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_directoryservice(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_opensearch(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_outposts(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_elasticbeanstalk(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_batch(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_s3(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_codeguruprofiler(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_memorydb(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_personalize(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_sagemaker_resources(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_mediaconvert(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_ivs(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_specialized(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_workspaces_web(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_streaming(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_media_extra(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_management_counts(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_rest_counts(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_new_services(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_appconfig(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_servicecatalog(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_wafv2(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_waf_regional(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_acm(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_cognito(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_backup(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_glue(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_emr(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_datasync(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_codebuild(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_codepipeline(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_codeartifact(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_logs(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_dynamodb(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_elasticache(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_docdb(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_neptune(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_bedrock(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_cleanrooms_ml(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_appstream(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_bedrock_agentcore(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_rekognition(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_comprehend(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_textract(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_directconnect(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_iot(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_appsync(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_config(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_dms_resources(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_mgn(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_groundstation(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_sitewise(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_twinmaker(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_robomaker(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_workspaces(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_finspace(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_m2(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_entityresolution(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_datazone(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_apprunner(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_amplify(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_cases(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_airflow(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_amplifyuibuilder(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_evs(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_lightsail(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_mediastore(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_mediatailor(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_kinesisvideo(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_codedeploy(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_cassandra(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_qldb(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_cloud9(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_resource_explorer(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_neptune_graph(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_location(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_appintegrations(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_iotevents(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_iotanalytics(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_pcs(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_grafana(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_oam(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_networkmonitor(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_gameliftstreams(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_gamelift(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_dsql(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_payment_cryptography(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_pca_connector_ad(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_pca_connector_scep(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_serverlessrepo(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_swf(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_cloudhsm(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_kafka(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_proton(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_imagebuilder(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_fms(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_kafkaconnect(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_rolesanywhere(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_internetmonitor(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_kinesisanalytics(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_kinesis_resources(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_license_manager(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_route53profiles(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_refactor_spaces(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_docdb_elastic(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_databrew(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_cognito_identity(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_wellarchitected(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_ssm_contacts(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_dataexchange(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_rbin(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_discovery(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_ssm_incidents(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_workspaces_instances(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_repostspace(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_evidently(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_applicationsignals(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_ram(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_fis(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_aoss(ctx=ctx, skip=official))
    entries.extend(get_current_quotastatus_eks(ctx=ctx, skip=official))
    # A compatible official metric is the single source of truth for its
    # quota, including quotas that also have a resource-check implementation.
    # Incompatible metrics fall back to that resource check and are not emitted
    # as a second UNSUPPORTED measurement.
    metric_quotas = [q for q in quotas if compatible(q)]
    entries.extend(fetch_metrics(ctx, metric_quotas, ctx.now - timedelta(minutes=20), ctx.now))
    for entry in entries:
        if entry['qualityStatus'] == 'ERROR':
            errors.append(f"{entry['serviceCode']}/{entry['quotaCode']}: {entry['qualityReason']}")
        try:
            db.put_quota_entry(entry)
        except Exception as exc:
            errors.append(f"store:{entry['quotaCode']}: {exc}")
            continue
        if catalog_usable:
            try:
                alerts.check_and_alert(entry)
            except Exception as exc:
                errors.append(f"alert:{entry['quotaCode']}: {exc}")
    coverage = build_coverage(quotas, entries)
    db.put_quota_entry({'PK': f'COVERAGE#{ctx.account}#{ctx.region}', 'SK': f'TS#{iso(ctx.now)}',
                        **coverage, 'ttl': int(ctx.now.timestamp()) + 64 * 86400})
    # Run records also identify failures that occur before a quota is discovered.
    db.put_quota_entry({'PK': f'RUN#{ctx.account}#{ctx.region}', 'SK': f'TS#{iso(ctx.now)}',
                        'qualityStatus': 'ERROR' if errors else 'OK', 'errors': errors,
                        'measurementCount': len(entries), 'ttl': int(ctx.now.timestamp()) + 64 * 86400})
    if errors:
        logger.error('Partial collector run: %s', errors)
        raise RuntimeError(f'Collector incomplete: {len(errors)} errors; successful measurements saved')
    ctx.client('cloudwatch').put_metric_data(Namespace='QuotaMonitor', MetricData=[{
        'MetricName': 'CollectorSuccess', 'Dimensions': [{'Name': 'Account', 'Value': ctx.account},
            {'Name': 'Region', 'Value': ctx.region}], 'Value': 1, 'Unit': 'Count'}])
    return {'statusCode': 200, 'body': json.dumps({'measurements': len(entries)})}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(lambda_handler({}, None), indent=2))
