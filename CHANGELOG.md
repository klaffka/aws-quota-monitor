# Changelog

All notable changes to this project are recorded here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- MediaConvert queue concurrency, reserved transcode slot and custom preset
  measurements, and Transfer Family certificate, SSH key and directory access
  measurements.

### Changed

- Quotas stating a clock in hours, minutes or seconds, or an allowance per
  twenty-four hours, are no longer ranked as countable inventory work.

### Added

- A project logo, and a README header carrying the coverage figure, with a test
  that fails when either the badge or the gap-shape table drifts from the catalog.
- Service Catalog delegated administrator measurement, and an
  `organization-wide` gap shape so quotas counted across every member account
  stop being ranked as the measurement work to do next.
- SageMaker ml.p3 training, spot training, warm pool and processing instance
  measurements, for the quotas AWS publishes no usage metric for.
- IoT security profile behaviour value, job target, fleet index filter, command
  parameter and command execution concurrency measurements.
- Bedrock Data Automation blueprints per project and modality, agent
  collaborator, action group parameter and Advanced Prompt Optimization job
  measurements.
- A `no SDK client` gap shape, so services AWS no longer ships a client for stop
  being ranked as the measurement work to do next.
- IoT job, security profile, stream, audit, endpoint, rule and thing group
  measurements.
- Comprehend job, flywheel and inference unit measurements, and Lambda capacity
  provider, MicroVM image and VPC interface measurements.
- Deadline Cloud association and License Manager grant, token and entitlement measurements.
- MediaLive inventory and FSx capacity, IOPS, cache and backup measurements.
- Forecast parallel task and dataset group measurements.
- Data Exchange revision, asset, job and data grant measurements.
- API Gateway key, certificate, domain, usage plan, VPC link, route and stage
  measurements, and a --update-progress flag that keeps the audit figures current.
- Transcribe concurrent job, pending vocabulary and Call Analytics measurements.
- Lightsail storage, certificate, container service and distribution measurements.
- CodeBuild concurrent build, project tag, VPC and timeout measurements.
- Deeper AppSync, CodePipeline, CodeDeploy and Resilience Hub measurements
  beyond their top-level inventories.
- Support permit measurements.
- Connect agent status, data table value and queue email address measurements,
  and Pinpoint import job, event campaign and journey activity measurements.
- IVS stage, composition, public key, stream key and playback measurements.
- Storage Gateway tape, volume, cache and upload buffer capacity measurements.
- Application Migration Service server, wave, job and action measurements.
- HealthOmics run, task, store, share and import job measurements.
- Resilience Hub V2 service, system, policy, journey and input source
  measurements, read through the second-generation client.
- Redshift event subscription, reserved node, subnet group and snapshot
  restore-access measurements.
- WAFv2 capacity unit, token domain, rate-based statement, custom body and
  custom header measurements, read from the full web ACL and rule group.
- Service Catalog portfolio, product, TagOption and AppRegistry measurements.
- CodeDeploy running-deployment instance, traffic route listener and GitHub
  token measurements, and the AgentCore generated-policy rolling window.
- Keyspaces user-defined type measurements in both reference directions.
- WAF Classic inventory and condition-depth measurements: rules, rate-based
  rules, geo match sets, the filters of every match condition type, and logging
  destinations per web ACL.
- EC2 transit gateway multicast domain, group, interface and association
  measurements, Direct Connect and VPC attachment counts from both ends, and
  Verified Access endpoint and FPGA image counts.
- Capacity block measurements for the P5, P5e, P5en, P6 and Trainium families,
  and Client VPN session and route measurements per endpoint.
- A fourth unmeasurable rule that reads the period AWS states for a quota, and
  wording rules for the `Rate of`, `Request rate for` and named token bucket
  forms, so 1,671 uncovered rate quotas leave the measurable denominator.
- MWAA Serverless, Migration Hub Strategy, Security Agent, Snow Device
  Management, Compute Optimizer automation, DevOps agent, observability
  centralization, organizational unit and S3 on Outposts measurements.
