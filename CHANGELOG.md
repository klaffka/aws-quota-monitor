# Changelog

All notable changes to this project are recorded here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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
