# Quota coverage progress — 2026-09-14

Catalog: `tests/fixtures/quota-catalog-union.json`, the committed union of
`data/service-quotas-20251102T133323Z.json` and
`data/service-quotas-BA-eu-central-1-20260910.json`. The exports themselves are
untracked, so the union is what CI and other contributors can reproduce.
Regenerate it with `quota_coverage.py --write-catalog`.
This is an offline implementation audit, not a live measurement success rate.

Neither export is the whole catalog. `list_service_quotas` returns a different
set with and without `QuotaAppliedAtLevel`, which `catalog.py` passes as `ALL`:
the BA export holds 205 services and omits quotas the account really has, such
as the S3 `Access Points`, `Lifecycle rules` and `Bucket tags` limits that the
older export lists. Coverage is therefore measured against the union of both,
with the single-export figure kept for comparison.

The union column is asserted against the committed catalog by
`test_the_progress_document_reports_the_measured_union_totals`; the single-export
column is measured against an untracked export and is kept for comparison only.

| Measure | Union | BA export only |
| --- | ---: | ---: |
| total | 12,081 | 10,398 |
| implemented | 2,607 | 2,076 |
| compatibleMetric | 2,535 | 2,535 |
| covered | 4,988 | 4,457 |
| uncovered | 7,093 | 5,941 |
| unmeasurable | 5,019 | 3,055 |
| measurable | 7,062 | 7,343 |

Implemented measurement availability: **41.29%** of the whole union, or
**70.63%** of the 7,062 quotas whose usage can be counted at all.

5,019 quotas are excluded from the second denominator by four rules in
`quota_coverage.py`, applied in this order:

| Reason | Quotas | Rule |
| --- | ---: | --- |
| `TOKEN_BUCKET` | 1,648 | `... request bucket maximum capacity` / `... refill rate`, `<Operation> throttle token bucket size`, a name ending in `bucket refill rate`, or any name containing `replenish` |
| `API_RATE` | 3,079 | name contains `TPS` as a word, `per second` or `throttle rate`, is exactly `<Operation> throttle limit`, `<Operation> API throttle limit` or `<Operation> rate`, ends in `rate quota` or `throttle quota`, or starts with `Rate of` / `Request rate for` without naming a longer window |
| `API_BURST` | 166 | name contains `burst`, except EFS `Bursting throughput`, which is a published metric |
| `PERIOD_RATE` | 126 | the catalog states the quota's period as one second |

A bucket's occupancy and a per-second peak are not derivable from one-minute
CloudWatch sums, so these are not a matter of writing further checks. The rules
only ever apply to quotas that are already uncovered: where AWS publishes a
usage metric for a rate quota it counts as covered, which is how all 19 covered
`TPS` quotas and all 25 covered `Rate of ...` quotas are accounted for, and no
custom check measures a per-second rate today. Rates over a longer stated
window, such as `Policy generations per day`, stay in the measurable base, and
`LONGER_WINDOW` keeps a future `Rate of ... per day` there as well: no catalog
entry names one today.

`PERIOD_RATE` is the only rule that does not read the quota's name. AWS
publishes the measurement window in the catalog entry, and a period of one
second says the quota is a request rate however it is worded. The wording rules
run first, so it is left with the 136 per-second quotas whose names give no
sign of being rates at all.

The rules cost nothing to widen and instantly flatter the figure, so both
numbers are always reported together and `compare_baseline` fails when the
exclusion count grows, exactly as it fails on a coverage regression. Raising it
requires the same review as any other change to the number.

`iotwireless` is what surfaced this: all 100 of its quotas are
`TPS limit for <Operation>`, so it read as the largest uncovered service while
being entirely unmeasurable. `throttle rate` was added for the same reason after
`emr-containers` (21 of 21 quotas), `aco-automation` (23 of 24) and
`lookoutmetrics` (30) turned out to name their rate limits that way; the wording
covers 215 quotas across ten services and none of them is covered today. The
`<Operation> throttle limit` form is anchored on purpose: Textract writes
`CreateAdapter throttle limit for max number of adapters per account` for a
quota that really is a resource count, and a loose `throttle limit` rule would
have excluded six countable Textract quotas. `rate quota` rests on the
catalog's own structure rather than on wording: all 89 such quotas pair exactly
with an `<Operation> burst quota` that the burst rule already excludes, so each
pair is the refill rate and the depth of one token bucket.
`test_every_catalog_rate_quota_has_an_excluded_burst_twin` fails if AWS ever
adds a `rate quota` without that twin.

Per-minute quotas stay in the measurable base on purpose: a one-minute
CloudWatch sum is exactly the window they name, so Bedrock's
`requests per minute` and `tokens per minute` quotas are a measurement problem
rather than an impossible one.

Custom and compatible metric counts overlap; covered is their union.
`tests/fixtures/coverage-baseline.json` holds these totals and CI fails on any
regression. Approaching 100% of the measurable base remains open; the section below
records how far the current AWS APIs reach.

## Latest verified changes

- Split the quotas AWS counts over a whole organization out of `countable`.
  EC2 reports capacity blocks twice, per account and per organization, and only
  the first is answerable from one account's credentials; the ten
  organization-wide halves were what made EC2 look like the fifth-largest
  countable holding while its account-scoped twins were already measured. The
  shape covers thirteen quotas across EC2, License Manager and Service Catalog.
  Like `no_sdk_client` it is a shape rather than an exclusion: the quotas are
  measurable, just not by a collector holding one account.
  The exception proves the rule. `Delegated administrators per organization`
  names an organization too, but Organizations answers it directly, so it is
  measured through `ListDelegatedAdministrators` for the Service Catalog
  service principal and never reaches the shape rule — covered quotas are
  classified before the shapes are consulted. An account outside an
  organization reports `NO_DATA` with the reason rather than zero.
  Two License Manager quotas stay in the shape although part of their answer is
  local: `Number of accounts per organization for License Manager` and the
  per-asset-group instance counts would need every member account's inventory,
  and counting only this account's share would report a confident undercount.
- Deepened AWS IoT by 7 catalog quotas. Security profile behaviours are counted
  by the elements in each behaviour's threshold list rather than by the
  behaviours themselves, and a machine-learning behaviour, which carries no
  list, counts as zero. Job targets come from the job detail, because the
  listing omits them. The named shadow and geo location filters turned out not
  to bound a single query after all: they configure the fleet index for the
  whole account and `GetIndexingConfiguration` reports both, whether or not
  indexing is enabled. Commands report their mandatory parameters from the
  command detail, and command execution concurrency is asked for one unfinished
  status at a time, because IoT filters executions server side. `iotcore`
  names the dynamic thing group quota under its own code and now shares the
  existing check.
  Three IoT quotas stay open for reasons of their own. `Maximum number of CA
  certificates with the same subject field` would need the subject parsed out
  of each certificate's PEM, which `DescribeCACertificate` returns but no
  dependency here can read. `Maximum number of policies that can be attached to
  a certificate or Amazon Cognito identity` can be counted for certificates but
  not for Cognito identities, which IoT cannot enumerate, so the maximum could
  silently sit on the half that is invisible. The remaining `iotcore` gap is
  the MQTT broker: unacknowledged publishes, topic aliases, subscriptions per
  connection and shared subscription groups live in the connection rather than
  in an inventory.
- Deepened Amazon Bedrock by 13 catalog quotas. The Data Automation blueprints
  per project are counted per modality: a project names its blueprints by ARN
  alone, so each one's `DOCUMENT`, `IMAGE`, `AUDIO` or `VIDEO` type comes from
  the blueprint detail, and a project holding none still reports zero rather
  than dropping out of the maximum. Agent collaborators and the parameter map
  of each action group function are read per agent, the latter from the action
  group detail because its summary omits the schema. The Advanced Prompt
  Optimization jobs are split into running and retained over one walk of a
  listing that offers no status filter, and an unknown status is reported
  rather than assigned to either side. AWS reissued the knowledge-base quotas
  under a renamed "Managed Knowledge Bases" product: the three affected codes
  share the existing checks instead of walking the same API twice.
- Audited every check's call sites against botocore and fixed what the audit
  found: EFS and EMR addressed their Service Quotas service codes (`elastic‑
  filesystem`, `elasticmapreduce`) as SDK clients, Keyspaces addressed a
  `cassandra` client that does not exist and listed tables without the keyspace
  they require, Internet Monitor called a `ListMonitoredResources` operation the
  SDK has never had, and twelve listings read a response key their operation
  does not return, reporting zero usage with an OK status. Three tests now walk
  every `ctx.call` in `qmchecks`: the service must be a client botocore ships,
  the operation must exist on it, and the paginated key must be a member of the
  response. Evidently, IoT Analytics, IoT Events, QLDB and RoboMaker have no
  client at all any more and report as unsupported through one shared helper.
- Fixed 60 IAM actions that named SDK clients rather than service prefixes
  (`voice-id` for `voiceid`, `amp` for `aps`, `connectcases` for `cases`,
  `servicecatalog-appregistry` for `servicecatalog` and more). Each would have
  been denied at run time. Duplicate grants inside a statement are gone, and a
  test compares every prefix with botocore's signing name, with CloudWatch and
  IAM Identity Center documented as the two exceptions.
- Taught the shared paginator the `PageToken` cursor: an API that returns
  `NextPageToken` and takes it back under a different name silently stopped
  after its first page, which is how every Service Catalog listing behaved.
- Deepened AWS IoT from 7 to 15 catalog quotas and IoT Core from 7 to 15.
  Jobs are filtered server side by status and target selection; security profile
  behaviours come from the profile detail and the profiles per target are
  inverted from the per-profile target listing; files per stream, on-demand
  audits in progress within a bounded seven-day window, and metric dimensions.
  IoT Core gains domain configurations, topic rule destinations, actions per
  rule, resource-specific logging configurations, registration tasks, and the
  attributes, hierarchy depth and direct children of each thing group, where the
  depth comes from the ancestors the group already reports rather than a walk.
  The MQTT protocol quotas stay open: unacknowledged publishes, topic aliases,
  subscriptions per connection and shared subscription groups live in the broker
  rather than in an inventory.
- Fixed the shared call cache, which built its key with `json.dumps` and so
  rejected any datetime argument. Several APIs take a time window; the key only
  has to be stable, not round-trippable.
- Deepened Amazon Comprehend from 1 to 20 catalog quotas: the nine active job
  counts, one per job kind, plus document classifiers and entity recognizers
  still training, flywheels by status, datasets being created and per flywheel
  by type, running flywheel iterations, and inference units per account and per
  endpoint. Comprehend filters every listing server side, so each unfinished
  status is asked for rather than walking a service's whole job history.