- Complete Snow Family and VM Import/Export coverage.
- Migration Hub Orchestrator, Connect outbound campaign, Linux subscription,
  EC2 fast launch, AppFlow and Inspector Classic measurements.
- QuickSight approval policy and Greengrass V2 component measurements.
- Complete Service Quotas request, Auto Scaling plan, Shield protection,
  Translate, CloudWatch RUM and CodeCommit coverage.
- Complete DAX and License Manager user subscription coverage, and Textract
  in-progress adapter version measurements.
- AWS RTB Fabric gateway, link and routing measurements.
- Complete Telco Network Builder and Interconnect coverage.
- Amazon Chime SDK identity, messaging, voice and media pipeline measurements.
- Complete Elastic Disaster Recovery and EventBridge Schemas coverage, and
  Launch Wizard deployment measurements.
- Amazon Connect Customer Profiles domain, object type and recommender measurements.
- VPC IP Address Manager resource measurements.
- Amazon EBS volume, snapshot, archive and fast-snapshot-restore measurements.
- Amazon SQS queue configuration, policy and tag measurements.
- Coverage reported against both the full catalog and the measurable base,
  excluding token-bucket, per-second rate and burst quotas by documented rule.
- Coverage measured against the union of several quota exports, a
  `data/coverage-baseline.json` regression gate in CI, and `quota_orphans.py`
  for implemented quota codes that no export contains.
- Lex V2 build-time configuration coverage for intents, slots, composite
  subslots, custom slot types, values and synonyms, and UTF-16 utterance lengths.
- Broad AWS quota coverage through official CloudWatch usage metrics and paginated resource inventories.
- Offline quota coverage and package verification tools.
- Automated Python, packaging, and Terraform checks for pull requests and branches.
- Tag-driven GitHub releases with validated versions, release notes, and SHA-256 checksums.
- FinSpace Managed kdb measurements for 28 resource, node, and storage quotas.
- EC2 Image Builder measurements for 20 resource and configuration quotas.
- AWS Network Firewall measurements for 25 resource, policy, rule-group, TLS,
  VPC-endpoint, and container quotas.
- Network Access Analyzer and Reachability Analyzer measurements for all six
  quotas in the retained Network Insights catalog.
- Unique Audit Manager accounts in scope across all assessments.
- DLM target accounts per snapshot sharing rule.
- Recycle Bin tag key/value pairs per retention rule.
- AWS RAM resource/principal associations per share and customer-managed
  permissions at account and resource-type scope.
- Complete App Runner resource coverage for connections, configuration names,
  VPC connectors, and VPC ingress connections per service.
- Complete Application Auto Scaling coverage for scheduled actions and scaling
  policies per target plus step adjustments per step policy.
- Complete AWS Proton coverage for combined templates, components, environment-account
  connections, template versions, and service instances at their documented scopes.
- Complete Route 53 Profiles coverage for owned profiles and VPC, private-hosted-zone,
  and VPC-endpoint associations per profile.
- Route 53 Resolver measurements for DNS Firewall groups per VPC, rules per group,
  and Resolver-rule and Firewall-group associations per Route 53 Profile.
- Complete Migration Hub Refactor Spaces coverage for owned environments,
  applications, services, and routes across visible multi-account hierarchies.
- Maximum configured inference units per running Rekognition Custom Labels model.
- Registered the existing OpenSearch domain and UI-application inventories for
  offline coverage reporting and validated application identities and states.
- Complete current MediaConnect catalog coverage for outputs per flow and regional
  Router inputs, outputs, and network interfaces.
- Complete AWS Outposts coverage for regional sites and the maximum number of
  Outposts per site.
- Regional AWS Payment Cryptography alias counts.
- Complete resource-quota coverage for Private CA Connector for Active Directory:
  connectors, templates per connector, and group access-control entries per template.