- Added Lambda capacity providers and their function versions, network
  connectors, MicroVM images and their versions, and the elastic network
  interfaces Lambda attaches per VPC, which EC2 reports as interfaces of type
  `lambda`. Capacity providers are listed by ARN, which the version listing also
  accepts as its name argument.
- Deepened AWS Deadline Cloud from 9 to 16 catalog quotas and corrected two
  that could never have worked: `ListWorkers` takes a fleet and `ListJobs` takes
  a queue, so both were being called with a farm alone. Each now sums its
  children back up to the farm. Added limits, queue fleet associations and farm
  members per farm, members per fleet and per queue, queue environments per
  queue, and queue limit associations attributed to the queue the farm-wide
  listing names. The step, task and job member quotas stay open because they
  need a walk through every job in every queue, which a render farm makes
  unbounded.
- Deepened AWS License Manager from 2 to 11 catalog quotas: licenses, asset
  groups and asset rulesets, grants and tokens per license, received licenses
  per product, counted and uncounted entitlements split by whether the
  entitlement's unit is a plain count, and configuration associations inverted
  onto the resource they attach to.
- Measured AWS Elemental MediaLive at 20 catalog quotas, a service that had only
  official metrics before: inputs grouped by push type, device, MediaConnect,
  VPC destination and on-premises placement; channels by the codec and
  resolution their input specification names and by whether they carry a CDI
  specification; input security groups, multiplexes, networks, reservations, SDI
  sources and signal maps; both template families; and nodes and channel
  placement groups per cluster. `Pull Inputs` stays open because MediaLive names
  the push direction in its input types but not the pull one.
- Deepened Amazon FSx from 7 to 30 catalog quotas: storage capacity summed per
  file system type and storage class, the per-file-system maxima, throughput and
  IOPS read from each type's own configuration block, the Intelligent-Tiering
  and provisioned read caches, file caches counted through `DescribeFileCaches`
  rather than the file system listing, and backups grouped by file system type.
  The catalog states these limits in GiB, MBps and IOPS, which is what the API
  reports.
- Deepened Amazon Forecast from 12 to 25 catalog quotas: dataset import jobs,
  datasets per dataset group, and the eleven parallel task counts. Forecast
  reports lifecycle statuses as `<VERB>_<STATE>`, so a resource counts as a
  running task while its state is pending or in progress, and a resource without
  a status raises `NoData`.
- Deepened AWS Data Exchange from 2 to 24 catalog quotas: revisions per data
  set and per asset type, assets per revision in the same four flavours, the
  nine concurrent in-progress job counts grouped by job type, data grants in
  total and pending per consumer, and event actions per source data set.
- Deepened API Gateway from 9 to 23 catalog quotas: API keys, client
  certificates, custom domain names and the private ones among them, domain name
  access associations, usage plans, VPC links in both API generations, subnets
  per V2 VPC link, resources and WebSocket routes against the quota they share,
  routes per HTTP API, and stage variables and tags per stage. Usage plans per
  API key inverts the per-plan key listing, which is the only direction the API
  offers.
- `quota_coverage.py --update-progress` now rewrites this document's union
  column and headline percentages, which had gone stale twice while the figures
  moved. The single-export column is still refreshed by hand.
- Deepened Amazon Transcribe from 4 to 21 catalog quotas: the current total
  vocabulary, medical vocabulary and language model codes alongside the retired
  ones they replace, pending vocabularies, and the concurrent transcription,
  medical transcription, Call Analytics and language model training counts.
  Transcribe filters jobs by status server side, so each unfinished status is
  asked for separately rather than listing every job. Call Analytics categories
  and the rules on each are counted from the same listing.
- Deepened Lightsail from 3 to 21 catalog quotas: distributions, load
  balancers, buckets and certificates per Region, active certificates counted as
  the issued ones, block storage disks per instance, the largest disk and the
  attached total, container service nodes, deployment containers, custom
  domains, deployment versions and stored images per service, and the
  alternative domain names, cache behaviours and forwarded cookie, header and
  query string allow lists per distribution.
- Measured CodeBuild's 26 concurrent build quotas from one traversal. Each
  quota names an environment type and a compute size, so the running builds are
  grouped by that pair and every quota reads its own cell. The scan is bounded
  at 1,000 build ids, newest first, which a build cannot outlive given
  CodeBuild's eight-hour maximum timeout; a build still running in the last
  batch scanned raises `NoData` rather than reporting a possibly truncated
  count. Tags, VPC security groups, VPC subnets and the configured build timeout
  come from the project details in the same pass.
- Deepened four services that were only counting their top-level inventory.
  AppSync gained Event APIs per Region, API keys and authentication providers
  per API, functions per pipeline resolver walked through every schema type,
  channel namespaces per Event API and source API associations per merged API.
  CodePipeline gained stages and actions per pipeline, actions per stage, the
  parallel and sequential action counts a stage's run orders imply, active
  executions per pipeline, custom action types and webhooks. CodeDeploy gained
  alarms, Auto Scaling groups and triggers per deployment group, deployment
  groups per ECS service, customer deployment configurations, and concurrent
  deployments per account and per group, asking AWS to filter by status rather
  than listing everything. Resilience Hub gained application components and
  resources on each application's newest version, and concurrent assessments and
  recommendation templates per account and per application.

  `Minimum actions` and `Minimum stages per pipeline` state a floor rather than
  a ceiling, so a usage count means nothing against them and they stay open.
- Added Support permits per account, the last reachable quota in the
  zero-coverage set, and checked every remaining service against the SDK. What
  is left is recorded under `Services with no coverage at all`.
- Reached the end of what the SDK exposes for the remaining zero-coverage
  services. Measured MWAA Serverless workflows, versions per workflow and
  concurrent runs; Migration Hub Strategy active imports and servers per
  assessment; Security Agent concurrent code review, pentest and threat model
  jobs across every agent space; Snow Device Management total and active tasks;
  Compute Optimizer automation events in flight; DevOps agent spaces; the
  organization centralization rules; accounts per organizational unit, walked
  from the organization roots; and S3 on Outposts buckets and access points per
  outpost.
- Completed the AWS Snow Family at 2 of 2 catalog quotas and VM Import/Export at
  2 of 2. Snow devices are counted from the jobs that hold them, excluding jobs
  that are `Complete` or `Cancelled`, and the Edge and Snowcone families are
  separated by device type. The two VM Import/Export quotas cover different
  operation families, so each counts only its own task inventories and only
  tasks that are still `active` or `cancelling`.
- Completed AWS Migration Hub Orchestrator at 3 of 3 catalog quotas (workflows,
  step groups per workflow, steps per step group), License Manager Linux
  subscriptions at 1 of 1, EC2 fast launch at 1 of 1 (the largest configured
  parallel launch count), and Amazon Connect outbound campaigns at 2 of 2. The
  campaign summaries carry no state, so the active count asks
  `GetCampaignStateBatch` in batches of 25 and raises `NoData` when a state
  cannot be read rather than counting the campaign as inactive.
- Measured AppFlow flows and connector profiles, and Inspector Classic
  assessment targets, templates and runs. AppFlow's remaining quotas bound a
  single run or record, are per-connector rates, or count executions that
  `ListFlows` does not expose; `Instances in running assessments` counts the
  instances an Inspector Classic run covers, which the run does not report.
- Measured Amazon QuickSight approval policies at 4 of its 24 measurable catalog
  quotas: policies per account, policies per asset type, and the applicable and
  approver group lists on each policy. The visual, sheet control and calculated
  field quotas live inside an analysis or dashboard definition rather than in an
  inventory, the Quick Automate quotas have no listing operation, and
  `Data Prep: Fields per dataset` counts fields inside a dataset's preparation
  tables, which `DataPrepConfiguration` exposes only as source, transform and
  destination table maps.