- Complete resource-quota coverage for Private CA Connector for SCEP: connectors
  and challenges per connector.
- Amazon Personalize measurements for active filters, pending batch inference jobs,
  pending solution versions and pending data deletion jobs, with corrected campaign,
  solution and recommender scopes per dataset group.
- Complete VPC Lattice resource-quota coverage across regional inventories and every
  documented parent scope; register the existing WorkSpaces Thin Client inventory for
  offline coverage reporting.
- Complete AWS KMS resource-quota coverage, including completed and in-progress
  on-demand rotations per eligible customer-managed key.

### Changed

- Quota collection, alerting, reporting, and deployment behavior now use explicit failure and data-quality states.

### Fixed

- The shared call cache rejected datetime arguments, which the APIs that take a
  time window need.
- Pinpoint listings sent the page token as `NextToken`, which those APIs reject,
  and called the nonexistent `GetJourneys`; projects were also read unpaginated.
- The Application Migration Service application count called the nonexistent
  `DescribeApplications`.
- Paginated calls stopped after the first page whenever an API returns
  `NextPageToken` and takes it back as `PageToken`, as Service Catalog does.
- The Keyspaces checks addressed a `cassandra` client that botocore does not
  ship and listed tables without the keyspace those listings require, so both
  quotas always failed.
- EFS and EMR addressed their Service Quotas service codes as SDK clients, so
  every check in both modules errored; a test now proves each check module only
  names clients botocore ships. The retired Evidently, IoT Analytics, IoT
  Events, QLDB and RoboMaker clients report as unsupported through one shared
  helper instead of failing the run.
- Internet Monitor called a `ListMonitoredResources` operation the SDK has
  never had; a monitor's resources come from `GetMonitor`. A second test now
  proves every operation a check names exists on its client.
- Twelve listings read a response key the API does not return, so Backup report
  plans and plan versions, Cloud9 environments, EVS environments and hosts,
  GameLift matchmaking configurations, GuardDuty detectors, MediaPackage v2
  channel groups, Timestream InfluxDB instances and Voice ID domains all
  reported zero usage with an OK status. A third test proves every paginated
  key exists in its operation's response.
- 60 IAM actions in the collector policy named SDK client names rather than
  service prefixes (`voice-id` for `voiceid`, `amp` for `aps`, `connectcases`
  for `cases` and more), so those calls would have been denied; duplicate
  grants inside a statement are gone and a test checks both.
- Thirteen calls passed parameters their operation does not accept or omitted
  required ones: Access Analyzer archive rules by ARN instead of name, both
  Cognito listings without the required page size, CodeArtifact repositories
  with a `domain` that operation has not, Cloud Map services with a namespace
  instead of a filter, DataZone connections without their domain, EventBridge
  targets as `RuleName`, both FIS detail calls, Glue user-defined functions
  without a pattern, IoT dynamic groups through a filter `ListThingGroups` has
  not, and SWF activity types and open executions. A fourth call-site test now
  checks every parameter name against the operation.
- The IoT Events checks now report the missing SDK client as unsupported instead
  of failing with an unknown-service error.
- Deadline Cloud worker and job counts called ListWorkers and ListJobs with a
  farm alone, though they take a fleet and a queue; both now sum their children.
- Corrected the OpenSearch UI `ListApplications` IAM service prefix to `es`.
- Corrected four truncated quota codes in the Backup, GameLift, Ground Station
  and IoT Core checks, which matched no catalog entry and were therefore never
  reported.
- Invoke the Network Insights and WAF Regional checks from the collector; both
  were registered for reporting but never ran.
- Corrected the nonexistent KMS `ListCustomKeyStores` call and IAM action to
  `DescribeCustomKeyStores`; reject incomplete or inconsistent KMS inventories.
- Historical quota measurements and monthly reports preserve account, Region, unit, and interval boundaries.
- Corrected the Network Firewall stateless-rule-group quota code.
- Corrected Recycle Bin rule collection to query every supported resource type.