- Measured AWS IoT Greengrass at 3 of 17 catalog quotas from the V2 API:
  components in the account's own `PRIVATE` scope, versions per component, and
  core device thing name length. The recipe, artifact and deployment document
  size quotas bound a single document. The five group quotas belong to the V1
  model, whose definition versions are addressed by ARN while the API takes a
  definition id and version id pair, so they stay open rather than being reached
  through ARN parsing. Sources:
  [QuickSight quotas](https://docs.aws.amazon.com/quicksight/latest/user/limits.html),
  [ListApprovalPolicies](https://docs.aws.amazon.com/quicksight/latest/APIReference/API_ListApprovalPolicies.html),
  [Greengrass V2 quotas](https://docs.aws.amazon.com/greengrass/v2/developerguide/quotas.html),
  [ListComponents](https://docs.aws.amazon.com/greengrass/v2/APIReference/API_ListComponents.html).
- Completed six smaller services from their own inventories: Service Quotas at
  2 of 2 (requests still `PENDING` or `CASE_OPENED`, in total and per quota),
  AWS Auto Scaling plans at 3 of 3 (plans, instructions per plan, target
  tracking configurations per instruction), Shield Advanced at 2 of 2 (Elastic
  IP and load balancer protections, split by the protected resource's ARN),
  Amazon Translate at 2 of 2 (custom terminologies and the batch jobs still
  running), CloudWatch RUM at 1 of 1 and CodeCommit at 1 of 1.
- Completed Amazon DynamoDB Accelerator at 5 of 5 catalog quotas (total nodes,
  nodes per cluster from the `TotalNodes` each cluster reports, parameter groups,
  subnet groups and subnets per subnet group) and AWS License Manager user
  subscriptions at 4 of 4 (user-based subscriptions for each of the three
  products and instance associations per user). Product names are compared with
  spacing and casing removed, so `VISUAL_STUDIO_ENTERPRISE` and
  `Visual Studio Enterprise` count towards the same quota.
- Added Textract in-progress adapter versions per account, counting only
  versions still in `CREATION_IN_PROGRESS`.
- Measured AWS RTB Fabric at 5 of 11 measurable catalog quotas: gateways across
  both the requester and responder listings, links and certificate associations
  per gateway, routing rules per link, and flow modules per link from the link
  summaries. The external inbound and outbound link quotas would need the link's
  connectivity and direction mapped onto AWS's external wording, which the API
  does not state in those terms; availability zones per gateway would have to be
  derived from the gateway's subnets through EC2; and the two `supported` quotas
  describe a service capability rather than an inventory.
- Completed AWS Telco Network Builder at 4 of 4 catalog quotas (function
  packages, network packages, network service instances, and the operations
  still `PROCESSING` or `CANCELLING`) and AWS Interconnect at 4 of 4 (created
  connections excluding deleted ones, outstanding requested connections, and
  connections per last-mile and per cloud-service provider). A connection's
  `provider` is a tagged union naming one side, so the two provider quotas group
  disjoint sets of connections.
- Measured the Amazon Chime SDK from 0 to 13 of its 32 measurable catalog
  quotas across four APIs: app instances, users per app instance, admins per app
  instance and endpoints per user from Chime SDK Identity; channel flows per app
  instance and processors per channel flow from Chime SDK Messaging, whose
  summaries already carry the processor list; voice connectors, SIP media
  applications and applications per SIP rule from Chime SDK Voice; and media
  pipelines, Kinesis Video Stream pools, call analytics configurations and call
  analytics pipelines from Chime SDK Media Pipelines. A pipeline counts towards
  the call analytics quota only when its detail carries a
  `MediaInsightsPipeline`.

  Meeting quotas are not measurable: a meeting exists only while it runs and no
  API lists one, which also covers attendees, video streams and replica
  meetings. Active call limits and concurrent connections per app instance user
  are in-flight counts, and the prefetch quotas bound one event's contents.
  Sources:
  [Chime SDK quotas](https://docs.aws.amazon.com/chime-sdk/latest/dg/end-user-quotas.html),
  [ListAppInstances](https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_identity-chime_ListAppInstances.html),
  [ListChannelFlows](https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_messaging-chime_ListChannelFlows.html),
  [GetMediaPipeline](https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_media-pipelines-chime_GetMediaPipeline.html).
- Completed AWS Elastic Disaster Recovery at 9 of 9 catalog quotas: source
  servers and replicating source servers, concurrent jobs, jobs per source
  server, source servers in a single job and across all jobs, launch
  configuration templates, source networks, and launch actions per resource.
  Only `STOPPED` and `DISCONNECTED` servers count as no longer replicating,
  because a paused or stalled server still holds its staging area, and an
  unknown replication state raises `NoData`.
- Completed EventBridge Schemas at 5 of 5 catalog quotas: registries,
  discoverers, schemas per registry, discovered schemas in the
  `discovered-schemas` registry, and versions per schema from the `VersionCount`
  each schema summary already reports.
- Measured AWS Launch Wizard at 3 of 4 catalog quotas: deployments excluding
  deleted ones, active deployments, and in-progress deployments. `Settings Set`
  counts saved deployment settings, which no API lists. Sources:
  [DRS quotas](https://docs.aws.amazon.com/drs/latest/userguide/drs-quotas.html),
  [EventBridge Schemas quotas](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-quota.html),
  [ListDeployments](https://docs.aws.amazon.com/launchwizard/latest/APIReference/API_ListDeployments.html).
- Measured Amazon Connect Customer Profiles from 0 to 12 of 17 catalog quotas:
  domains per account, profile object types and domain object types per domain,
  keys per object type, the longest configured retention on a domain or object
  type, calculated attributes, event streams, event triggers and integrations
  per domain, and recommenders, recommender schemas and recommender filters per
  domain.

  The five remaining quotas need a per-profile walk or bound a single record:
  objects per profile and profile history records per profile would require
  enumerating every profile in a domain, the two size quotas bound one object or
  profile, and segment snapshots per day is a rolling daily rate. Sources:
  [Customer Profiles quotas](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-connect-service-limits.html),
  [ListDomains](https://docs.aws.amazon.com/customerprofiles/latest/APIReference/API_ListDomains.html),
  [GetProfileObjectType](https://docs.aws.amazon.com/customerprofiles/latest/APIReference/API_GetProfileObjectType.html).
- Measured VPC IP Address Manager from 0 to 10 of 14 catalog quotas: IPAMs and
  resource discoveries per Region, scopes and resource-discovery associations
  per IPAM, pools per scope, pool depth, CIDRs per pool, organizational-unit
  exclusions per resource discovery, and internet-registry associations and
  prefix-list resolvers per IPAM. Scope, pool and association counts come from
  the counters AWS already reports on each resource rather than from a second
  listing. Prefix-list resolvers name their IPAM by ARN, so they are matched
  through the IPAM inventory and an unknown parent raises `NoData`.

  The four contiguous-block quotas (`Max IPv4/IPv6 Contig Block Size` and
  `Max IPv4/IPv6 Contig Blocks`) bound what a single allocation request may ask
  for and leave no inventory. Sources:
  [IPAM quotas](https://docs.aws.amazon.com/vpc/latest/ipam/quotas-ipam.html),
  [DescribeIpams](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeIpams.html),
  [DescribeIpamScopes](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeIpamScopes.html),
  [GetIpamPoolCidrs](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_GetIpamPoolCidrs.html).
- Measured Amazon EBS from 0 to 21 of 43 catalog quotas: snapshots per Region,
  fast snapshot restores in their enabled and transitioning states, archived
  snapshots per source volume, in-progress archives and restores from archive,
  provisioned IOPS for io1 and io2, storage per volume type in TiB for all seven
  types, and concurrent snapshots per volume for all seven types. A pending
  snapshot whose source volume is gone raises `NoData` rather than being
  attributed to the wrong type.

  The 22 remaining quotas are not an inventory. The nine storage and IOPS
  modification quotas apply to everything modified within a rolling six-hour
  window, which the current volume state cannot reconstruct; concurrent snapshot
  copies and concurrent volume copy operations are in-flight cross-Region
  operations that no API lists; the seven direct-API request quotas and the two
  throughput quotas are rates. Sources:
  [EBS quotas](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-resource-quotas.html),
  [DescribeVolumes](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeVolumes.html),
  [DescribeSnapshotTierStatus](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSnapshotTierStatus.html),
  [DescribeFastSnapshotRestores](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeFastSnapshotRestores.html).
- Measured Amazon SQS from 0 to 14 of 18 catalog quotas: in-flight messages on
  standard queues only, the configured visibility timeout, retention period,
  maximum message size and delivery delay, queue name length, policy size and
  the statements, actions, conditions and principals inside each policy, plus
  tags per queue and UTF-8 tag key and value lengths. The four remaining quotas
  (`Attributes per Message`, `Messages per Batch`, `Batched Message ID Length`,
  `Message Size in S3 Bucket`) bound a single request and leave no inventory to
  read. Sources:
  [SQS quotas](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-quotas.html),
  [GetQueueAttributes](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_GetQueueAttributes.html),
  [ListQueueTags](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ListQueueTags.html).
- Corrected four quota codes that no catalog contains. `backup L-9122A82`,
  `gamelift L-AED4A06` and `groundstation L-5CCF0BC` were each missing their
  final character, and `iotcore L-FC25158C` should be `L-FC25158E`
  (`Custom authentication: maximum number of active authorizers per account`).
  Every one of the 1,975 implemented quota codes now matches a catalog entry,
  and `tests/test_quota_orphans.py` fails if that stops being true.
- Wired `networkinsights` and `waf_regional` into the collector. Both were
  registered for reporting but never invoked, so their quotas counted as
  implemented while nothing measured them.
  `tests/test_registry_matches_collector.py` now compares the reporting
  registry with the collector in both directions.
- Added `scripts/quota_orphans.py`, which reports implemented quota codes that
  no export contains and separates a missing quota code from a missing service.
  It is what surfaced the four typos above.
- Expanded Lex V2 from 2 to 12 of 13 current catalog quotas by measuring build-time
  configuration in addition to the bot and version counts. The collector now walks
  every stable bot, version and locale and counts intents, slots, composite subslots,
  custom slot types, and their values and synonyms. Sample-utterance and slot-type
  value lengths are measured in UTF-16 code units, matching the AWS character
  definition. Bot networks are excluded from the bot count, the synthesized `DRAFT`
  version is never counted, and inventories that change during pagination or locales
  that are still building raise `NoData` instead of undercounting. Corrected synonym
  accounting: `SynonymList` members are `SampleValue` structures, so the previous
  string comparison rejected every slot type that has synonyms. Removed the
  module-local caches in favour of the shared `CheckContext` call cache used by every
  other check module. `Bot channel associations per bot alias` (`L-DA28F59B`) remains
  open: `lexv2-models` exposes no channel inventory, and the V1
  `GetBotChannelAssociations` operation addresses V1 bot names that V2 bots do not
  have. Sources:
  [Lex V2 quotas](https://docs.aws.amazon.com/lexv2/latest/dg/quotas.html),
  [ListBots](https://docs.aws.amazon.com/lexv2/latest/APIReference/API_ListBots.html),
  [DescribeSlotType](https://docs.aws.amazon.com/lexv2/latest/APIReference/API_DescribeSlotType.html),
  [DescribeSlot](https://docs.aws.amazon.com/lexv2/latest/APIReference/API_DescribeSlot.html).
- Completed KMS resource coverage at 5/57 current catalog quotas by counting completed
  on-demand rotations and any accepted rotation still in progress per eligible
  customer-managed key. The existing key, alias, grant and custom-key-store paths now
  validate account/Region ARNs, manager, lifecycle, key type, exact parents and
  conflicting duplicates. Corrected the nonexistent `ListCustomKeyStores` operation
  and IAM action to `DescribeCustomKeyStores`; added `ListKeyRotations` and
  `GetKeyRotationStatus`. All five checks returned `OK` with zero usage in
  BA/eu-central-1, where only AWS-managed keys currently exist. Sources:
  [KMS resource quotas](https://docs.aws.amazon.com/kms/latest/developerguide/resource-limits.html),
  [ListKeyRotations](https://docs.aws.amazon.com/kms/latest/APIReference/API_ListKeyRotations.html),
  [on-demand rotation](https://docs.aws.amazon.com/kms/latest/developerguide/rotating-keys-on-demand.html),
  [DescribeCustomKeyStores](https://docs.aws.amazon.com/kms/latest/APIReference/API_DescribeCustomKeyStores.html).
- Expanded VPC Lattice from 0/17 to 16/17 current catalog quotas. The collector now
  covers every resource quota at its documented Region, VPC, service-network, service,
  listener, target-group, resource-configuration-group or association scope. It
  separates owned regional resources from shared resources, validates ARNs, lifecycle
  states and exact parents, and deduplicates complete paginated inventories. The only
  remaining quota is auth-policy size. Also registered the existing WorkSpaces Thin
  Client environment collector; its quota was already covered by a compatible metric,
  so this adds 17 custom methods and 16 net covered quotas. Added nine VPC Lattice read
  permissions. Sources: [VPC Lattice quotas](https://docs.aws.amazon.com/vpc-lattice/latest/ug/quotas.html), [resource configurations](https://docs.aws.amazon.com/vpc-lattice/latest/APIReference/API_ListResourceConfigurations.html), [resource associations](https://docs.aws.amazon.com/vpc-lattice/latest/APIReference/API_ListServiceNetworkResourceAssociations.html), [VPC association details](https://docs.aws.amazon.com/vpc-lattice/latest/APIReference/API_GetServiceNetworkVpcAssociation.html).
- Expanded Amazon Personalize from 5/74 to 9/74 catalog quotas. New checks count
  active filters per dataset group, pending or in-progress batch inference jobs and
  solution versions per Region, and pending data deletion jobs per dataset group.
  Existing campaign and solution checks now traverse their real parent APIs instead
  of grouping on fields their list summaries do not return. All inventories validate
  account/Region ARNs, lifecycle states, parent relationships and conflicting duplicate
  pages. Added four read permissions. Sources: [Amazon Personalize quotas](https://docs.aws.amazon.com/personalize/latest/dg/limits.html), [ListBatchInferenceJobs](https://docs.aws.amazon.com/personalize/latest/dg/API_ListBatchInferenceJobs.html), [ListSolutionVersions](https://docs.aws.amazon.com/personalize/latest/dg/API_ListSolutionVersions.html), [ListDataDeletionJobs](https://docs.aws.amazon.com/personalize/latest/dg/API_ListDataDeletionJobs.html).
- Completed the resource portion of Private CA Connector for SCEP coverage at 2/17 catalog quotas, taking overall coverage above 40%. The collector counts connectors in the Region and challenges per connector through complete paginated inventories. Connector/challenge ARNs, exact parents, lifecycle states and duplicate pages are validated; a non-active connector makes its child measurement `NO_DATA`. Added `ListConnectors` and `ListChallengeMetadata`. Both BA/eu-central-1 checks returned `OK` with zero usage. The 15 remaining quotas limit API request rates. Sources: [PCA Connector for SCEP quotas](https://docs.aws.amazon.com/general/latest/gr/pca.html), [ListConnectors](https://docs.aws.amazon.com/pca-connector-scep/latest/APIReference/API_ListConnectors.html), [ListChallengeMetadata](https://docs.aws.amazon.com/pca-connector-scep/latest/APIReference/API_ListChallengeMetadata.html).
- Completed the resource portion of Private CA Connector for Active Directory coverage at 3/30 catalog quotas. The collector counts connectors in the Region, templates per connector, and group access-control entries per template through complete paginated parent inventories. ARNs, parent links, lifecycle states, SIDs and repeated pages are validated before emitting a value; unresolved parent transitions return `NO_DATA`. Added three read permissions. All three BA/eu-central-1 checks returned `OK` with zero usage. The 27 remaining quotas limit API request rates. Sources: [PCA Connector AD quotas](https://docs.aws.amazon.com/general/latest/gr/pca.html#limits_acm), [ListConnectors](https://docs.aws.amazon.com/pca-connector-ad/latest/APIReference/API_ListConnectors.html), [ListTemplates](https://docs.aws.amazon.com/pca-connector-ad/latest/APIReference/API_ListTemplates.html), [ListTemplateGroupAccessControlEntries](https://docs.aws.amazon.com/pca-connector-ad/latest/APIReference/API_ListTemplateGroupAccessControlEntries.html).
- Expanded AWS Payment Cryptography to 2/5 catalog quotas with a regional alias inventory. `ListAliases` returns every alias in the caller's account and Region; the collector validates alias names and any reported key ARN, deduplicates identical repeated pages, and rejects conflicting identities. Added `payment-cryptography:ListAliases`. A read-only BA/eu-central-1 check returned `OK` with zero aliases. The three remaining quotas are request rates without a compatible metric in this catalog. Sources: [Payment Cryptography quotas](https://docs.aws.amazon.com/payment-cryptography/latest/userguide/quotas.html), [ListAliases](https://docs.aws.amazon.com/payment-cryptography/latest/APIReference/API_ListAliases.html).
- Completed AWS Outposts coverage at 2/2 current catalog quotas. The paginated site inventory counts sites owned by the monitored account in the current Region, and the Outpost inventory reports the maximum number of owned Outposts per known site. Account, owner, parent and optional ARN relationships are validated; identical repeated pages are deduplicated, while incomplete or conflicting identities return `NO_DATA`. Added both required read permissions. Sources: [AWS Outposts quotas](https://docs.aws.amazon.com/outposts/latest/userguide/outposts-limits.html), [ListSites](https://docs.aws.amazon.com/outposts/latest/APIReference/API_ListSites.html), [ListOutposts](https://docs.aws.amazon.com/outposts/latest/APIReference/API_ListOutposts.html).
- Completed MediaConnect coverage at 6/6 current catalog quotas. `DescribeFlow` provides the maximum output count per flow; the three paginated Router inventories count inputs, outputs and network interfaces in the monitored Region. Flow/detail parents, lifecycle states, resource identities, reported Regions and duplicate pages are validated before emitting a sample. Added four read permissions. All four new BA/eu-central-1 checks returned `OK` with zero current usage. Sources: [MediaConnect quotas](https://docs.aws.amazon.com/mediaconnect/latest/ug/quotas.html), [ListRouterOutputs](https://docs.aws.amazon.com/mediaconnect/latest/api/API_ListRouterOutputs.html), [Router network interfaces](https://docs.aws.amazon.com/mediaconnect/latest/ug/managing-router-network-interfaces.html).
- Registered the existing OpenSearch domain and OpenSearch UI application inventories, closing two coverage-reporting omissions. The application inventory now validates required IDs, ARNs and lifecycle states, deduplicates identical repeated pages and rejects conflicting identities. Corrected its IAM action from the invalid `opensearch:ListApplications` prefix to `es:ListApplications`. Both read-only BA/eu-central-1 inventories returned `OK` with zero current usage. Sources: [OpenSearch UI quotas](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/opensearch-ui-endpoints-quotas.html), [ListApplications](https://docs.aws.amazon.com/opensearch-service/latest/APIReference/API_ListApplications.html), [application permissions](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/application-getting-started.html#application-getting-started-permissions).
- Expanded Rekognition to 13/92 catalog quotas by measuring the maximum configured inference units per running Custom Labels model. `MaxInferenceUnits` is the model's auto-scaling ceiling; when automatic scaling is disabled, the check uses the fixed `MinInferenceUnits` capacity. Invalid capacity metadata and versions in `STARTING`, `STOPPING` or `DELETING` return `NO_DATA` because their reservation is unresolved. A read-only BA/eu-central-1 check returned `OK` with zero current usage; populated and failure paths are covered by offline fixtures. Sources: [running Custom Labels models](https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/running-model.html), [project-version metadata](https://docs.aws.amazon.com/rekognition/latest/APIReference/API_ProjectVersionDescription.html).
- Completed Migration Hub Refactor Spaces coverage at 4/4 catalog quotas. The collector traverses every visible environment and its applications, services and routes, then counts resources owned by the monitored account across the Region. This preserves the service's multi-account model: the environment owner also owns child resources even when a participant account creates them. Every page is validated for unique identities, supported lifecycle states, required ownership and exact environment/application parents; incomplete or conflicting inventories return `NO_DATA`. Added four read permissions and registered the new collector. All four BA/eu-central-1 checks returned `OK` with zero current usage. Sources: [Refactor Spaces quotas](https://docs.aws.amazon.com/general/latest/gr/migrationhub-refactor-spaces.html), [multi-account ownership](https://docs.aws.amazon.com/migrationhub-refactor-spaces/latest/userguide/how-it-works.html), [service ownership](https://docs.aws.amazon.com/migrationhub-refactor-spaces/latest/APIReference/API_CreateService.html).
- Expanded Route 53 Resolver from 8/13 to 12/13 catalog quotas. New checks measure DNS Firewall rule-group associations per VPC, rules per Firewall rule group, and Resolver-rule and Firewall-group associations per Route 53 Profile. Every result uses the maximum at its documented parent scope; duplicate associations, invalid states, and mismatched rule parents return `NO_DATA`. The domain-list inventory now excludes AWS-managed lists before counting lists or reading domains, fixing a live `AccessDenied` and preventing managed resources from inflating customer quotas. Added `ListFirewallRuleGroupAssociations` and `ListFirewallRules` permissions. All twelve BA/eu-central-1 checks returned `OK` with zero customer usage. The single remaining quota limits domains in one S3 import file and cannot be derived from retained domain lists. Sources: [Route 53 Resolver quotas](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/DNSLimitations.html#limits-api-entities-resolver), [Firewall rule-group associations](https://docs.aws.amazon.com/Route53/latest/APIReference/API_route53resolver_ListFirewallRuleGroupAssociations.html), [Firewall rules](https://docs.aws.amazon.com/Route53/latest/APIReference/API_route53resolver_ListFirewallRules.html), [Route 53 Profiles](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/profiles.html).
- Completed Route 53 Profiles coverage at 4/4 catalog quotas. Profile counts exclude profiles shared into the account, while profiles shared by the account remain owned. VPC associations and typed private-hosted-zone and VPC-endpoint resource associations use the maximum per profile. Creating, updating and deleting associations retain their reservation until the API reports `DELETED`; failed, unknown, duplicate or parent-inconsistent records return `NO_DATA`. Added `ListProfileAssociations` and `ListProfileResourceAssociations` permissions. All four BA/eu-central-1 checks returned `OK` with zero current usage. Sources: [Route 53 Profile quotas](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/DNSLimitations.html#limits-api-entities-profiles), [VPC associations](https://docs.aws.amazon.com/Route53/latest/APIReference/API_route53profiles_ListProfileAssociations.html), [profile resource associations](https://docs.aws.amazon.com/Route53/latest/APIReference/API_route53profiles_ListProfileResourceAssociations.html).
- Completed AWS Proton coverage at 7/7 catalog quotas. Components are counted account-wide; environment-account connections are read from both management- and environment-account views and grouped by environment account; service instances use the maximum per service. Template inventories now correctly combine service and environment templates, and template-version usage traverses every template, major version and minor version. Duplicate identities, inconsistent account or parent scopes, and incomplete records return `NO_DATA`. Added six read permissions. All seven BA/eu-central-1 checks returned `OK`; their inventories are currently empty. Sources: [AWS Proton quotas](https://docs.aws.amazon.com/proton/latest/userguide/ag-limits.html), [environment-account connections](https://docs.aws.amazon.com/proton/latest/APIReference/API_ListEnvironmentAccountConnections.html), [template versions](https://docs.aws.amazon.com/proton/latest/APIReference/API_ListEnvironmentTemplateVersions.html), [service instances](https://docs.aws.amazon.com/proton/latest/APIReference/API_ListServiceInstances.html).
- Completed Application Auto Scaling coverage at 16/16 catalog quotas. Scheduled actions and all scaling-policy types are grouped by the full namespace/resource/dimension target identity; step adjustments are measured only inside step-scaling policies. Every inventory traverses all 15 namespaces supported by the pinned SDK, including Neptune and WorkSpaces even though they have no separate target-count quota in the current BA catalog. Duplicate identities, namespace mismatches, malformed targets, unknown policy types and incomplete step configurations return `NO_DATA`. Added `DescribeScheduledActions` and `DescribeScalingPolicies` permissions. All 30 namespace-specific BA/eu-central-1 inventory calls succeeded and returned no scheduled actions or scaling policies. Sources: [Application Auto Scaling quotas](https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-quotas.html), [scheduled actions](https://docs.aws.amazon.com/autoscaling/application/userguide/scheduled-scaling-policy-overview.html), [step scaling](https://docs.aws.amazon.com/autoscaling/application/userguide/step-scaling-policy-overview.html).
- Completed App Runner coverage at 6/6 catalog quotas. Connections, unique active auto-scaling and observability configuration names, and active VPC connector names are counted account-wide; VPC ingress connections use the maximum per service required by the quota scope. Configuration list calls explicitly request only the latest revision, deleted/inactive resources are excluded, and duplicate identities or unknown states return `NO_DATA`. Status matching is case-insensitive because the live API returns lower-case auto-scaling status values despite upper-case SDK enums. Added five read permissions. All six BA/eu-central-1 checks were queried successfully: one auto-scaling and one observability configuration exist; the other four inventories are empty. Sources: [App Runner quotas](https://docs.aws.amazon.com/general/latest/gr/apprunner.html), [auto-scaling configuration inventory](https://docs.aws.amazon.com/apprunner/latest/api/API_ListAutoScalingConfigurations.html), [VPC connector lifecycle](https://docs.aws.amazon.com/apprunner/latest/api/API_VpcConnector.html).
- Added all five open AWS RAM audit checks: account-wide resource associations; maximum resource and principal associations per resource share; customer-managed permissions account-wide and per resource type. Association inventories count the same resource or principal separately in each share, as required by AWS's quota semantics, while permission inventories deduplicate versions by permission ARN. Missing or conflicting identities return `NO_DATA`, and no resource/principal identifiers are copied into metadata. Added `ListPermissions` permission. All three backing BA/eu-central-1 inventories were queried successfully and are currently empty. RAM is now 2/2 in the current catalog; four additional checks cover retained older catalog entries. Sources: [AWS RAM quotas](https://docs.aws.amazon.com/ram/latest/userguide/service-quotas.html), [ListResources](https://docs.aws.amazon.com/ram/latest/APIReference/API_ListResources.html), [ListPrincipals](https://docs.aws.amazon.com/ram/latest/APIReference/API_ListPrincipals.html).
- Completed Recycle Bin coverage at 2/2 catalog quotas. Rule inventories are fully paginated for EBS snapshots, EC2 images and EBS volumes; the existing rule count now covers all three required API scopes. Every rule detail is validated against its list scope, and the maximum tag key/value-pair count is measured per tag-level retention rule without including Region-level exclusion tags or copying tag contents into metadata. Added `GetRule` permission. All three BA/eu-central-1 inventories were queried successfully and are currently empty. Sources: [Recycle Bin quotas](https://docs.aws.amazon.com/general/latest/gr/rbin.html), [GetRule](https://docs.aws.amazon.com/recyclebin/latest/APIReference/API_GetRule.html).
- Completed DLM coverage at 2/2 catalog quotas. Every lifecycle-policy detail is inspected and the maximum target-account count is measured per individual schedule sharing rule. Policy identities, schedule/rule structures and unique non-empty target accounts are validated; account IDs are not copied into metadata. Added `GetLifecyclePolicy` permission. Source: [DLM policy details](https://docs.aws.amazon.com/dlm/latest/APIReference/API_PolicyDetails.html), [DLM sharing rule](https://docs.aws.amazon.com/dlm/latest/APIReference/API_ShareRule.html).
- Completed Audit Manager coverage at 5/5 catalog quotas. The new check reads every assessment detail and counts the union of account IDs in `metadata.scope.awsAccounts`, matching AWS's quota definition of unique accounts across all assessments. Assessment identities and details are validated, and account metadata is not copied into measurements. Added `GetAssessment` permission. Source: [Audit Manager assessment scope](https://docs.aws.amazon.com/audit-manager/latest/userguide/edit-assessment.html), [Scope API](https://docs.aws.amazon.com/audit-manager/latest/APIReference/API_Scope.html).
- Added all six Network Insights checks from the retained catalog: Network Access Analyzer scopes, retained scope analyses and running scope analyses, plus Reachability Analyzer paths, retained analyses and running analyses. Each EC2 inventory is fully paginated and deduplicated; conflicting pages and unknown analysis states return `NO_DATA`. Added four read permissions. All four inventory APIs were read successfully in BA/eu-central-1 and are currently empty. The 2026-09-10 BA catalog snapshot no longer contains `networkinsights`, so this closes the audit section without changing the current 4,118/10,398 total. Sources: [Network Access Analyzer quotas](https://docs.aws.amazon.com/vpc/latest/network-access-analyzer/network-access-analyzer-limits.html), [Reachability Analyzer quotas](https://docs.aws.amazon.com/vpc/latest/reachability/reachability-analyzer-limits.html).
- Expanded AWS Network Firewall from 4/27 to 25/27 catalog quotas and corrected the stateless-rule-group quota code. Complete account inventories now cover firewalls, policies, account-owned stateful/stateless rule groups, TLS configurations, VPC endpoint associations and container associations. Detail checks measure policy association counts, consumed rule capacity, rule-group references and reuse, TLS references and certificates, configured rule-group capacity, Suricata rules-string bytes, IP set references, custom actions, endpoint associations per firewall/Availability Zone and account-wide container resource filters. Duplicate identities, inconsistent details, invalid references and incomplete endpoint scope data return `NO_DATA`. Added seven read permissions. The two remaining quotas are live endpoint bandwidth and expanded Suricata rule character length; static configuration APIs cannot establish either value without traffic telemetry or exact variable expansion semantics. Sources: [Network Firewall quotas](https://docs.aws.amazon.com/general/latest/gr/network-firewall.html), [firewall policy response](https://docs.aws.amazon.com/network-firewall/latest/APIReference/API_FirewallPolicyResponse.html), [rule-group capacity](https://docs.aws.amazon.com/network-firewall/latest/developerguide/nwfw-rule-group-capacity.html), [container monitoring configuration](https://docs.aws.amazon.com/network-firewall/latest/APIReference/API_ContainerMonitoringConfiguration.html).
- Expanded EC2 Image Builder from 3/23 to 20/23 catalog quotas. Account inventories now count owned image/container recipes, distribution and infrastructure configurations, and image pipelines. Detail checks measure components per image recipe; component and workflow parameters; UTF-8 component, workflow and Docker-template sizes; workflow steps parsed with the safe YAML loader; and per-distribution-Region launch templates, SSM parameters and cross-account AMI targets. Configuration identities and regional scopes are validated, and parameter values are measured without being copied into metadata. Added ten read permissions. The three remaining quotas are concurrent builds, concurrent resource-state updates and workflows attached to ad-hoc image builds; deriving them would require a potentially unbounded retained-build traversal without a complete active-only account API. Sources: [Image Builder quotas](https://docs.aws.amazon.com/general/latest/gr/imagebuilder.html), [recipe constraints](https://docs.aws.amazon.com/imagebuilder/latest/userguide/manage-recipes.html), [workflow constraints](https://docs.aws.amazon.com/imagebuilder/latest/userguide/manage-image-workflows.html), [distribution structure](https://docs.aws.amazon.com/imagebuilder/latest/APIReference/API_Distribution.html).
- Expanded FinSpace Managed kdb from 1/32 to 28/32 catalog quotas. Complete per-environment inventories now measure clusters by AZ mode, users, scaling groups, volumes, databases and dataviews; live nodes are classified across seven dedicated and nine scaling-group host types; volume, savedown and database-cache storage are summed in GiB. Every environment-scoped result reports the highest single-environment usage instead of an account-wide sum. Duplicate identities, inconsistent detail responses, dangling scaling-group references and invalid storage sizes return `NO_DATA`. Added nine read permissions. The four remaining quotas are concurrent changeset/dataview processing and per-volume read/write mounts, whose current use is not unambiguously separated by the control-plane inventories. Sources: [FinSpace quotas](https://docs.aws.amazon.com/finspace/latest/userguide/finspace-quotas.html), [cluster details](https://docs.aws.amazon.com/finspace/latest/management-api/API_GetKxCluster.html), [dataview inventory](https://docs.aws.amazon.com/finspace/latest/management-api/API_ListKxDataviews.html), [volume inventory](https://docs.aws.amazon.com/finspace/latest/management-api/API_ListKxVolumes.html).
- Expanded IoT SiteWise from 1/42 to 24/42 catalog quotas. Model checks now distinguish `ASSET_MODEL`, `COMPONENT_MODEL` and `INTERFACE`, measure root/all/interface properties, hierarchy definitions, distinct models and depth per hierarchy tree, parents per child model, composite counts/depth/properties, component/interface reuse, assets per model and children per asset. Formula checks count configured variables and function calls while ignoring function-like text inside string literals. Running bulk imports and retained event-detection enrichment jobs are measured at account and workspace scope. Model configuration checks require a stable `ACTIVE` detail response; unknown references, cycles, duplicate identities, malformed paths and parent/type mismatches return `NO_DATA`. Added eleven read permissions. Sources: [SiteWise quotas](https://docs.aws.amazon.com/iot-sitewise/latest/userguide/endpoints-and-quotas.html), [model types](https://docs.aws.amazon.com/iot-sitewise/latest/APIReference/API_ListAssetModels.html), [model properties](https://docs.aws.amazon.com/iot-sitewise/latest/APIReference/API_ListAssetModelProperties.html), [component models](https://docs.aws.amazon.com/iot-sitewise/latest/userguide/create-asset-and-component-models.html).
- Added 21 Glue checks, bringing the service to 33/43 catalog quotas. New inventory measurements cover user-defined functions and partitions at account and parent scope, development endpoints and their configured DPUs, databases per catalog, integrations, data-quality rulesets, jobs per trigger and named LF-Tag expressions. Concurrency checks distinguish active and queued job runs and include active crawler, ML-transform, data-quality evaluation/recommendation, materialized-view refresh and column-statistics task runs. Transitional `STARTING`/`STOPPING` states retain their reservation; completed states do not. Catalog, database, table, run and task identities are validated across complete pagination, and parent mismatches or unknown states return `NO_DATA`. Added thirteen Glue and one Lake Formation read permission. Sources: [Glue quotas](https://docs.aws.amazon.com/general/latest/gr/glue.html), [job-run states](https://docs.aws.amazon.com/glue/latest/webapi/API_JobRun.html), [development endpoint DPUs](https://docs.aws.amazon.com/glue/latest/webapi/API_DevEndpoint.html), [data-quality API](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-data-quality-api.html).
- Expanded Firewall Manager to 25/30 catalog quotas. Checks cover custom application/protocol lists and entries, resource sets and resources, organization administrators, member accounts, per-policy account/organizational-unit/tag scopes, Network Firewall rule-group references, summed stateful/stateless capacities and IPv4 CIDRs, DNS Firewall rule groups, common/content-audit security groups, WAF Classic and WAFV2 rule groups, partner-managed WAF groups, WAFV2 WCU, and directional network ACL rules. Custom-list calls explicitly exclude AWS defaults; resource and scope identities are deduplicated across pages and include/exclude maps. Distributed, centralized and imported Network Firewall JSON structures are handled without copying policy contents into metadata. Rule-group capacities are resolved through Network Firewall and WAF APIs with identity, type and version checks. Policies of unrelated types are skipped before parsing managed-service JSON, while missing or inconsistent data on a relevant policy returns `NO_DATA`. Added seven FMS and three rule-group read permissions. Sources: [FMS quotas](https://docs.aws.amazon.com/general/latest/gr/fms.html), [SecurityServicePolicyData](https://docs.aws.amazon.com/fms/2018-01-01/APIReference/API_SecurityServicePolicyData.html), [managed lists](https://docs.aws.amazon.com/waf/latest/developerguide/fms-lists.html).
- Replaced the broken inline OpenSearch Serverless checks with a dedicated collector covering all 21 AOSS catalog quotas. The former network-policy method does not exist and the remaining list calls omitted required policy types; the registered collector now uses typed, fully paginated security, access, lifecycle, security-config and collection-group inventories. Policy sizes use the whitespace-free UTF-8 JSON returned by AOSS; SAML size uses metadata bytes. Collection counts are split by Classic/NextGen generation, and configured account/group OCU maxima feed both default-setting and total allocated-capacity checks. Empty collection groups do not consume allocated capacity. Added seven read permissions. Sources: [AOSS quotas](https://docs.aws.amazon.com/general/latest/gr/opensearch-service.html), [collection-group capacity](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/collection-groups-capacity-limits.html), [SecurityPolicyDetail](https://docs.aws.amazon.com/opensearch-service/latest/ServerlessAPIReference/API_SecurityPolicyDetail.html).
- Added 44 AWS FIS checks: actions, stop conditions and target-account configurations per experiment template; currently parallel actions; and resolved resource counts for all 40 action-specific target quotas in the BA catalog. Together with two compatible official metrics, FIS coverage is now 46/53. Dynamic-target quotas count only tag- or parameter-selected targets, deduplicate resolved resources across matching actions, and take the maximum per active experiment. Target resolution that has not finished, inconsistent inventories and multi-account experiments whose resolved-target API lacks a documented account identity return `NO_DATA`. The BA live inventory currently has no templates or experiments; all mapped action IDs were verified against the live `eu-central-1` action catalog. Added five FIS read permissions. Sources: [FIS quotas](https://docs.aws.amazon.com/fis/latest/userguide/fis-quotas.html), [resolved targets](https://docs.aws.amazon.com/fis/latest/userguide/list-experiment-resolved-targets.html), [action sequencing](https://docs.aws.amazon.com/fis/latest/userguide/action-sequence.html).
- Added all seven remaining non-throttle Connect Cases checks: related items, files and SLAs per case; fields per custom related item; parent and child option values per field-options rule; and field-options rules per template. `SearchAllRelatedItems` supplies one paginated domain-wide inventory with case IDs and typed content, while `BatchGetCaseRule` and `GetTemplate` resolve configuration details. Cases now covers all 14 content/configuration quotas in the catalog; its other 86 entries are API rate or burst limits. Unknown unions, incomplete batches, missing references and conflicting pages return `NO_DATA`; item contents and option values are not copied into metadata. Sources: [SearchAllRelatedItems](https://docs.aws.amazon.com/connect/latest/APIReference/API_connect-cases_SearchAllRelatedItems.html), [BatchGetCaseRule](https://docs.aws.amazon.com/connect/latest/APIReference/API_connect-cases_BatchGetCaseRule.html), [Cases quotas](https://docs.aws.amazon.com/general/latest/gr/connect_region.html).
- Added three net CloudFormation checks: original template size in UTF-8 MiB, auto-deployment dependencies per StackSet, and queued operations per StackSet. The first uses `TemplateStage=Original`; dependency details come from `DescribeStackSet.AutoDeployment.DependsOn`; operation pages count only the explicit `QUEUED` status. Corrected the module quota code from the nonexistent `L-DCC58D6E` to catalog code `L-DCC58E6D`. CloudFormation now has methods for 23/104 catalog quotas and covers 25/104 after compatible metrics. Added `DescribeStackSet` and `ListStackSetOperations` permissions. Sources: [CloudFormation template and StackSet quotas](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html), [AutoDeployment](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_AutoDeployment.html), [ListStackSetOperations](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_ListStackSetOperations.html).
- Added explicit official-metric mappings for Step Functions open executions and open Map Runs. AWS documents `OpenExecutionCount` and `ApproximateOpenMapRunCount` as the account/Region quota signals, but the Service Quotas catalog does not attach their `UsageMetric` metadata. Collector, historical reports, runtime coverage and the offline audit now share the same fixed quota-code mapping and query `Maximum` with no dimensions. Step Functions coverage rises from 4/98 to 6/98. Both metrics are approximate, best-effort gauges by AWS definition. Sources: [Step Functions CloudWatch metrics](https://docs.aws.amazon.com/step-functions/latest/dg/procedure-cw-metrics.html), [Step Functions quotas](https://docs.aws.amazon.com/general/latest/gr/step-functions.html).
- Added eleven CloudFormation checks for resources, parameters, outputs, mappings, mapping attributes and dynamic references per deployed template, plus the maximum logical-ID, mapping/attribute, parameter and output name lengths and UTF-8 description bytes. CloudFormation now has methods for 19/104 catalog quotas and 22/104 are covered after compatible metrics. Checks inspect the `Processed` template of every active stack, so transforms are measured in their deployed form; deleted stack history is excluded. Sources: [GetTemplate](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_GetTemplate.html), [CloudFormation quotas](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html), [dynamic references](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html).
- JSON and YAML templates are supported, including CloudFormation short-form intrinsic tags. Required sections, mapping shapes, identities and pages are validated before emitting a sample; a partial stack/template inventory returns `NO_DATA` or `ERROR` instead of a lower value. Template bodies and dynamic-reference contents are never placed in measurement metadata. Added `cloudformation:GetTemplate` and a pinned PyYAML dependency; the reproducible Lambda-layer build removes PyYAML's optional native accelerator and uses its pure-Python safe loader.
- Added four Connect Cases checks for fields and layouts per domain, field options per single-select field, and field slots per layout. Cases now has methods for 7/100 catalog quotas. Layout checks traverse both the top and more-info panels; repeated slots count separately. Active and inactive options both remain configured and count. Unknown field/layout union types, deleted or mismatched details, conflicting pages and incomplete sections return `NO_DATA`. Added four read permissions. Sources: [Cases quotas](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-connect-service-limits.html), [GetLayout](https://docs.aws.amazon.com/connect/latest/APIReference/API_connect-cases_GetLayout.html), [case field options](https://docs.aws.amazon.com/connect/latest/adminguide/case-fields.html).
- Added four CloudFormation registry checks for private resource types and live versions per private resource, module and hook. CloudFormation now has methods for 11/104 catalog quotas; the private-resource count already had a compatible official metric, so these checks add three net covered quotas. `ListTypes(Visibility=PRIVATE)` also returns activated public extensions, which are now excluded through `IsActivated`. Type/version pages are deduplicated and inconsistent parent/type data or an empty live-version inventory returns `NO_DATA`. Added `ListTypeVersions` permission. Sources: [ListTypes visibility](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_ListTypes.html), [extension version quotas](https://docs.aws.amazon.com/general/latest/gr/cfn.html).
- Added eight Rekognition checks: running Custom Labels models, training jobs, model copy jobs, concurrent face-search and label-detection processors, processor associations per Kinesis input/output stream, and concurrent Media Analysis jobs. Rekognition now has methods for 12/92 catalog quotas. The existing project, model and project-policy checks now request `Features=[CUSTOM_LABELS]`, preventing Content Moderation projects from entering Custom Labels inventories. Sources: [DescribeProjects filter](https://docs.aws.amazon.com/rekognition/latest/APIReference/API_DescribeProjects.html), [model version states](https://docs.aws.amazon.com/rekognition/latest/APIReference/API_ProjectVersionDescription.html).
- Streaming concurrency uses type-specific states: label detection stays `STARTING` throughout processing, while face search uses `RUNNING`. Stopped processors still count toward configured input/output stream associations. Unknown processor types, status changes during collection and unverified transitional reservations return `NO_DATA`. Media Analysis counts `IN_PROGRESS`; `CREATED`/`QUEUED` reservations remain unresolved. Inventories deduplicate identities and reject conflicting pages; no media files or model artifacts are downloaded. Added `DescribeStreamProcessor` and `ListMediaAnalysisJobs` read permissions. Sources: [label-detection lifecycle](https://docs.aws.amazon.com/rekognition/latest/dg/streaming-labels-detection.html), [processor settings](https://docs.aws.amazon.com/rekognition/latest/APIReference/API_DescribeStreamProcessor.html).
- Added five SSM checks for Distributor package versions, association versions, advanced-parameter policies, private shares per document and publicly shared documents per account. Fixed the existing `ListDocuments` request to use `Filters=[{Key: Owner, Values: [Self]}]`; the previous top-level `Owner` argument failed SDK validation. Version inventories now deduplicate retained versions and reject missing identities, empty inventories and mismatched parents. Sources: [SSM quotas](https://docs.aws.amazon.com/general/latest/gr/ssm.html), [ListDocuments](https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_ListDocuments.html).
- Document sharing reads both `AccountIds` and `AccountSharingInfoList` across every page, deduplicates account IDs and excludes the public `all` marker from private-share counts. Public quotas count documents, not recipient accounts. Parameter policies use metadata only; parameter values are not requested, and policy text is omitted from measurements. Source: [DescribeDocumentPermission](https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_DescribeDocumentPermission.html).
- Added four Bedrock Data Automation checks: blueprint versions, schema size in characters, libraries per account and vocabulary phrases per library. Schema maxima include listed LIVE/DEVELOPMENT stages and saved versions; the returned schema text is measured without reformatting or UTF-8 byte conversion. Unknown blueprint versions, including an unresolved `0`, return `NO_DATA`. Vocabulary counts sum entity summaries across all languages, deduplicate entity IDs and reject conflicting counts without retrieving phrase text. Sources: [blueprint operations](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-blueprint-operations.html), [library entity summaries](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-library-listing-entities.html), [BDA quotas](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-limits.html).
- These nine custom checks add seven previously uncovered quotas; blueprint versions and public document sharing already had compatible official metrics. SSM now has methods for 72/160 catalog quotas, Bedrock for 98/722. Added two SSM and three Bedrock read permissions.
- Added 16 Bedrock checks: six Automated Reasoning configuration/version/test counts, nine model-evaluation inventory/configuration checks, and concurrent model imports. Bedrock now has methods for 95/722 catalog quotas. Policy maxima include the working draft and every published version; published-version counts exclude the draft. Exports and paginated lists share the collection cache, and policy/test content is omitted from measurement metadata. Sources: [policy/version inventory](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ListAutomatedReasoningPolicies.html), [definition export](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ExportAutomatedReasoningPolicyVersion.html).
- Evaluation inventories explicitly select `ModelEvaluation`, separating them from RAG evaluation. Human and automated model counts use separate scopes; dataset and per-dataset metric limits apply to automated jobs, while custom metrics and custom prompt datasets use the human scope. Completed evaluations remain in the retained-job count but leave concurrency counts. `Stopping`, `Deleting` and unknown states produce `NO_DATA` for the affected concurrency check. Sources: [quota definitions](https://docs.aws.amazon.com/general/latest/gr/bedrock.html), [evaluation job configuration](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_GetEvaluationJob.html).
- Fixed the existing Data Automation blueprint count to request both `LIVE` and `DEVELOPMENT` stages with `resourceOwner=ACCOUNT`, deduplicating by blueprint ARN. The API's default list omitted development-only blueprints. Added five Bedrock read permissions for policy exports/test cases and evaluation/import jobs. Source: [ListBlueprints defaults and filters](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_data-automation_ListBlueprints.html).
- Added 140 Clean Rooms ML checks: 129 training-instance types validated against the pinned SDK, total training instances, account/membership training and inference jobs, trained-model versions, active input channels, configured-algorithm associations and three audience job counts. Registered the collector and added nine read-only ML actions. Clean Rooms ML now has methods for 140/148 quotas (94.6%).
- Training inventories cover every creator membership and model version, deduplicate repeated versions, and reject missing or inconsistent inventories. Distributed training uses the configured instance count; `ACTIVE` model artifacts are excluded. Pending/cancelling/deleting compute reservations return `NO_DATA` for the affected type; pending training jobs still count toward their explicit job quota. Zero applied limits never receive a fabricated utilization percentage. Sources: [quotas](https://docs.aws.amazon.com/clean-rooms/latest/userguide/clean-rooms-ml-quotas.html), [model versions](https://docs.aws.amazon.com/cleanrooms-ml/latest/APIReference/API_ListTrainedModelVersions.html), [training resource configuration](https://docs.aws.amazon.com/cleanrooms-ml/latest/APIReference/API_GetTrainedModel.html).
- Added 25 Bedrock configuration checks: 14 flow-node counts, conditions per node, seven guardrail policy counts/text lengths, published guardrail/prompt versions, and inference-profile endpoints. Bedrock now has methods for 79/722 catalog quotas. Configuration maxima include working drafts and saved versions; a larger older version is not hidden by a smaller draft. Guardrail contents are not included in measurement metadata. Nested Flow `Loop` nodes return `NO_DATA` until their quota scope is verified. Sources: [flow versions](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_GetFlowVersion.html), [guardrail versions](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ListGuardrails.html), [prompt versions](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_ListPrompts.html).
- Corrected eleven existing IAM actions that incorrectly used the SDK client prefixes `bedrock-agent:` and `bedrock-data-automation:`. These now use `bedrock:`; added `GetFlow`, `GetFlowVersion` and `GetGuardrail`. A regression check verifies the deployed policy prefixes and required actions. AWS's [Flows sample permissions](https://github.com/aws-samples/amazon-bedrock-flows-samples) use the same IAM prefix.
- Added 36 Bedrock batch-job checks with explicit model-ID/quota-code mappings, including two custom-model quotas. Cross-region/application profiles resolve to one underlying foundation model; customized models resolve through their base-model ARN. Completed jobs are excluded, repeated job ARNs are deduplicated, and conflicting duplicates or incomplete inventories are rejected. `Submitted`/`InProgress` count; target-model jobs in `Validating`, `Scheduled` or `Stopping` produce `NO_DATA` until quota-reservation semantics are verified. Sources: [supported model IDs](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-supported.html), [job states](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ModelInvocationJobSummary.html).
- Added nine EKS configuration/inventory checks, eight present in the current BA catalog and one access-entry quota present in the older catalog. EKS now has methods for 12/12 BA quotas. CIDRs count inside remote-network wrappers; Fargate labels use each selector's maximum; managed nodes count actual backing Auto Scaling members rather than scaling targets. Missing required inventory returns `NO_DATA`.
- Added two AgentCore checks for entries and dimension keys per gateway rate limit, bringing AgentCore to 28/199 covered catalog quotas (27 custom checks and one compatible metric).
- Added 20 Connect checks and corrected the users quota code to `L-9A46857E`, bringing Connect to 34/338 covered quotas. New checks cover Lex V2 associations, Lambda functions, data tables, workspaces, notifications, email addresses, predefined attributes, eight integration types, hours overrides, agent proficiencies, routing-profile queue/channel combinations and data-table attributes.
- Connect inventories now resolve each instance's applied limit with `GetServiceQuota(ContextId=instance ARN)` and select the highest usage/limit ratio. A larger raw inventory can have lower utilization when its limit was increased. Unresolved limits and partial failures do not produce a successful sample. Standard queues exclude agent queues; application associations use the APPLICATION filter. Manual-assignment and normal routing queues have separate limits, so their counts are not summed. See [Connect scopes and routing-profile limits](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-connect-service-limits.html) and [GetServiceQuota](https://docs.aws.amazon.com/servicequotas/2019-06-24/apireference/API_GetServiceQuota.html).
- Added a resumable AWS utilization-report exporter with complete-page, identity and timestamp validation. A live BA/eu-central-1 report on 2026-09-11 returned six quotas, all already covered by compatible metrics, so this source adds no coverage in the observed account. The exporter is not integrated into the collector.
- Validation: 860 tests passed; Terraform format/validate passed; isolated function ZIP/dependency-layer imports passed; release metadata, dependency consistency and Python bytecode compilation passed. All five KMS resource measurements, all 16 VPC Lattice resource measurements, WorkSpaces Thin Client environments, all nine Amazon Personalize measurements and the PCA Connector SCEP, PCA Connector AD, Payment Cryptography alias, AWS Outposts, MediaConnect, OpenSearch domain/UI, Rekognition Custom Labels, Migration Hub Refactor Spaces, Route 53 Resolver, Route 53 Profiles, AWS Proton, Application Auto Scaling, App Runner, AWS RAM, Recycle Bin, Network Firewall, Network Insights, DLM, FinSpace and owned Image Builder inventories were queried successfully in BA/eu-central-1. FIS actions, templates and experiments were read live in the same account/Region; populated KMS, VPC Lattice, Personalize, PCA Connector SCEP, PCA Connector AD, Payment Cryptography aliases, AWS Outposts, MediaConnect, OpenSearch UI, Rekognition, Migration Hub Refactor Spaces, Route 53 Resolver, Route 53 Profiles, Proton, FIS, AOSS, FMS, Glue, SiteWise, FinSpace, Image Builder, Network Firewall, Network Insights, Audit Manager, DLM, Recycle Bin, AWS RAM, App Runner and Application Auto Scaling paths were verified with offline fixtures. No deployment was performed.

## Previous verified changes

- Added 520 AppStream checks: 502 instance-type/image-type mappings, 15 platform-scoped builder/session quotas, image-copy concurrency, image sharing and user-pool users.
- AppStream now has methods for 527/529 quotas. Concurrent image updates and AgentAccessMCP request rate remain unsupported; the AgentAccessMCP session quota already has a compatible official metric.
- Native, BYOL and imported CUSTOM instance types are distinguished explicitly. On-Demand idle fleet capacity counts; session slots never substitute for multi-session instance counts.
- AppStream fleet scaling/draining transitions and image-builder states other than RUNNING return NO_DATA. A registered method is not a guarantee of a usable sample for every resource state. Stopped image-builder quota reservation semantics still need authoritative verification.
- Elastic sessions include API, SAML, USERPOOL and AWS_AD authentication, retain disconnected sessions and deduplicate IDs within each fleet.
- Added 25 AgentCore checks covering inventories, per-parent maxima, memory strategies and active browser/code-interpreter sessions. System tools contribute to session quotas but not custom-tool configuration quotas.
- Updated Boto3/Botocore to 1.43.92 and s3transfer to 0.19.2; rebuilt the Lambda dependency layer and added the required read permissions.
- Validation: 396 tests passed; Terraform format/validate passed; isolated function ZIP/rebuilt dependency-layer imports passed; pip check passed. No deployment or live AWS collection was performed in this iteration.

## Earlier verified changes

- Added 140 EC2 dedicated-host family quotas, with ownership/family checks and explicit unknown states during recovery.
- Added EKS native cluster quota L-1194D53C and corrected external registration quota L-FDFA5F81.
- Corrected central AppStream registration and the offline coverage tool: native AWS fields, aliases, account scope and union with official metrics.

## Services with no coverage at all

Every service that reports zero covered quotas has been checked against the SDK.
13 services with 91 measurable quotas remain, for two distinct reasons.

**No SDK client (80 quotas, 7 services).** `botocore` ships no client for
`lookoutmetrics` (30), `qt-platform` (15), `simspaceweaver` (14),
`lookoutvision` (13), `cloudshell` (4), `kiro` (2) or `sms` (2). There is no
call to make, and the collector's own service guard skips them.

**The API exposes no usable inventory (11 quotas, 6 services).**

| Service | Quotas | What the API gives instead |
| --- | ---: | --- |
| `cognito-sync` | 5 | `ListDatasets` needs an identity, so counting datasets per identity means enumerating every identity in every pool |
| `signin` | 2 | `ListResourcePermissionStatements` returns a statement's `sid` and `condition`, never the policy body the size quota bounds |
| `account-access` | 1 | `ListEntitlements` requires a mandatory filter naming a role, and no operation lists the roles |
| `codeguru-reviewer` | 1 | `Allowed Code Reviews` is an entitlement, not the count `ListCodeReviews` returns |
| `emr-serverless` | 1 | applications report their maximum capacity, never the vCPUs currently in use |
| `ssm-guiconnect` | 1 | the client has no listing operation at all |

`signer` left this list when the `Rate of <Operation> requests` wording became
an exclusion rule: all 19 of its quotas are request rates, so the service now
reports no measurable quota at all rather than nineteen unreachable ones.

## Largest remaining gaps

2,074 quotas are measurable and still uncovered. Sorting them by what their
names describe shows what the remaining work actually is:

| Shape | Quotas | What it would take |
| --- | ---: | --- |
| countable | 892 | the name describes a count; whether an API exposes that inventory has to be checked quota by quota |
| size or period | 722 | the bound applies to one payload, document or retention period, so there is a value to read only while a request is in flight |
| rate-shaped | 299 | a rate no exclusion rule matches, because the name states neither a window nor an operation |
| no SDK client | 148 | botocore ships no client for the service any more, so no inventory can be read until AWS restores one |
| organization-wide | 13 | the quota is counted over every account in the organization, which one account's credentials cannot see |

The countable ones are spread thin. The twelve largest holdings:

| Service | Catalog | Covered | Uncovered | Unmeasurable | Countable |
| --- | ---: | ---: | ---: | ---: | ---: |
| bedrock | 809 | 118 | 691 | 146 | 65 |
| connect | 361 | 37 | 324 | 283 | 35 |
| pinpoint | 132 | 10 | 122 | 52 | 31 |
| iotcore | 240 | 17 | 223 | 173 | 25 |
| iot | 179 | 24 | 155 | 112 | 17 |
| lambda | 70 | 13 | 57 | 28 | 16 |
| sagemaker | 1913 | 1819 | 94 | 77 | 16 |
| chime | 83 | 13 | 70 | 51 | 14 |
| deadline | 32 | 16 | 16 | 0 | 14 |
| forecast | 40 | 25 | 15 | 0 | 14 |
| kinesisvideo | 98 | 3 | 95 | 70 | 13 |
| quicksight | 24 | 4 | 20 | 0 | 13 |

The two tables above are generated by `quota_coverage.py --update-progress`;
`gap_shape` holds the rules that sort a name into a shape. "Countable"
classifies the name, not the reach of the API, and the largest holdings are all
blocked behind that distinction:

- **Bedrock (65)** is mostly per-model. `Model units per provisioned model for
  <model>` (25) and `Sum of in-progress and submitted batch inference jobs using
  a base model for <model>` (11 still open) each name a model in their display
  name only. Reaching them needs the fixed quota-code-to-model mapping
  `bedrock_batch.py` keeps, and that mapping can only be extended against AWS's
  own model list, never inferred from a display name. Everything Bedrock exposes
  without that resolution is now measured: provisioned throughput units, the
  knowledge-base ingestion jobs and the Automated Reasoning policy builds live
  in `bedrock_throughput.py`. Two of the remainder are blocked for their own
  reasons. `APIs per Agent` counts the operations in an action group's OpenAPI
  document, which `GetAgentActionGroup` returns either inline or as an S3
  pointer; reading only the inline half would report a confident undercount for
  every agent that stores its schema in a bucket. `(Model customization)
  Scheduled customization jobs` names a state `ListModelCustomizationJobs` does
  not have: its status filter offers InProgress, Completed, Failed, Stopping and
  Stopped, so any mapping to "scheduled" would be a guess.
- **Connect (35)** is workforce management: staffing groups, shift profiles,
  forecast groups, schedules and capacity plans. This SDK ships no operation
  for any of them; `connect` has no `list_staffing_groups`, `list_schedules` or
  equivalent.
- **Pinpoint (31)** is almost entirely per-request: attribute counts, template
  character counts and payload sizes that exist only while a call is in flight.

The `no SDK client` shape was split out of `countable` for the same reason.
Twelve services still appear in the Service Quotas catalog while botocore ships
no client for them under any name: AWS retired IoT Analytics, IoT Events, QLDB,
RoboMaker, Lookout for Metrics, Lookout for Vision, CloudWatch Evidently and
SimSpace Weaver, and has never published an API for CloudShell, Kiro, the Q
Developer transformation platform or Amazon Connect Decisions. Their 148 quotas
read as counts and had been ranked as the work to do next, which is how
lookoutmetrics and iotevents came to hold two of the twelve largest countable
gaps while being entirely unreachable. They are listed as a shape rather than
excluded as unmeasurable, because a restored API would make them countable
again overnight; `SDK_REMOVED` in `quota_coverage.py` holds the list and
`test_every_service_listed_as_dropped_really_has_no_client` fails the moment
botocore ships one of them again.

After those, no reachable service holds more than 26, so each further service is
a handful of quotas for a full traversal of its API. That is the shape of the
remaining work: broad rather than deep. The services the shape change promoted
into the table are not deeper than the ones it removed: Deadline Cloud's 14 need
a walk through every job in every queue, Forecast's 14 are dataset column and
row bounds, and the Kinesis Video, Chime SDK and Lambda holdings are concurrent
connection and call limits that exist only while traffic is in flight.

## Next investigations

- FIS has seven open quotas: two duration limits, three resources created internally by the cross-Region route-table action, completed-data retention, and the rolling seven-day DynamoDB action-minute limit. The resolved-target API exposes subnets but not the action's generated route, route-table or managed-prefix-list inventory; duration and rolling-window accounting need a source that cannot undercount elapsed or retained usage.
- Connect Cases: validate the new related-item and case-rule checks against populated live domains. The remaining catalog entries are per-second API rate/burst quotas whose token occupancy cannot be reconstructed from one-minute CloudWatch sums.
- CloudFormation: inspect hooks-per-resource and nested-module depth only if stored configuration exposes an exact scope. Stack-instance operation concurrency and import-operation input counts need stronger API evidence. Template checks currently cover deployed active stacks; templates stored outside CloudFormation are not observable through this collector.
- Rekognition: investigate classification/detection dataset accounting, stored-video job inventories and transitional quota reservations. The inference-unit metadata check still needs validation against a populated live project.
- Clean Rooms ML's eight remaining quotas: synthetic-data input rows/columns/category cardinality, synthetic MLIC generation concurrency, active audience exports per generation job, and the membership scope of configured model algorithms. Verify pending/cancelling training-instance reservations and populated live inventories separately from implementation availability.
- The EC2 catalog contains 1,526 token-bucket capacity/refill quotas, identified by their quota names. Exact bucket occupancy needs separate telemetry; these have not been marked covered by counting API calls over longer intervals.
- Bedrock model/token quotas and API rate quotas: identify exact telemetry and aggregation windows. Minute sums cannot establish per-second peaks or token-bucket occupancy.
- Bedrock batch jobs: verify quota reservation in transitional states and remaining model mappings (Claude Opus 5, MiniMax M2.5, NVIDIA Nemotron 3 Super 120B A12B). Input record/file quotas require a separate data-aware check.
- Bedrock configuration: verify node accounting inside Flow loops, Automated Reasoning build reservations and annotations, and Data Automation project blueprint/fallback accounting. Resolve any blueprint version `0` returned by populated inventories before assigning it a quota meaning. Verify evaluation transitions and populated live policy/version inventories separately from offline method availability.
- AgentCore remaining configuration limits: temporal policies, tools per target and policy-generation windows.
- Connect remaining limits: concurrent contacts via instance-scoped official metrics; data-table value/version semantics; agent-status accounting; additional queue configuration limits. Verify the new per-instance checks with live populated inventories where available.
- Verify ambiguous AppStream image-builder quota accounting and scaling transitions using stronger AWS evidence.
- Audit runtime success separately from implementation availability. Missing metrics, denied API calls and ambiguous resource states remain explicit.

## AWS utilization-report observation

The complete report contained CloudTrail `L-1568E18E`, Lambda `L-B99A9384`,
ElastiCache `L-80E085C7`, and DynamoDB `L-F98FE922`, `L-34F8CCC8`, `L-34F6A552`.
All six have compatible metrics in the local catalog. This is an account-specific
observation, not a limit on report coverage in other accounts.
AWS documents the asynchronous report in
[StartQuotaUtilizationReport](https://docs.aws.amazon.com/servicequotas/2019-06-24/apireference/API_StartQuotaUtilizationReport.html)
and [GetQuotaUtilizationReport](https://docs.aws.amazon.com/servicequotas/2019-06-24/apireference/API_GetQuotaUtilizationReport.html).

## Auditing what actually ran

A check that is structurally broken -- a wrong parameter, an operation the SDK
does not ship -- reports ERROR on every run rather than failing once. The
collector already records each failure in its `RUN#` item, but until now
nothing read them back, so a permanent failure was indistinguishable from a
throttle in the same log line.

`tests/test_check_smoke.py` catches that class before a deploy: it runs every
registered check against a response generated from botocore's own service
model and refuses any ERROR. What only shows up live -- denied permissions,
throttling, a Region where the service is not enabled -- is read afterwards
from an exported DynamoDB scan:

```sh
python scripts/coverage_inspector.py data/scan.json --view errors
python scripts/coverage_inspector.py data/scan.json --view persistent
```

`errors` groups the newest run per account and Region by `reason_group` and by
service. `persistent` lists only the quotas that failed in *every* recorded
run, which is the signature of a defect rather than bad luck.

Reproduce with:

```sh
python scripts/quota_coverage.py tests/fixtures/quota-catalog-union.json \
  --baseline tests/fixtures/coverage-baseline.json
python scripts/quota_orphans.py tests/fixtures/quota-catalog-union.json
python -m pytest -q
```
