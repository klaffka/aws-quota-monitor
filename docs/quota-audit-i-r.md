# Audit der offenen Quotas: Services I–R

Quelle: `data/service-quotas-20251102T133323Z.json` (lokaler Snapshot).
Berücksichtigt werden je Service und Quota-Code die noch nicht in der Registry registrierten Quotas. Doppelte Account-/Regional-Einträge des Snapshots werden zusammengeführt.
Jeder Eintrag erhält den konkreten Grund, aus dem er derzeit nicht sicher als Messwert erfasst werden kann. `RESOURCE_MAPPING` markiert Ressourcenbegriffe, für die die lokale Prüfung keine eindeutige API-/Quota-Zuordnung belegen konnte. `USAGE_METRIC` bedeutet, dass eine offizielle Nutzungsmetrik erforderlich wäre; `CONFIG_LIMIT` und `CONCURRENCY` sind keine Inventarzähler.

## `imagebuilder` (3 offene Quotas)

- `L-31E5726E` — **Image workflows per image** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-5E848392` — **Concurrent resource state update** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-BA4D191B` — **Concurrent builds** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.

## `inspector` (1 offene Quota)

- `L-6750F872` — **Instances in running assessments** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.

## `internetmonitor` (1 offene Quota)

- `L-4C7E946E` — **Days that health events are retained** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.

## `iot` (152 offene Quotas)

- `L-002E66AE` — **DescribeDimension API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-00511A32` — **Maximum connection rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-00E8EC16` — **Maximum number of query terms per query** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-014BF26E` — **ListTargetsForSecurityProfile API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-016FB677` — **ListScheduledAudits API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-01C40691` — **DescribeAccountAuditConfiguration API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-026DF298` — **Job execution roll out rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0321A666` — **ListAuditFindings API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-03D9A452` — **CancelAuditMitigationActionsTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-08C28D29` — **ListAuditMitigationActionsTasks API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-090EA78D` — **GetStatistics rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0A17A254` — **ListDimensions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0C3BA39D` — **CreateAuditSuppression API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-10F35433` — **ListJobExecutionsForThing throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-13A0BCCB` — **ListCommands throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-13B49C07` — **CancelDetectMitigationActionsTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-13B86658` — **DocumentSource length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-145287EF` — **DescribeMitigationAction API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-145FD0E6` — **ListJobs throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-146D20C5` — **DescribeAuditTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1CB31CD2` — **UpdateMitigationAction API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1F770514` — **DeleteCommand throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-211671C6` — **UpdateScheduledAudit API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2145354D` — **UpdateSecurityProfile API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-224318E9` — **CreateJobTemplate throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-22D1A126` — **Minimum job execution roll out rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-23B1CFB2` — **DescribeIndex rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-23F244D4` — **CreateJob throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2B367AAD` — **Storage duration for detect metrics** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-3123807D` — **Comment length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-32F19277` — **DescribeAuditMitigationActionsTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3470FAF6` — **JobTemplateId Length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-36FC3065` — **StatusDetail map value length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-382CCFC0` — **DescribeTunnel API throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3AA926CF` — **CancelAuditTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4026757A` — **ListStreams API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-42A0EE7E` — **DescribeScheduledAudit API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4627F3A5` — **GetPercentiles rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-465123DA` — **Maximum tunnel lifetime** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-46522656` — **PutVerificationStateOnViolation API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-46C255C8` — **DeleteJob throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-470BD798` — **StartCommandExecution throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-471C1537` — **StartOnDemandAuditTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-47ADF6AA` — **Maximum number of ? wildcard operators per query term** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-47B4076F` — **Maximum tag key length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-4832A12B` — **Maximum length of a custom field name** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-48D98BA3` — **GetThingConnectivityData rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4AB367B4` — **DeleteJobExecution throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4B5EBCAE` — **Minimum period of a fleet metric** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-4BB13F2B` — **DeleteStream API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4C86F053` — **CloseTunnel API throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4F362163` — **GetIndexingConfiguration rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-56E94C1D` — **ListViolationEvents API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5755407D` — **TagResource API throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-58D26E10` — **DeleteCommandExecution throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-59178860` — **ListJobTemplates throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-59F27FE9` — **UpdateStream API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5C712B10` — **DeleteMitigationAction API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5D01DB62` — **CancelJobExecution throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5F04543F` — **UpdateCommand throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-60251A2B` — **CreateScheduledAudit API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-609D00CE` — **DescribeJob throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-60A7ED34` — **ListTagsForResource API throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-62AE8B9D` — **DescribeJobExecution/GetPendingJobExecutions throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-62C55F58` — **ListMitigationActions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-632CA122` — **UpdateIndexingConfiguration rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-670D7C85` — **StartDetectMitigationActionsTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-68091094` — **GetCommandExecution throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6891CC02` — **ListActiveViolations API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-68A50D88` — **UpdateDimension API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6A19A60F` — **DescribeAuditFinding API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6A50FCE7` — **ListOTAUpdates API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6A6494DD` — **In Progress timeout** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6D2A593E` — **Maximum bandwidth per tunnel** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6F3753D8` — **DescribeCustomMetric API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-717A207E` — **Step Timer** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-7365ADF8` — **UpdateJob throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-74CF42C0` — **GetOTAUpdate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-786CEEF0` — **List results per page** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-7BF41710` — **Device metric minimum delay** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-7C0B717A` — **DeleteScheduledAudit API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7C5B0274` — **S3 job document length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-81189B2F` — **StartAuditMitigationActionsTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-85B5C2FD` — **StatusDetail map key length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-86E241A6` — **CreateStream API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-86FC5D66` — **GetJobDocument throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-88D87918` — **ValidateSecurityProfileBehaviors API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8AEAB7FE` — **DescribeSecurityProfile API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8D3E8509` — **ListDetectMitigationActionsExecutions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-908D0FBE` — **SearchIndex rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-90F8C878` — **Maximum number of query terms per dynamic group** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-9227E25C` — **ListAuditSuppressions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9299DD15` — **ListSecurityProfilesForTarget API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-94973834` — **Job description length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-95D5D7AB` — **StatusDetail map key-value pairs** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-99780C4B` — **DeleteJobTemplate throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9AE67DFC` — **Device metric peak reporting rate for an account** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9CCB5F90` — **ListJobExecutionsForJob throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A2577F1F` — **CreateSecurityProfile API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A6ABB02F` — **DeleteSecurityProfile API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A7724468` — **GetCommand throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-ABC0EA56` — **UpdateCustomMetric API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AD4AFD1C` — **Retention period for command executions** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-ADA44585` — **DescribeAuditSuppression API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AE161BC5` — **CreateCommand throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B359270D` — **GetCardinality rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B475FD53` — **Data retention** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B68A9868` — **File size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B731A266` — **DescribeJobExecution throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B78A9E08` — **ListAuditTasks API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B7CAF86D` — **ListTunnels API throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B8CB01EA` — **Maximum tag value length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-BF877B05` — **UntagResource API trottle limit** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-C002DA39` — **DeleteDimension API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C0894219` — **ListIndices rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C3993A6F` — **Maximum length of a query** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-C6AA7145` — **DeleteAccountAuditConfiguration API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C6D7A02D` — **ListAuditMitigationActionsExecutions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C8D2DE05` — **Storage duration for detect violations** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-C8F5F7B3` — **StartNextPendingJobExecution/UpdateJobExecution throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CA8BDEFC` — **UpdateAuditSuppression API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CCBF5835` — **ListCommandExecutions throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CD7FC91A` — **DeleteCustomMetric API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CE4D15EC` — **Maximum number of tags per resource** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-CEAD881C` — **Job Template description length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-CF4F23BC` — **DetachSecurityProfile API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D18738F6` — **ListDetectMitigationActionsTasks API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D3020048` — **DescribeJobTemplate throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D45EEF28` — **ListCustomMetrics API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D7A534B0` — **AssociateTargetsWithJob throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D92F6C41` — **Maximum number of * wildcard operators per query term** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-DACF0EDE` — **ListSecurityProfiles API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DC1637B1` — **ListMetricValues API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DCAEF14C` — **DescribeDetectMitigationActionsTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DEC656C5` — **CancelJob throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E41D2F60` — **JobId Length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-E68D12E6` — **CreateCustomMetric API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E70CF14E` — **DeleteAuditSuppression API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E72C1C85` — **OpenTunnel API throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E9111144` — **AttachSecurityProfile API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EC6F1940` — **Minimum pre-signed URL lifetime** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-EFA916AE` — **CreateMitigationAction API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EFEC7F9B` — **CreateOTAUpdate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F0C81A68` — **UpdateCommandExecution throttle limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F288A443` — **DescribeStream API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F5608FF9` — **Storage duration for audit findings** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-F62705AB` — **UpdateAccountAuditConfiguration API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F69C5695` — **Commands execution timeout** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-F7BC9359` — **Maximum number of query terms per fleet metric** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-FBBB476F` — **Pre-signed URL lifetime** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-FC067223` — **Maximum period of a fleet metric** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-FCC8A955` — **DeleteOTAUpdate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `iotanalytics` (15 offene Quotas)

- `L-41F5CE82` — **Number of Parquet SchemaDefinition columns** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-546EC585` — **Rate of CreateDatasetContent requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-59E2DC0E` — **Batch size of BatchPutMessage messages** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-5CD4F96D` — **Minimum data set refresh interval** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6AE7A88C` — **Concurrent container dataset runs** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-8363A0C2` — **Activities per pipeline** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-94D1C11F` — **Container datasets triggered per SQL data set** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-9514024B` — **Concurrent data set content generation** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-A9F757CF` — **Size of BatchPutMessage messages** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B7F65767` — **Depth of Parquet SchemaDefinition column** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-BA86816F` — **Number of partitions in a data store** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-C24E823A` — **Rate of SampleChannelData requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C770541D` — **Rate of RunPipelineActivity requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CFCA90F1` — **Rate of BatchPutMessage messages** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EFB6780D` — **Number of StartPipelineReprocessing requests** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `iotcore` (216 offene Quotas)

- `L-00ACEBE9` — **ListThingPrincipalsV2 API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-01BCDDCA` — **CreateCertificateFromCsr API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-033DE216` — **Connect requests per second per client ID** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-037A5A45` — **Maximum MQTT5 Content Type size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-066C37B5` — **DeleteProvisioningTemplate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-06D0B96B` — **UpdateCertificateMode API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-06E76376` — **TagResource API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-073010AA` — **ListPolicyPrincipals API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-083F3861` — **Publish requests per second per connection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0AA974E3` — **ListRetainedMessages API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0D3E2C36` — **DisableTopicRule API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0DD80F19` — **Maximum outbound unacknowledged QoS 1 publish requests** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-0DF9E6AC` — **CreateProvisioningTemplate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0EF0F5EE` — **DescribeThing API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1243AB32` — **GetRetainedMessage API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-129466FE` — **ListPrincipalPolicies API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-13573643` — **MQTT payload size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-136C6B71` — **AcceptCertificateTransfer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-137EE1A7` — **SetV2LoggingOptions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-14E3C32E` — **CancelCertificateTransfer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-15185D92` — **ListCACertificates API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-16C54232` — **DeleteTopicRuleDestination API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-19FEFCAA` — **DescribeAuthorizer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1B2EEF52` — **CreatePolicy API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1E5260D6` — **ListThingGroups API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1F4BE39E` — **AddThingToBillingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1FD03A8A` — **UpdateProvisioningTemplate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1FE17093` — **GetPolicyVersion API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-211F680E` — **UpdateThing API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-220198EC` — **Maximum number of provisioning claims that can be generated per second by trusted user** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-22E81A4A` — **DeleteRoleAlias API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-23DF46E7` — **DescribeBillingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-23F45906` — **Maximum number of in-flight, unacknowledged messages per thing** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-24EAC95F` — **EnableTopicRule API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-261C415C` — **DescribeProvisioningTemplate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2904683A` — **AddThingToThingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2990EF9F` — **DeletePolicyVersion API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2A7BC612` — **Maximum depth of JSON device state documents** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-2A81A394` — **RemoveThingFromThingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2B86A5A0` — **ListPolicies API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2BF8F5C1` — **DeleteV2LoggingLevel API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-307251B7` — **DeleteProvisioningTemplateVersion API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3084D098` — **GetV2LoggingOptions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-31D9CC26` — **TestAuthorization API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-33A2AE15` — **CreateProvisioningClaim API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-35130141` — **DescribeProvisioningTemplateVersion API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-35DA9240` — **Queued messages per second per account** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-3964F400` — **Maximum number of thing attributes for a thing with a thing type** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-39DBF618` — **TestInvokeAuthorizer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3B9C1B78` — **Maximum size of fleet provisioning template** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-3BB07D58` — **Maximum thing group name size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-3BB6AFBC` — **Persistent session expiry period** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-3F401592` — **WebSocket connection duration** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-407F7533` — **GetLoggingOptions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-40B55430` — **CreateKeysAndCertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-447FFBFB` — **UpdateRoleAlias API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-45957C13` — **Subscriptions per connection** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-4671C7C8` — **RegisterCertificateWithoutCA API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4673EACA` — **DescribeThingRegistrationTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4B33E451` — **Inbound publish requests per second per account** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4BDBE56D` — **ListDomainConfigurations API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4F16A45D` — **SetDefaultPolicyVersion API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4FB8C075` — **Rule payload size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-5104A2FD` — **Size of thing attributes per thing** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-512F449C` — **CreateThingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-51C95546` — **SetDefaultAuthorizer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-51D1E673` — **ListThingRegistrationTaskReports API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-52CBB99B` — **Subscriptions per account** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-52E1E197` — **DescribeThingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-53E8A280` — **ListProvisioningTemplates API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-56AB20B6` — **ListOutgoingCertificates API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-57AAC135` — **ListThings API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-58129C66` — **DeletePolicy API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-589D5E1D` — **Subscriptions per second per account** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-5A0AFD83` — **ListCertificatesByCA API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5BDDC7FE` — **ClearDefaultAuthorizer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5C386551` — **Queued Messages per shared subscription group** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-5CE9072D` — **GetPolicy API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5D84F9FE` — **UpdateThingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5E9B88DA` — **Rule evaluations per second per AWS account** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-6355B513` — **UpdateAuthorizer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-638916DB` — **UpdateThingGroupsForThing API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-64BE4C6D` — **Minimum MQTT5 maximum packet size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-64CBACAC` — **CreateThing API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-675FC798` — **Maximum retry interval for delivering QoS 1 messages** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6C20C764` — **DeleteBillingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6CC6395A` — **Device Shadow API requests/second per account** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-7027E8DD` — **DescribeDomainConfiguration API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-719363F9` — **UpdateEncryptionConfiguration API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7201B389` — **Maximum User Properties total size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-724130CC` — **Maximum shadow name size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-7278F198` — **StartThingRegistrationTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-757705D9` — **Subscribe and unsubscribe requests per second per group** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-75CAB723` — **Maximum concurrent client connections per account** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-75F129AD` — **ListThingGroupsForThing API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-771FD74A` — **Retained message inbound publish requests per second per topic** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-77B523DC` — **UpdateCertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-78413E12` — **Maximum MQTT5 packet size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-79328B0C` — **SetLoggingOptions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7C43D13A` — **CreateProvisioningTemplateVersion API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7D0B47D6` — **Number of thing types that can be associated with a thing** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-7E0F5745` — **CreateDynamicThingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7E496DB6` — **DescribeCertificateTag API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7E9783FF` — **Maximum MQTT5 Correlation Data size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-7F1DBFAE` — **DeprecateThingType API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-80CBA176` — **ListProvisioningTemplateVersions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-81689EEF` — **AttachPrincipalPolicy API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-82706932` — **DescribeRoleAlias API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-83161BB8` — **Fleet Provisioning CreateCertificateFromCsr MQTT API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-83705EE2` — **GetRegistrationCode API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-83BC2FA9` — **Maximum thing name size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-850876C0` — **Shared Subscription groups per account** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-860C3E36` — **ListTopicRules API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8650816F` — **CreateThingType API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-866D6FAF` — **CreateAuthorizer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8736D8E0` — **Maximum inbound unacknowledged QoS 1 publish requests** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-889800F7` — **DeleteThing API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-88CA286A` — **UpdateBillingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8996ACA8` — **UntagResource API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8B5FA95E` — **Data retention policy** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-8C0011A3` — **RegisterCertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-927E0A91` — **HTTP Action: Maximum size of a header key** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-9410BF75` — **CreateDomainConfiguration API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-944099F0` — **DeleteCACertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-945D2414` — **Maximum number of thing attributes for a thing without a thing type** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-97D120C3` — **Registration task termination** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-97DA2C60` — **ListCertificates API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9A4156D0` — **TransferCertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9BF00264` — **ListAuthorizers API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9C512C33` — **UpdateEventConfigurations API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9DF61146` — **DeleteDynamicThingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A20A8794` — **DetachPrincipalPolicy API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A26060BE` — **Maximum number of CA certificates with the same subject field allowed per AWS account per Region** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-A295A064` — **Maximum size of a JSON state document** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-A34ABBD3` — **DescribeDefaultAuthorizer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A6574E9E` — **Maximum subscriptions per subscribe request** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-A755E860` — **UpdateCACertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A9BD0A45` — **DescribeEncryptionConfiguration API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AA03977E` — **UpdateThingType API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AB8384AA` — **Maximum size of a thing group attribute name, in chars** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-AC832B8A` — **DescribeEventConfigurations API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AD5A8D4F` — **Maximum number of slashes in topic and topic filter** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-AEA1E176` — **Connect requests per second per account** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AF06EF1C` — **Maximum size of a thing group attribute value, in chars** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B2BBBD8C` — **Fleet Provisioning RegisterThing MQTT API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B2CCE1DE` — **ListThingRegistrationTasks API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B2DA2A45` — **ListAttachedPolicies API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B3AC62F0` — **RegisterCACertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B5EE4A16` — **DetachThingPrincipal API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B6E73822` — **HTTP Action: Maximum length of an endpoint URL** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B6E97F34` — **DeleteAuthorizer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B8E3A42A` — **DeleteTopicRule API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B9586B46` — **UpdateCertificateTag API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BAFC6221` — **Retained message inbound publish requests per second per account** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BB923BC2` — **ListBillingGroups API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BBB14FFD` — **CreateTopicRuleDestination API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BD4A365E` — **CreatePolicyVersion API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BD70FE3A` — **Maximum Message Expiry Interval** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-BD9799A6` — **UpdateTopicRuleDestination API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BF6AC917` — **SetV2LoggingLevel API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C0B2EF8B` — **RegisterThing API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C0EA6C17` — **Maximum MQTT5 Topic Alias value** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-C12BBB7E` — **Maximum number of thing groups a thing can belong to** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-C481616A` — **ListPrincipalThings API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CA7D4E3E` — **AttachPolicy API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CAFFCA46` — **Fleet Provisioning CreateKeysAndCertificate MQTT API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CE45290D` — **GetEffectivePolicies API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CFBDB489` — **DeleteThingType API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CFF04779` — **ListTopicRuleDestinations API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D12550DB` — **ReplaceTopicRule API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D127B7BE` — **ListTagsForResource API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D33FD5F9` — **ListThingsInThingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D4CA1ECC` — **Maximum line length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D5D09DC2` — **DeleteRegistrationCode API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D624FA43` — **UpdateDomainConfiguration API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D74B77D3` — **ListV2LoggingLevels API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D7C50543` — **ListTargetsForPolicy API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D9543C11` — **ListCertificateProviders API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D9B73671` — **Maximum policy document size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D9C66F9D` — **Throughput per second per connection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DA868E55` — **AssumeRoleWithCertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DADCC3DA` — **StopThingRegistrationTask API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DDCF8E97` — **DescribeThingType API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E06BBD5F` — **UpdateDynamicThingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E2D9C89C` — **Client ID size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-E67DF416` — **ListPolicyVersions API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E694C311` — **DeleteCertificateProvider API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E72BB356` — **DescribeCACertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E77027EF` — **Connection inactivity (keep-alive interval)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-E817179B` — **CreateTopicRule API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E82C8FBF` — **RejectCertificateTransfer API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E8797DCC` — **ListThingsInBillingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E892E94A` — **CreateRoleAlias API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E99F934A` — **GetTopicRuleDestination API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EB813241` — **Shared Subscriptions per group** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-EBD13534` — **UpdateCertificateProvider API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EC88D510` — **DetachPolicy API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-ECD9BEEF` — **Topic size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-ED45A70B` — **ListPrincipalThingsV2 API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EE822245` — **DescribeCertificateProvider API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EEB8F0B1` — **DeleteCertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EF53B0E4` — **GetTopicRule API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EF8DF306` — **CreateCertificateProvider API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EFF4BE08` — **Requests per second per thing** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F22E433B` — **ListRoleAliases API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F2D09BC8` — **CreateBillingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F30831DF` — **DescribeEndpoint API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F64D1AA6` — **AttachThingPrincipal API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F9709CF8` — **HTTP Action: Request timeout** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-F9EBF527` — **ListThingTypes API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FAF5733F` — **RemoveThingFromBillingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FBA96CAB` — **DeleteDomainConfiguration API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FC3EF4D9` — **ListThingPrincipals API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FC864907` — **DescribeCertificate API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FCAB1AF4` — **DeleteThingGroup API TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FE4EDCF9` — **Outbound publish requests per second per account** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `iotevents` (25 offene Quotas)

- `L-0B548925` — **States per detector model** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-17157277` — **Detector models per input** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-18935129` — **Number of detector model analyses in RUNNING status** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-1B3BA3EE` — **Detector model versions** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-1EE1AE32` — **Message size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-27919AE8` — **Detector model definition size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-279A67DA` — **Detector models** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-2FA8EFB5` — **Maximum alarm model versions per alarm model** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-3ED590C1` — **Detectors per detector model** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-41C77D73` — **Maximum total messages evaluated per second** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-46EA5101` — **State variables per detector model definition** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-4E41133E` — **Maximum actions per event** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-52F0DBB4` — **Maximum alarms per alarm model** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-7F0B14C2` — **Messages per detector per second** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-89B1F2C1` — **Timers scheduled per detector** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-BE1D061A` — **Trigger expressions** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-C031B6B8` — **Inputs** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-C0F716CA` — **Maximum events per state** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-C4A5E0B8` — **Maximum messages per alarm per second** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-D86BAB00` — **Minimum timer duration** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-DE2C2CBE` — **Maximum number of recipients per notification action in an alarm model** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-EB687A61` — **Maximum actions per alarm model** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-EBDD79FD` — **Maximum number of alarm models per property in an AWS IoT SiteWise asset model** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-F7E2E007` — **Maximum alarm models per input** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-FCDB3431` — **Maximum transition events per state** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `iotfleetwise` (5 offene Quotas)

- `L-03C735B1` — **Number of state templates for each vehicle in an AWS Region.** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-463B5628` — **Maximum size of a message** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6ED070A2` — **Rate of API requests for each account in an AWS Region** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B91464DC` — **Rate of ingesting messages for each account in an AWS Region.** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FDD53FA4` — **Rate of ingesting messages for each vehicle in an AWS Region.** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `iotsitewise` (64 offene Quotas)

- `L-055D0253` — **Rate of data points ingested** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0B4FE3AE` — **Request rate for DeleteTimeSeries** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0E1DA1E4` — **Request rate for ListCompositionRelationships** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0ED7CAC0` — **Request rate for UpdateAssetProperty** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-11052945` — **Request rate for UntagResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-18D6B079` — **Number of unique data streams in a single data bulk import job file** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-19AC6080` — **Number of OPC UA sources per gateway** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-1A4574EB` — **Request rate for DeleteAsset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1AC5759B` — **Request rate for ListAssetModelCompositeModels** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1DAFF3FA` — **Request rate for PutStorageConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1F08A062` — **Request rate for BatchGetAssetPropertyAggregates** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-27B1043C` — **Rate of GetInterpolatedAssetPropertyValues requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2AA24120` — **Size of the CSV file for Adaptive Ingestion** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-2C0E5B73` — **Number of metrics per dashboard visualization** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-2E6A6BE6` — **Request rate for ListAssetModels** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-30ACF5DC` — **Request rate for DescribeAssetModel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-36098D32` — **Request rate for GetAssetPropertyAggregates** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3B5A6523` — **Number of data points per second per data quality per asset property** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-47E0AE04` — **Number of properties that depend on a single property within enforced asset model** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-493A14B3` — **Rate of GetAssetPropertyValue request and BatchGetAssetPropertyValue entry queries per asset property** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4C7927F2` — **Request rate for PutDefaultEncryptionConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5570DDB2` — **Size of the uncompressed parquet row group** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-5ABA0B04` — **Request rate for UpdateAsset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5FBB9338` — **Number of properties that depend on a single property** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-6A0446E9` — **Request rate for BatchGetAssetPropertyValue** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6A07E983` — **Request rate for CreateAssetModelCompositeModel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6BA71B50` — **Request rate for BatchGetAssetPropertyValueHistory** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-71344A05` — **Request rate for DescribeLoggingOptions** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-76DAFFD4` — **Request rate for CreateAssetModel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8833D569` — **Request rate for DisassociateAssets** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-90092B39` — **Rate of BatchPutAssetPropertyValue entries ingested per asset property** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-92FDA60B` — **Size of the uncompressed parquet file** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-95E7BD97` — **Number of visualizations per dashboard** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-97DCC2B9` — **Request rate for TagResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-99ECDFE8` — **Request rate for DescribeTimeSeries** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9AB54A74` — **Request rate for DescribeDefaultEncryptionConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A2DC172E` — **Request rate for UpdateAssetModel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A52C4EC3` — **Request rate for BatchPutAssetPropertyValue** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A6B45284` — **Rate of datapoints retrieved from GetAssetPropertyValueHistory and BatchGetAssetPropertyValueHistory** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A6CC6143` — **Request rate for AssociateAssets** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A8F3779C` — **Rate of GetAssetPropertyValueHistory request and BatchGetAssetPropertyValueHistory entry queries per asset property** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A9C0553C` — **Request rate for PutLoggingOptions** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AD488EF9` — **Request rate for DisassociateTimeSeriesFromAssetProperty** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-ADBE6DE2` — **Number of days between the timestamp in the past and today for Adaptive Ingestion in Bulk Import Job API** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-C65D47B0` — **Request rate for ListTagsForResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C866EFAE` — **Request rate for DeleteAssetModelCompositeModel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C95674C2` — **Request rate for DescribeAssetCompositeModel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CDF30604` — **Request rate for GetAssetPropertyValue** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CDFB770E` — **Number of properties that directly depend on a single property** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-D1C7039E` — **Request rate for ListAssetRelationships** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D7745D01` — **Request rate for GetAssetPropertyValueHistory** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DABC3942` — **Number of results per GetInterpolatedAssetPropertyValues request** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-DDBB1C6A` — **Rate of GetAssetPropertyAggregates request and BatchGetAssetPropertyAggregates entry queries per asset property** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DF999358` — **Request rate for ListAssociatedAssets** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DFA2B5CE` — **Request rate for DescribeStorageConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E824E02D` — **Request rate for DeleteAssetModel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EC3E9870` — **Request rate for DescribeAsset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EF35D760` — **Request rate for UpdateAssetModelCompositeModel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EFD4443A` — **Request rate for ListTimeSeries** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FAC80CD0` — **Request rate for CreateAsset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FC916B9F` — **Request rate for AssociateTimeSeriesToAssetProperty** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FD327B60` — **Request rate for ListAssets** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FE40635A` — **Request rate for DescribeAssetProperty** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FF65FBE9` — **Request rate for DescribeAssetModelCompositeModel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `iottwinmaker` (12 offene Quotas)

- `L-019A0AE4` — **Depth of entity hierarchy** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-09F67DF4` — **Size of the metadata transfer job import file** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-2064CF20` — **Number of SiteWise export resources per job** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-43909161` — **Number of TwinMaker export resources per job** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-56552C16` — **Number of SiteWise import resources per job** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-62EFDD1A` — **Component type composition tree size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6A666826` — **Tags per resource** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-6B0BA854` — **Component type composition tree depth** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-8537DB8F` — **Number of TwinMaker import resources per job** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-C511254B` — **Depth of component type hierarchy** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-F123ACD6` — **Number of metadata transfer jobs in queue** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-FE672086` — **Components per entity** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `iotwireless` (100 offene Quotas)

- `L-0253A672` — **TPS limit for GetMetrics** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-05BE3C0D` — **TPS limit for CreateWirelessGatewayTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0604C085` — **TPS limit for ListFuotaTasks** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0641E5DC` — **TPS limit for CreateDestination** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0C3B538C` — **TPS limit for GetWirelessGatewayFirmwareInformation** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0C83FCE2` — **TPS limit for DisassociateWirelessDeviceFromFuotaTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0D8E249D` — **TPS limit for UpdateLogLevelsByResourceTypes** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0E4BA92F` — **TPS limit for SendDataToWirelessDevice** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0F5F17D1` — **TPS limit for ListNetworkAnalyzerConfigurations** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-12D6182B` — **TPS limit for PutResourceLogLevel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1346D5EC` — **TPS limit for SendDataToMulticastGroup** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-13F3B5DD` — **TPS limit for GetServiceEndpoint** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-182F8619` — **TPS limit for DeleteWirelessGatewayTaskDefinition** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-189593ED` — **TPS limit for UpdateMetricConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1DF3438B` — **TPS limit for DisassociateWirelessDeviceFromMulticastGroup** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2639F0B0` — **TPS limit for GetWirelessDevice** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3103F50C` — **TPS limit for GetWirelessGatewayStatistics** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-33206197` — **TPS limit for DisassociateWirelessGatewayFromThing** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-334EA895` — **TPS limit for GetWirelessGatewayTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-35D1818B` — **TPS limit for ListWirelessDevices** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3B5AF547` — **TPS limit for CreateWirelessDevice** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-42B55186` — **TPS limit for GetWirelessGateway** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4915A563` — **TPS limit for AssociateWirelessGatewayWithCertificate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4951240E` — **TPS limit for DisassociateWirelessDeviceFromThing** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4AC6BBEA` — **TPS limit for AssociateWirelessDeviceWithFuotaTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4DEB3C3F` — **TPS limit for ListMulticastGroups** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4F7C7CD3` — **TPS limit for DeleteNetworkAnalyzerConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4FCAEFF0` — **TPS limit for GetDeviceProfile** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-50B185BA` — **TPS limit for DeleteDeviceProfile** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5369BF7E` — **TPS limit for UpdateFuotaTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5FCBB48D` — **TPS limit for GetPositionConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6175FC12` — **TPS limit for GetResourceLogLevel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-61A27891` — **TPS limit for DisassociateMulticastGroupFromFuotaTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6407631C` — **TPS limit for AssociateWirelessDeviceWithThing** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-647D6C46` — **TPS limit for ListServiceProfiles** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6796B05C` — **TPS limit for CreateNetworkAnalyzerConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6829C2D4` — **TPS limit for CreateDeviceProfile** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6AF47E8B` — **TPS limit for GetNetworkAnalyzerConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6DEF44D2` — **TPS limit for DeleteWirelessGateway** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6FC5E39D` — **TPS limit for StartMulticastGroupSession** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-70D824D9` — **TPS limit for UpdateResourceEventConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-72A5D5E0` — **TPS limit for GetMulticastGroup** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-72AB9EAE` — **TPS limit for CancelMulticastGroupSession** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7AF1469B` — **TPS limit for GetWirelessGatewayTaskDefinition** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7CE08A6C` — **TPS limit for ListMulticastGroupsByFuotaTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8007AA14` — **TPS limit for GetMetricConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-81B64868` — **TPS limit for GetWirelessGatewayCertificate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8367137B` — **TPS limit for UpdateNetworkAnalyzerConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-882084A6` — **TPS limit for UpdateEventConfigurationByResourceTypes** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-89C556FB` — **TPS limit for DeleteFuotaTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8DBB3861` — **TPS limit for StartBulkDisassociateWirelessDeviceFromMulticastGroup** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8E7EAF51` — **TPS limit for GetDestination** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8E864D54` — **TPS limit for UpdateMulticastGroup** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8FFCC81A` — **TPS limit for CreateWirelessGatewayTaskDefinition** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-905ED905` — **TPS limit for GetServiceProfile** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-907EFF6F` — **TPS limit for DisassociateWirelessGatewayFromCertificate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-92ECAB75` — **TPS limit for AssociateWirelessDeviceWithMulticastGroup** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-93C5A1DB` — **TPS limit for DeleteMulticastGroup** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-96FA888E` — **TPS limit for ResetAllResourceLogLevels** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9C8C92B3` — **TPS limit for GetMulticastGroupSession** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9CF47CC5` — **TPS limit for ResetResourceLogLevel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9D5A90BD` — **TPS limit for TagResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9E25CA04` — **TPS limit for StartNetworkAnalyzerStream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A1F96616` — **TPS limit for UpdateWirelessGateway** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A2058506` — **TPS limit for ListEventConfigurations** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A25EC315` — **TPS limit for DeleteServiceProfile** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A4CD53FD` — **TPS limit for PutPositionConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A755236A` — **TPS limit for DeleteWirelessDevice** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AA413BB8` — **TPS limit for UpdateDestination** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B0F3D444` — **TPS limit for DeleteWirelessGatewayTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B29C7ECC` — **TPS limit for AssociateWirelessGatewayWithThing** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B4636E40` — **TPS limit for UpdateWirelessDevice** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B6937DF9` — **TPS limit for DeleteQueuedMessages** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B8A41F6F` — **TPS limit for GetPosition** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C2175B1E` — **TPS limit for GetLogLevelsByResourceTypes** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C2F6FC68` — **TPS limit for CreateWirelessGateway** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C80BC655` — **TPS limit for UpdatePosition** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CC2D61C3` — **TPS limit for ListWirelessGatewayTaskDefinitions** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CCEFD4AF` — **TPS limit for GetWirelessDeviceStatistics** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D07E0E7A` — **TPS limit for CreateMulticastGroup** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D33E220F` — **TPS limit for GetFuotaTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D6B79324` — **TPS limit for GetPositionEstimate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D91B7067` — **TPS limit for ListQueuedMessages** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DB770805` — **TPS limit for StartFuotaTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DEC8385B` — **TPS limit for ListTagsForResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DF869DBB` — **TPS limit for UntagResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E01F1EA2` — **TPS limit for UpdateResourcePosition** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E3C6A79E` — **TPS limit for CreateFuotaTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E4F0512E` — **TPS limit for GetResourceEventConfiguration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E54A2621` — **TPS limit for ListDestinations** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E6CBA335` — **TPS limit for ListDeviceProfiles** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E91B60DF` — **TPS limit for AssociateMulticastGroupWithFuotaTask** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EB538AAC` — **TPS limit for DeleteDestination** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F4D43AC0` — **TPS limit for ListPositionConfigurations** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F654617D` — **TPS limit for GetResourcePosition** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F8530DBD` — **TPS limit for CreateServiceProfile** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F881E3D9` — **TPS limit for ListWirelessGateways** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F930F6AD` — **TPS limit for StartBulkAssociateWirelessDeviceWithMulticastGroup** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FAE31118` — **TPS limit for GetEventConfigurationByResourceTypes** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FC84B266` — **TPS limit for TestWirelessDevice** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `ivs` (13 offene Quotas)

- `L-160C013D` — **Stage participants (subscribers)** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-25CC60E6` — **Max Composition duration** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-3B5D0A1C` — **Ingest bitrate (channel type BASIC)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-41152BE7` — **Stream takeovers** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-4189D9D0` — **PutMetadata rate per channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-77A18D5D` — **Concurrent views** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-832F442C` — **Ingest bitrate (channel type STANDARD)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8D348609` — **Metadata payload** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-8E5617D4` — **Concurrent replication per participant** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-B33A5A4F` — **Concurrent publishers** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-BE74979C` — **Playback token size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-E9691DAB` — **Concurrent subscriptions** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-FD1EB8A7` — **Concurrent streams** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.

## `ivschat` (7 offene Quotas)

- `L-0CF8D910` — **Rate of DisconnectUser requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-12580D29` — **Message review handler timeout period** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-2D7A45DA` — **Concurrent chat connections** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-766F0845` — **Rate of DeleteMessage requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B11841BF` — **Rate of SendMessage requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B96AB553` — **Rate of messaging requests per connection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F87B0F22` — **Logging Configurations** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `kafka` (2 offene Quotas)

- `L-03FD6822` — **Number of brokers per KRaft cluster** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-FAB9E493` — **Number of brokers per cluster** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `kafkaconnect` (2 offene Quotas)

- `L-5BED8C47` — **Maximum worker configurations** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-C78B0952` — **Maximum connect workers** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `kinesisanalytics` (3 offene Quotas)

- `L-3A88E041` — **Apache Flink Kinesis Processing Units (KPUs)** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-59171AE6` — **Input Parallelism in input streams for SQL applications** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-90BEDB9D` — **SQL Kinesis Processing Units (KPUs)** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `kinesisvideo` (95 offene Quotas)

- `L-004D0B56` — **Rate of GetDASHManifestPlaylistAPI requests per session** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-007A0A1E` — **Rate of UpdateStreamAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-00B1F645` — **Rate of UpdateSignalingChannelAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-00CBFFF8` — **GetClip fragments** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-031A11B8` — **Rate of GetHLSMasterPlaylistAPI requests per session** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0528E1BD` — **ConnectAsViewer idle connection timeout** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-07A0DA4B` — **Rate of DescribeStreamAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-08A947EC` — **Rate of GetTSFragmentAPI requests per session** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-08EC4D9E` — **PutMedia concurrent connections per stream** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-08F65F09` — **Rate of CreateStreamAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0AB4413A` — **Rate of GetDataEndpointAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0F2DD60B` — **Rate of DescribeMediaStorageConfigurationAPI requests per resource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1190DACE` — **Rate of UpdateSignalingChannelAPI requests per signaling channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-12CD9A60` — **Rate of ListEdgeAgentConfigurationsAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-18022F70` — **Rate of StartEdgeConfigurationUpdateAPI requests per resource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-18823A76` — **Rate of DeleteStreamAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1A34128A` — **Rate of archived fragment media per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1D1B9375` — **Rate of StartEdgeConfigurationUpdateAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1FE8DF31` — **ConnectAsMaster GO_AWAY message grace period** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-2087401F` — **Rate of GetDASHStreamingSessionURLAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2C56AD83` — **PutMedia minimum fragment duration** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-2FC7D6B2` — **GetMediaForFragmentList bandwidth** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-32D5DC79` — **Rate of CreateSignalingChannelAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-33EBA7A5` — **ConnectAsMaster connection duration** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-354AF9F0` — **PutMedia bandwidth** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-35D8C370` — **Rate of GetSignalingChannelEndpointAPI requests per signaling channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-38A739F2` — **Rate of SendSDPAnswerAPI requests per websocket connection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3DF8FB52` — **Rate of ConnectAsViewerAPI requests per signaling channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3E968CB6` — **SendSDPOffer message payload size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-409E30B3` — **Rate of UntagStreamAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4450B3B7` — **Rate of ListTagsForStreamAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4E1944F3` — **Rate of UntagStreamAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4F4BE4AA` — **Rate of archived fragment metadata per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-54F8D7FD` — **Rate of UpdateMediaStorageConfigurationAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-56782C84` — **Rate of DescribeEdgeConfigurationAPI requests per resource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-577474A7` — **Rate of DeleteEdgeConfigurationAPI requests per resource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-65A25202` — **Rate of ConnectAsMasterAPI requests per signaling channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-66B2FAAB` — **Rate of ListSignalingChannelsAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6A7E955C` — **Rate of GetICEServerConfigAPI requests per signaling channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6C5E79A7` — **Rate of UpdateDataRetentionAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6F5F7717` — **PutMedia fragment size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6F95545E` — **Rate of DescribeMappedResourceConfigurationAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-782F9031` — **Rate of SendAlexaOfferToMasterAPI requests per signaling channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7D08463B` — **Rate of GetMP4MediaFragmentAPI requests per session** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-84C54DF4` — **Rate of TagResourceAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-85B46D1C` — **Rate of SendICECandidateAPI requests per websocket connection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-87FBA326` — **GetDASHManifestPlaylist fragments** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-885A87A1` — **Rate of GetMediaAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8F38419A` — **Rate of TagStreamAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8F974349` — **ConnectAsViewer connections per signaling channel** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-912086DE` — **ConnectAsViewer GO_AWAY message grace period** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-99F327D1` — **Rate of DescribeSignalingChannelAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9A1B0418` — **Rate of DescribeSignalingChannelAPI requests per signaling channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9FD64640` — **Rate of DescribeEdgeConfigurationAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A0781139` — **Rate of GetSignalingChannelEndpointAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A34DF4E5` — **Rate of TagResourceAPI requests per resource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A34FDF94` — **Rate of DeleteStreamAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A8327CB5` — **Rate of ListTagsForStreamAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AB63770C` — **TURN session concurrent allocations per signaling channel** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-AD15B1B2` — **SendSDPAnswer message payload size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-AD9AD2F3` — **TURN session expiration** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-AEE268C4` — **Rate of UpdateStreamAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B16CD5E1` — **Rate of ListStreamsAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B6B6EF8E` — **Rate of DeleteEdgeConfigurationAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B71B4FEE` — **GetMedia concurrent connections per stream** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-B7CB457B` — **Rate of UpdateDataRetentionAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BAA6C939` — **Rate of DescribeStreamAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BF0D282F` — **GetMedia bandwidth** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-C030232D` — **Rate of UntagResourceAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C0373393` — **Rate of UntagResourceAPI requests per resource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C122494E` — **ConnectAsMaster connections per signaling channel** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-C2CB1AD1` — **Rate of GetHLSStreamingSessionURLAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CAEB7065` — **Rate of TagStreamAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CBA8C1A0` — **Rate of UpdateMediaStorageConfigurationAPI requests per resource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CCD54BEE` — **ConnectAsMaster idle connection timeout** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D87CE70F` — **Rate of PutMediaAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DAAD01CD` — **GetHLSMediaPlaylist fragments** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-DCCB6A93` — **Rate of GetDataEndpointAPI requests per stream** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DE85179A` — **GetMediaForFragmentList connections per stream** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-E4F56E4A` — **TURN session bandwidth** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-EDC0C00D` — **PutMedia fragment duration** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-EDC81B7E` — **Rate of GetHLSMediaPlaylistAPI requests per session** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EDF96A63` — **GetMediaForFragmentList fragments** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-EF7DE569` — **Rate of DescribeMappedResourceConfigurationAPI requests per resource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F0B5EFE9` — **ConnectAsViewer connection duration** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-F10078DD` — **Rate of ListTagsForResourceAPI requests per resource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F42E49F0` — **PutMedia tracks** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-F43C3E04` — **SendICECandidate message payload size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-F65F9A02` — **Rate of GetMP4InitFragmentAPI requests per session** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F6EB90C7` — **Rate of SendSDPOfferAPI requests per websocket connection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F7EF17C6` — **Rate of DeleteSignalingChannelAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FB68989A` — **Rate of DescribeMediaStorageConfigurationAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FD6244B8` — **Rate of ListTagsForResourceAPI requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FD863935` — **GetClip file size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-FDF11C98` — **Rate of DeleteSignalingChannelAPI requests per signaling channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `kms` (52 offene Quotas)

- `L-0428A42E` — **CreateGrant request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-08932E37` — **CreateCustomKeyStore request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1233BF9B` — **DeleteImportedKeyMaterial request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-161E93A6` — **ListRetirableGrants request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-16B46EF0` — **GenerateDataKeyPair (ECC_NIST_P384) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-171660E4` — **ListKeyRotations request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1D966DA0` — **GenerateDataKeyPair (ECC_NIST_P521) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1F75ADD1` — **DeleteAlias request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-275D92F3` — **UpdateCustomKeyStore request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2AC98190` — **Cryptographic operations (RSA) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-32B67F4A` — **CreateKey request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3B372FA9` — **GenerateDataKeyPair (ECC_SECG_P256K1) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3C995F2B` — **Cryptographic operations (ML-DSA) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-515A0541` — **GetParametersForImport request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-635264CC` — **CancelKeyDeletion request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6375F442` — **UntagResource request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6B8C93BD` — **DisableKey request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6E3AF000` — **Cryptographic operations (symmetric) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-705B9E79` — **ConnectCustomKeyStore request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-74021A59` — **RetireGrant request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-77042783` — **GenerateDataKeyPair (RSA_2048) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7851D255` — **GenerateDataKeyPair (ECC_NIST_EDWARDS25519) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-79E0D0AB` — **ListKeyPolicies request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7D6DE447` — **TagResource request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-88313D4A` — **ScheduleKeyDeletion request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8A08DAEA` — **ListKeys request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-99631835` — **ImportKeyMaterial request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9DDDE6CA` — **PutKeyPolicy request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9F1FCF6D` — **DisconnectCustomKeyStore request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A2A30EC6` — **GetKeyPolicy request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A3828E1F` — **UpdateKeyDescription request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AE57B391` — **GenerateDataKeyPair (RSA_3072) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BD96F100` — **EnableKey request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BE799B67` — **EnableKeyRotation request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BF3F8F1D` — **ListAliases request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CE1DB614` — **DisableKeyRotation request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D2EEB5E0` — **GenerateDataKeyPair (ECC_NIST_P256) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D39AB822` — **ListGrants request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D7711EF4` — **GetKeyRotationStatus request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DB3BF542` — **UpdateAlias request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DC14942D` — **Cryptographic operations (ECC & SM2) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E1C93865` — **ReplicateKey request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E20AA94C` — **DescribeCustomKeyStores request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E4FBCA5E` — **GetPublicKey request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E99520CB` — **DeleteCustomKeyStore request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F20EBCB7` — **RevokeGrant request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F7504F73` — **CreateAlias request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F83AC7F7` — **UpdatePrimaryRegion request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FAE8F084` — **DescribeKey request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FB1A2EEA` — **RotateKeyOnDemand request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FB6513A2` — **ListResourceTags request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FCE4492D` — **GenerateDataKeyPair (RSA_4096) request rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `lakeformation` (4 offene Quotas)

- `L-1343AC0E` — **Number of subfolders in an Amazon S3 path** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-3D55E97C` — **Length of a path that can be registered** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-47097528` — **Number of tag values per lf tag** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-9F3EFFAB` — **Number of lf tag policy per principal per resource type** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `lambda` (13 offene Quotas)

- `L-37540937` — **Rate of GetFunction API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4273958C` — **Rate of GetPolicy API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-438DAE3B` — **File descriptors** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-5C4B2C97` — **Synchronous payload** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-77C8EE9D` — **Processes and threads** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-7C0F49F9` — **Asynchronous payload** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-8E39F3F1` — **Deployment package size (console editor)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-9FEEFFC0` — **Function timeout** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-A1AFA3CF` — **Concurrency scaling rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AD930C90` — **Test events (console editor)** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-B2AA0F47` — **Rate of control plane API requests (excludes invocation, GetFunction, and GetPolicy requests)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B99A9384` — **Concurrent executions** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-E49FF7B8` — **Deployment package size (unzipped)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.

## `launchwizard` (1 offene Quota)

- `L-B644EE89` — **Settings Set** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `lex` (1 offene Quota)

- `L-DA28F59B` — **Bot channel associations per bot alias (V2)** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `license-manager` (8 offene Quotas)

- `L-089B8712` — **Total number counted entitlements per checkout** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-2D64C85F` — **Number of account discovery mode updates per day** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-404FB90C` — **Extend license consumption per consumption token** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-6FD36464` — **License conversion tasks per resource per day** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-908B54DF` — **Number of updates for a report generator per day** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-94CAAF1E` — **GetAccessTokens calls** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-96B4765E` — **Maximum number of concurrent organization grant activities** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-FD8F1E79` — **Number of accounts per organization for License Manager** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `lightsail` (12 offene Quotas)

- `L-0ABA1512` — **Default behaviors (default cache behavior) per distribution** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-18D5AED5` — **Response timeout per origin for a distribution** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-4179DBC5` — **Container service certificates** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-5BB7D4B4` — **Tags** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-64F0454B` — **Minimum block storage disk space** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-65A94DD9` — **Data transfer rate per distribution** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8E04AC4B` — **Container service logs storage days** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-A6831527` — **Parallel RDP connections using the browser-based RDP client** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-BBF0F260` — **Static IP addresses** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-C93D8613` — **Origins per distribution** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-D858D90E` — **Parallel SSH connections using the browser-based SSH client** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-D919EE0B` — **Maximum keys per bucket** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `logs` (45 offene Quotas)

- `L-0397E41F` — **PutRetentionPolicy throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-07A912D5` — **DeleteLogGroup throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-15F83CC1` — **GetTransformer throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1CD226BD` — **TestMetricFilter throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-27BFBEA7` — **TestTransformer throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-29A639F6` — **Batch size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-309BA0AF` — **PutTransformer throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-363FC8B0` — **DeleteMetricFilter throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-39FFB556` — **StartLiveTail throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3E4C85B1` — **ListTagsLogGroup throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3F243AD0` — **DescribeLogStreams throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4284EEDE` — **DescribeLogGroups throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4A1D48B1` — **Log groups scanned per Live Tail session** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-4FC2190A` — **StartQuery throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4FE15505` — **GetLogEvents throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-55E3CA17` — **FilterLogEvents throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-56B91A0A` — **DeleteSubscriptionFilter throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-66F5762A` — **DeleteRetentionPolicy throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-69BF6BAC` — **DescribeMetricFilters throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-76507CEF` — **CreateLogStream throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7A4B5D2F` — **AssociateKmsKey throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7A9B3427` — **PutDestination throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7E1FAE88` — **PutLogEvents throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7EB1C513` — **PutDestinationPolicy throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-91470774` — **Event size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-956BB71D` — **TagResource throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-97393AE2` — **CancelExportTask throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9D43025B` — **DescribeSubscriptionFilters throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A33040DC` — **Data archiving** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-A5D79081` — **PutSubscriptionFilter throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-ACAEE94E` — **DescribeExportTasks throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B501C43C` — **UntagResource throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BBECF742` — **TagLogGroup throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BD9DB0EB` — **CreateExportTask throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BE2A59B1` — **DeleteDestination throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BEB90E24` — **DescribeDestinations throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C029A21C` — **DeleteLogStream throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C68057D1` — **DeleteTransformer throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D2832119` — **CreateLogGroup throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D6990B80` — **Live Tail concurrent sessions limit** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-E5FB5933` — **PutMetricFilter throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E6EF8674` — **ListTagsForResource throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EEC839DF` — **Active export task** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-EEEC3365` — **UntagLogGroup throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FAF0999A` — **GetQueryResults  throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `lookoutmetrics` (60 offene Quotas)

- `L-020F22D6` — **Throttle rate (DescribeMetricSet)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0BC408F8` — **Files per interval (10m)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-0F70E4A0` — **Throttle rate (GetSampleData)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-17A5470E` — **Throttle rate (PutFeedback)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1EFB34E0` — **Throttle rate (GetDataQualityMetrics)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1FDF7B91` — **Files per interval (1h)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-29051655` — **Throttle rate (UpdateAnomalyDetector)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-297200B6` — **Throttle rate (ListTagsForResource)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2AF7F498` — **Throttle rate (GetFeedback)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2CD2EB7E` — **Throttle rate (ListAnomalyGroupRelatedMetrics)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-367E0B91` — **Time series per interval (5m)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-3AA7C566` — **Alerts** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-3BA5225A` — **Throttle rate (DetectMetricSetConfig)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3F1EEFE9` — **Dimensions per dataset** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-3FD71F75` — **Value filters per dimension filter** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-40C6821F` — **Dimensions filters per dataset** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-42533647` — **Throttle rate (CreateMetricSet)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-46692FC3` — **Files per interval (1d)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-4B1617A5` — **Throttle rate (BackTestAnomalyDetector)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4CDD974B` — **Records per interval (1d)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-4E92D475` — **Data size per interval (10m)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-535C09C0` — **Records per interval (1h)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-56F61C6F` — **Throttle rate (CreateAnomalyDetector)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-574A683B` — **Data size per interval (1d)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-5D0258C0` — **Throttle rate (ListAnomalyDetectors)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5EB8352D` — **Detectors** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-5F537F31` — **Value length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-5FD69032` — **Throttle rate (DeactivateAnomalyDetector)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-61F79416` — **Time series per interval (1h)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-70CC6666` — **Throttle rate (DescribeAnomalyDetector)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7548F78A` — **Throttle rate (ActivateAnomalyDetector)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7C0C1E87` — **Files per interval (5m)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-8BAF8991` — **Datasources per dataset** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-8C031EB7` — **Throttle rate (DeleteAnomalyDetector)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-943788CD` — **Records per interval (5m)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-96224E7E` — **Data size per interval (1h)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-970F0018` — **Throttle rate (UpdateMetricSet)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-989594D2` — **Time series per interval (1d)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-9A2D9472` — **Time series per interval (10m)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-A384774A` — **Throttle rate (DescribeAnomalyDetectionExecutions)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AA1B9C20` — **Throttle rate (DeleteAlert)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AA27DE10` — **Intervals in historical data (continuous mode)** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-B10A1291` — **Throttle rate (ListAnomalyGroupTimeSeries)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B2F2C358` — **Intervals in historical data (backtest mode)** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-B7D162E6` — **Records per interval (10m)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-BBA63122` — **Files in historical data** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-BD328382` — **Data size for historical data (backtest mode)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-BEA3839E` — **Data size per interval (5m)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-C566AD88` — **Throttle rate (UntagResource)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CB7F0960` — **Data size for historical data (continuous mode)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D87ABA33` — **Throttle rate (GetAnomalyGroup)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E09315CD` — **Measures per dataset** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-E7EB46AB` — **Throttle rate (ListAlerts)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E907B4C2` — **Throttle rate (ListMetricSets)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E91D3491` — **Throttle rate (TagResource)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F256354A` — **Throttle rate (ListAnomalyGroupSummaries)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F2FA38BF` — **Throttle rate (DescribeAlert)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F75BB1C7` — **Throttle rate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F84BD970` — **Throttle rate (CreateAlert)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FF74E011` — **Datasets per detector** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `lookoutvision` (15 offene Quotas)

- `L-1B1011CA` — **Maximum number of models per project** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-1DCAE97B` — **Maximum number of images in a training dataset** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-2489F742` — **Maximum number of concurrent training jobs** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-5863F741` — **Maximum number of concurrent trial detection tasks** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-64685F61` — **Maximum number of projects** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-65CC6428` — **Maximum image dimension for a training or test image (in pixels)** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-6C6DBBAE` — **Maximum number of API requests per second, excluding DetectAnomalies** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-82DA2ABD` — **Maximum number of running models** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-84E8C9F8` — **Maximum number of inference units per started model** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-9A58AC7A` — **Maximum number of DetectAnomalies API requests per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A2F581AB` — **Maximum number of concurrent model packaging jobs** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-C19F11D8` — **Maximum number of images in a trial detection dataset** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-D146B80F` — **Maximum number of images in a test dataset** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-DAB2DC95` — **Minimum image dimension (in pixels) for a training or test image** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-EF7B9086` — **Maximum image file size (in MB) for a training or test image** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.

## `m2` (2 offene Quotas)

- `L-24ACBEAE` — **Max Instances Per High Availability Environment** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-536F13DF` — **Max DataTransferEndpoints Per AWS Account** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `macie2` (19 offene Quotas)

- `L-06179120` — **Microsoft Excel workbook (.xls or .xlsx) file size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-062C8B21` — **Nested levels** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-08803FD0` — **Preventative control monitoring** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-1F4A8665` — **Apache Avro container (.avro) file size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-35C3874E` — **Full names detected** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-54398E25` — **Extracted archive bytes** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-5781F6A2` — **ZIP compressed archive (.zip) file size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6C7B3990` — **Portable Document Format (.pdf) file size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-74471B50` — **Extracted archive files** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-A8D2158C` — **Sensitive data finding occurrences** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-AFA44EA5` — **Mailing addresses detected** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-BEC9D9CC` — **Nested levels in structured data** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-BF81CFA3` — **Apache Parquet (.parquet) file size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-C63BC816` — **Non-binary text file size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-CA9A9123` — **Microsoft Word document (.doc or .docx) file size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D116B4D9` — **Sensitive data discovery occurrences** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-FDB33294` — **TAR archive (.tar) file size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-FE63254C` — **GNU Zip compressed archive (.gz or .gzip) file size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-FEB8D34D` — **Sensitive data discovery per month per account** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `mediaconvert` (67 offene Quotas)

- `L-01D327FE` — **Request rate for GetJobTemplate, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-050D5D43` — **Request rate for CreateResourceShare, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0A485F3B` — **Request rate for GetJob, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0D03A2D6` — **Request rate for ListQueues** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0EB971DE` — **Request rate for CreateJob** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1018D354` — **Request rate for CreateJobTemplate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-15CD4C9A` — **Request rate for StartJobsQuery, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-17F2DE2C` — **Request rate for UpdatePreset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-19E96FB2` — **Request rate for UntagResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1EFE8CE1` — **Request rate for CreateResourceShare** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2120336A` — **Request rate for DisassociateCertificate, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2AC6AD01` — **Request rate for DeletePolicy** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2C57B94C` — **Request rate for Probe** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2D1D110F` — **Request rate for CancelJob** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2F448E56` — **Request rate for StartJobsQuery** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3316B9B0` — **Request rate for ListVersions** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-35F8C38D` — **Request rate for CreatePreset, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-36B9CAA6` — **Request rate for ListTagsForResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3F17D407` — **Request rate for CreateQueue, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3FD3957B` — **Request rate for CreateJobTemplate, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-438B53F5` — **Request rate for DeleteJobTemplate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4922E007` — **Request rate for ListQueues, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4CC56996` — **Request rate for ListVersions, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4FAC0A2F` — **Request rate for GetQueue, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-54D5F5A5` — **Request rate for UpdateQueue, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-56566502` — **Request rate for DeletePolicy, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5663DECD` — **Request rate for UpdateJobTemplate, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5885B012` — **Request rate for GetPreset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-593F5D32` — **Request rate for GetQueue** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-61B4871B` — **Request rate for SearchJobs** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-63007F37` — **Request rate for TagResource, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-647EBFA7` — **Request rate for TagResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6728A9EC` — **Request rate for GetPolicy** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6960A8DA` — **Request rate for DeletePreset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6CA5AFAC` — **Request rate for ListJobTemplates** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-716F67B4` — **Request rate for DeleteQueue, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7485AF10` — **Request rate for AssociateCertificate, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-75A471E3` — **Request rate for UpdateJobTemplate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-78B2D11D` — **Request rate for GetJob** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7AE60458` — **Request rate for AssociateCertificate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-83C5ACEF` — **Request rate for PutPolicy** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-84EB285F` — **Request rate for Probe, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-882AEE64` — **Concurrent jobs queries per account** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-94047106` — **Request rate for ListJobs, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9ABC3758` — **Request rate for DeletePreset, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A0D28790` — **Request rate for GetPreset, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A487133E` — **Request rate for CreateQueue** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A4F8DFA3` — **Request rate for ListJobs** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A51E3FE2` — **Request rate for ListTagsForResource, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AA313626` — **Request rate for DeleteQueue** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-ACAF5652` — **Request rate for UpdateQueue** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B152EC96` — **Request rate for ListPresets** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B529BF7C` — **Request rate for ListJobTemplates, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B537ABAB` — **Request rate for GetJobsQueryResults, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BA1DE85F` — **Request rate for CancelJob, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BBA38989` — **Request rate for PutPolicy, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C043869B` — **Request rate for DeleteJobTemplate, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C36D2A6D` — **Request rate for GetJobTemplate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CD746D2B` — **Request rate for CreateJob, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CE9179D5` — **Request rate for CreatePreset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CF93C968` — **Request rate for ListPresets, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D35248DB` — **Request rate for UpdatePreset, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E39302DC` — **Request rate for GetPolicy, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E45A403C` — **Request rate for UntagResource, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E62FCB1E` — **Request rate for GetJobsQueryResults** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F58AEA3F` — **Request rate for DisassociateCertificate** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FB5B56D0` — **Request rate for SearchJobs, in a burst** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `medialive` (2 offene Quotas)

- `L-4D7207DE` — **Pull Inputs** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-63879FB4` — **MediaLive DescribeThumbnails TPS** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `mediapackage` (16 offene Quotas)

- `L-1D216601` — **Burst rate of REST API requests (VOD)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1E11547D` — **Rate of manifest egress requests per asset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-20E16360` — **Rate of REST API requests (VOD)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-258E8DBA` — **Tracks per ingest stream (Live)** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-2FF063D2` — **Rate of REST API requests (Live)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3C7827C4` — **Content retention** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-4D5703CE` — **Ingest streams per asset** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-5625C794` — **Ingest streams per channel** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-80529300` — **Rate of segment egress requests per asset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-81A8E99B` — **Tracks per ingest stream (VOD)** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-8D3D8B62` — **Time-shifted manifest length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-BC1EEC38` — **Rate of manifest egress requests per origin endpoint** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BEF6A5C5` — **Rate of segment egress requests per origin endpoint** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F0A6E997` — **Burst rate of REST API requests (Live)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F461E421` — **Rate of ingest requests per channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F7CB14AC` — **Live manifest length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.

## `mediapackagev2` (11 offene Quotas)

- `L-327832D0` — **Rate of manifest egress requests per origin endpoint** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3982B8D7` — **Time-shifted manifest length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-628CF433` — **Active harvest jobs per channel group** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-71A50308` — **Content retention** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-88EC0651` — **Ingest streams per channel** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-B20140A1` — **Live manifest length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-BE196DD4` — **Rate of segment egress requests per origin endpoint** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BE974EAD` — **Tracks per ingest stream** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-DA364562` — **Burst rate of REST API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DC0E43E8` — **Rate of ingest requests per channel** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E84C56ED` — **Rate of REST API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `mediastore` (9 offene Quotas)

- `L-06089B48` — **Folder levels** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-2FCDD326` — **Rate of DeleteObject API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8038710B` — **Rate of DescribeObject API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-97AEAA6B` — **Rate of ListItems API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CA39FABB` — **Rate of PutObject API requests for standard upload availability** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CAF2EF73` — **Rate of PutObject API requests for chunked transfer encoding (also known as streaming upload availability)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DB1D877F` — **Rate of GetObject API requests for standard upload availability** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F7BC88E9` — **Object size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-FA6DBE33` — **Rate of GetObject API requests for streaming upload availability** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `mediatailor` (14 offene Quotas)

- `L-007E683B` — **Content origin server timeout** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-0F7265C4` — **Package configurations** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-16A95E26` — **Manifest size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-32FBC51C` — **Ad Insertion Requests** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-7202B1BD` — **Ad decision server (ADS) redirects** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-7946CFE6` — **Programs Per Channel** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-7A79D9CE` — **Live Sources** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-93B27B6F` — **Content origin length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-A32E8357` — **VOD Sources** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-B7A40915` — **Ad decision server (ADS) length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B800E13A` — **Ad decision server (ADS) timeout** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B9D43015` — **Manifest Requests** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-BE3CDF89` — **Session expiration** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-C13EFDBD` — **Channel Manifest Requests** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `mgn` (3 offene Quotas)

- `L-13A5D930` — **Max NSX gateway policy rules per network migration definition** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-866BF8B4` — **Max NSX security policy rules per network migration definition** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-9A599620` — **Max Active Source Servers** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.

## `migrationhubstrategy` (2 offene Quotas)

- `L-7571197D` — **Assessment Maximum** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-A80C6746` — **Active Assessment Maximum** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.

## `monitoring` (49 offene Quotas)

- `L-05D334F0` — **Rate of ListMetrics requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0720E68F` — **Rate of PutMetricAlarm requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0F4E28CA` — **Rate of DeleteMetricStream requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1F0C4E0C` — **Rate of GetInsightRuleReport requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-21CB40A4` — **Rate of DescribeAlarms requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-22339239` — **Rate of DeleteInsightRules requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-25E8DC37` — **Rate of DeleteAlarms requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4609795C` — **Rate of TagResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-50BF3376` — **Rate of DeleteAnomalyDetector requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-515B0B71` — **Rate of PutCompositeAlarm requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-59022E75` — **Rate of GetMetricStream requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5E141212` — **Rate of GetMetricData requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-601618F7` — **Rate of LAMBDA usage in GetMetricData** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6300B446` — **Rate of DescribeAnomalyDetectors requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-646A917A` — **Rate of EnableInsightRules requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6753900D` — **Rate of PutDashboard requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-68B0DFE2` — **Rate of SetAlarmState requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6929DE8C` — **Rate of UntagResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-69C44FFD` — **Rate of ListDashboards requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6FCAAA2E` — **Rate of GetMetricWidgetImage requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7193C790` — **Rate of DescribeAlarmHistory requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-722EAE58` — **Rate of ANOMALY_DETECTION_BAND usage in GetMetricData** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-787E531D` — **Rate of StartMetricStreams requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7D8B1BC8` — **Rate of DescribeAlarmContributors requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-86AA5564` — **Rate of DescribeInsightRules requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8742A250` — **Rate of DB_PERF_INSIGHTS usage in GetMetricData** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8A387C66` — **Rate of PutAnomalyDetector requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8BC498D4` — **Rate of PutMetricData requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8DCC6151` — **Rate of SERVICE_QUOTA usage in GetMetricData** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9FFA42D2` — **Rate of PutInsightRule requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A1710150` — **Rate of ListMetricStreams requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A23CEE97` — **Rate of SEARCH usage in GetMetricData** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A4883EA4` — **Rate of Metrics Insights usage in GetMetricData** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A64F5500` — **Rate of StopMetricStreams requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A6D89949` — **Rate of PutMetricStream requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AB1871A7` — **Number of Metrics Insights alarms** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-B6C4D57E` — **Rate of ListTagsForResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C1B4557E` — **Rate of GetMetricData datapoints for metrics older than three hours** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C234EDB6` — **Rate of DisableInsightRules requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C6D91C0A` — **Rate of INSIGHT_RULE_METRIC usage in GetMetricData** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CA907765` — **Rate of EnableAlarmActions requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D750D224` — **Rate of DisableAlarmActions requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DBD11BCC` — **Number of Contributor Insights rules** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-DFE30068` — **Rate of GetMetricData datapoints using Metrics Insights** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E1508405` — **Rate of DeleteDashboards requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E2310E7A` — **Rate of DescribeAlarmsForMetric requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E82C279D` — **Rate of GetDashboard requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EE839489` — **Rate of GetMetricStatistics requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F5FE387B` — **Rate of GetMetricData datapoints for the last three hours of metrics** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `mq` (12 offene Quotas)

- `L-2757006A` — **Storage capacity per smaller broker** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-2945EBE1` — **Destinations monitored in CloudWatch (RabbitMQ)** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-42B434B7` — **Wire-level connections per larger broker** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-5775772E` — **API burst limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7AAF71B3` — **Job scheduler usage limit per broker backed by Amazon EBS** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-9A922C52` — **Temporary storage capacity per larger broker** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-A5C214C9` — **Wire-level connections per smaller broker** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-B0F7ED94` — **Storage capacity per larger broker** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-BAFD73B7` — **Destinations monitored in CloudWatch (ActiveMQ)** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-BB510D1B` — **Groups per user (simple auth)** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-D9C3728B` — **API rate limit** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DF9D3FFB` — **Temporary storage capacity per smaller broker** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.

## `neptune` (5 offene Quotas)

- `L-22818E49` — **Reserved DB instances** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-463F8A01` — **Event subscriptions** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-9AEE2A70` — **DB cluster Roles** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-B3AC6773` — **Tags per resource** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-BF10548E` — **Cross-region snapshot copy requests** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `neptune-graph` (24 offene Quotas)

- `L-0E92389A` — **Rate of DeleteGraph API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-145975CA` — **Maximum provisioned memory for each graph** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-145FBBEC` — **Rate of DeletePrivateGraphEndpoint API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1A4D313F` — **Rate of CreateGraph API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2C6692EB` — **Rate of GetGraph API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-319B0970` — **Rate of UntagResource API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3BE1AAB0` — **Rate of ListImportTasks API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-43875DB3` — **Rate of CreateGraphUsingImportTask API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-43A5F0FD` — **Rate of GetImportTask API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4C2E6787` — **Rate of ResetGraph API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5E4F82AC` — **Rate of CreatePrivateGraphEndpoint API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6CECD12A` — **Maximum Graph snapshots** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-6D065F9A` — **Rate of RestoreGraphFromSnapshot API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8DE01AD2` — **Rate of ListTagsForResource API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A53FC974` — **Rate of GetGraphSnapshot API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-ACC6671C` — **Rate of CreateGraphSnapshot API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BAD55E25` — **Rate of TagResource API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BCF9AD64` — **Rate of GetPrivateGraphEndpoint API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CCA6A9D0` — **Rate of CancelImportTask API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CF286151` — **Rate of DeleteGraphSnapshot API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D317DBA8` — **Rate of ListPrivateGraphEndpoints API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DCD81945` — **Rate of ListGraphs API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E50E3387` — **Rate of UpdateGraph API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F4990E36` — **Rate of ListGraphSnapshots API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `network-firewall` (2 offene Quotas)

- `L-2B6C8C12` — **Network traffic bandwidth per firewall endpoint** — `USAGE_METRIC`: Current traffic bandwidth is transient and cannot be derived from the persistent configuration inventory. A compatible official usage metric is required.
- `L-A364946C` — **Suricata rule character length** — `CONFIG_LIMIT`: AWS counts expanded variable values toward each rule's character length. The API returns the unexpanded rules string and variable definitions separately, so raw line length could understate usage.

## `networkmonitor` (2 offene Quotas)

- `L-A8FA6DFE` — **Number of probes per subnet for each monitor** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-F192A8D6` — **Number of probes per monitor** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `oam` (15 offene Quotas)

- `L-022081A8` — **Rate of ListSinks requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0C9B84F1` — **Rate of GetLink requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-143B6A4E` — **Rate of DeleteSink requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-17A1180D` — **Rate of GetSink requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1DA9A53C` — **Rate of DeleteLink requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5CCC34E8` — **Rate of PutSinkPolicy requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-64C711AB` — **Rate of CreateSink requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6F6854CA` — **Rate of GetSinkPolicy requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6FE8607E` — **Rate of ListTagsForResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-73AD4D12` — **Rate of CreateLink requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7EEA7BFD` — **Rate of ListAttachedLinks requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AB9CB007` — **Rate of UntagResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B753F5F0` — **Rate of ListLinks requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D7E6CF70` — **Rate of UpdateLink requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F026BF93` — **Rate of TagResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `observabilityadmin` (22 offene Quotas)

- `L-02B8A1F5` — **CreateTelemetryRule throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0E7D3563` — **TagResource throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-16C95A4F` — **ListTelemetryRules throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-25B3FFB6` — **GetTelemetryRule throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-273CFA22` — **GetTelemetryRuleForOrganization throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3C08CE9A` — **DeleteCentralizationRuleForOrganization throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-44AADB91` — **GetCentralizationRuleForOrganization throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-511AA035` — **UpdateTelemetryRule throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-540C0D01` — **CreateTelemetryRuleForOrganization throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6C6C8BE5` — **UpdateCentralizationRuleForOrganization throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6F082A4D` — **ListTelemetryRulesForOrganization throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-843A6F7E` — **ListTagsForResource throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8CA0A2C6` — **Logs Centralization throughput per destination region** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9829E39B` — **DeleteTelemetryRule throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A444B7E5` — **CreateCentralizationRuleForOrganization throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B19247CC` — **GetTelemetryEnrichmentStatus throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C0997F54` — **UntagResource throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C6A78D4B` — **StopTelemetryEnrichment throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DC459BE3` — **UpdateTelemetryRuleForOrganization throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E3DAB469` — **StartTelemetryEnrichment throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F0470CCF` — **ListCentralizationRulesForOrganization throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F7893284` — **DeleteTelemetryRuleForOrganization throttle limit in transactions per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `omics` (6 offene Quotas)

- `L-13B00733` — **Analytics - Maximum size of each file in a variant import job** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-22E12079` — **Analytics - Maximum files per variant store import job** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-24A3B174` — **Workflows - Transactions per second (TPS) for the StartRun operation** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-35CE76C9` — **Workflows - Maximum static run storage capacity per run** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-7B9E5416` — **Workflows - Maximum run duration** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B94B38A2` — **Analytics - Maximum size of each file in an annotation import job** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.

## `payment-cryptography` (3 offene Quotas)

- `L-946BFBA8` — **Combined rate of control plane requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B90266F0` — **Combined rate of data plane requests (symmetric)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BBE04029` — **Combined rate of data plane requests (asymmetric)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `pca-connector-ad` (27 offene Quotas)

- `L-01AB3861` — **Rate of DeleteConnector requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-046630BB` — **Rate of GetTemplate requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0916B3E3` — **Rate of GetPolicies requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-17569A85` — **Rate of CreateDirectoryRegistration requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1F0B4E70` — **Rate of DeleteTemplate requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-21A25C3F` — **Rate of CreateTemplateGroupAccessControlEntry requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-27D56743` — **Rate of RequestSecurityToken requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-431F19A0` — **Rate of UpdateTemplate requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-49BEA97B` — **Rate of ListConnectors requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5512056E` — **Rate of ListTemplateGroupAccessControlEntries requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-568BB718` — **Rate of DeleteDirectoryRegistration requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5CC72EAF` — **Rate of GetDirectoryRegistration requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-64E52FB9` — **Rate of UntagResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-657D5FD0` — **Rate of UpdateTemplateGroupAccessControlEntry requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6930FFF8` — **Rate of CreateServicePrincipalName requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-70E167AD` — **Rate of CreateTemplate requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-71CF09F7` — **Rate of ListDirectoryRegistrations requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7362C0AD` — **Rate of ListTemplates requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7966F778` — **Rate of CreateConnector requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8228CBB5` — **Rate of DeleteServicePrincipalName requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-853BCABE` — **Rate of DeleteTemplateGroupAccessControlEntry requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8B0AFBB5` — **Rate of ListServicePrincipalNames requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-957664CC` — **Rate of TagResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A40E38B0` — **Rate of GetTemplateGroupAccessControlEntry requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EE597D84` — **Rate of ListTagsForResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F16E91B4` — **Rate of GetServicePrincipalName requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F6A7C5A2` — **Rate of GetConnector requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `pca-connector-scep` (15 offene Quotas)

- `L-2A99D11A` — **Rate of GetConnector requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2F85730F` — **Rate of GetChallengeMetadata requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-32FCF930` — **Rate of GetChallengePassword requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-35687899` — **Rate of DeleteChallenge requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-43C22268` — **Rate of ListTagsForResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-456B57EC` — **Rate of GetCACaps requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5967BA28` — **Rate of GetCACert requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7ED03DC7` — **Rate of CreateConnector requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8450A20F` — **Rate of ListChallengeMetadata requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-98EB5A5D` — **Rate of ListConnectors requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A0B79F1B` — **Rate of PKCSReq requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A87A2654` — **Rate of DeleteConnector requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F422750F` — **Rate of UntagResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F4B10249` — **Rate of TagResource requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F76F0010` — **Rate of CreateChallenge requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `personalize` (65 offene Quotas)

- `L-0314CB5C` — **Rate of GetActionRecommendations requests per campaign** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0DAD8751` — **Number of actions used in model training** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-12101E4A` — **Rate of UpdateCampaign requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-141B5F3C` — **Rate of CreateDatasetGroup requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1513644C` — **Rate of ListDatasetGroups requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-159027CF` — **Rate of DescribeSchema requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-18DCD0DA` — **PutActionInteractions Event size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-1B982452` — **Rate of CreateSolutionVersion requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1CAC7664` — **Rate of DeleteDatasetGroup requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-2EE592C4` — **Amount of users and items data combined for HRNN-metadata recipe** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-34736E70` — **Rate of DeleteSchema requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-353C3E7E` — **Rate of DeleteEventTracker requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3A329490` — **Rate of ListSolutions requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3A79BA38` — **Rate of ListRecipes requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3A81D0FF` — **Rate of DescribeRecipe requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-49CC69B6` — **Number of items used in model training** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-4DFC060E` — **Minimum data points for model training** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-5282CC49` — **Rate of ListDatasetImportJobRuns requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-542429F0` — **Rate of ListSchemas requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5667F87F` — **Rate of transactions per account** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5D7942B8` — **Rate of CreateDataset requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5E3F1253` — **Rate of DescribeEventTracker requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6A61577D` — **Rate of DescribeDatasetImportJob requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-76C4D7A9` — **Rate of UpdateDataset requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-76D6B0AB` — **Rate of ListSolutionVersions requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7AA65A3D` — **Rate of CreateDatasetImportJob requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7E76619B` — **Rate of DeleteSolution requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8047B3A8` — **Rate of PutEvents requests per dataset group** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-83D79D48` — **Rate of GetPersonalizedRanking requests per campaign** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-896849F5` — **Rate of ListEventTrackers requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-89B2007E` — **Rate of GetSolutionMetrics requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8CF67C84` — **Amount of interactions data for HRNN-coldstart recipe** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-90932EE6` — **Number of action interaction events in a PutActionInteractions call** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-9B095670` — **Rate of DescribeDatasetGroup requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9FDB137B` — **Rate of CreateCampaign requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A2675B6E` — **Amount of interactions data for HRNN-metadata recipe** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-A2738B0F` — **Number of events in PutEvents call** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-A527EF3A` — **Rate of CreateSolution requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A6A4AB70` — **Number of interactions for model training** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-A6D35102` — **Amount of data for Popularity-Count recipe** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-A8FE1453` — **Maximum number of interactions per event type per user considered by a filter.** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-ACBBDC27` — **Rate of DeleteDatasetImportJob requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-ADCAE478` — **Minimum unique users for model training** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-AE7FD4E5` — **Rate of ListCampaigns requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B33ADDC3` — **Amount of data for Personalized-Ranking recipe** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-B9C7903C` — **Rate of ListDatasetImportJobs requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BD0DF30D` — **Rate of DeleteCampaign requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C044F2CA` — **Rate of CreateSchema requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C5A4FD57` — **Amount of data per incremental import.** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-C71694DA` — **Maximum number of action interactions per event type per user considered by a filter.** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-CA34375E` — **Rate of ListDatasets requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D1699476` — **Rate of CreateEventTracker requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D551DB19` — **Rate of DescribeAlgorithm requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D98A73E8` — **Rate of DescribeCampaign requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DC96DE0A` — **Rate of DescribeDataset requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DD6792CA` — **Amount of data for HRNN recipe** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-DEDA9DCF` — **Amount of users and items data combined for HRNN-coldstart recipe** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-E1ABE5BE` — **Rate of DeleteDataset requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E30A1A43` — **Number of action interactions for model training** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-E427562C` — **Amount of data for SIMS recipe** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-E5F8E322` — **Rate of GetRecommendations requests per campaign** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-ECA454DD` — **Rate of DescribeSolution requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F1119DA2` — **Rate of PutActionInteractions requests per dataset group** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FA8BB2FC` — **Event size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-FAB63F14` — **Rate of DescribeFeatureTransformation requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `pinpoint` (122 offene Quotas)

- `L-00469515` — **CreateVoiceTemplate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-00CA3D60` — **Attribute value length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-011AAE4D` — **Number of SMS messages that can be sent to a single recipient each second** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-0428A7CE` — **UpdateInAppTemplate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0A577A5A` — **Import size per import job** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-10976A2B` — **Maximum number of characters in FCM-specific template parts of a push notification template** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-10D925B2` — **Maximum number of custom metric keys per app** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-10E9041F` — **APNs sandbox message payload size per message** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-11BF23E4` — **UpdateSegment operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-145312C1` — **Baidu Cloud Push message payload size per message** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-17A23394` — **Maximum number of characters in an email template** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-190CC5A1` — **CreateInAppTemplate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-19FAC8C7` — **Number of attributes assigned to the Metrics parameter** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-1A67054A` — **Maximum number of attempts to invoke a Lambda function** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-1CFEC081` — **PutEvents operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-1DACDC1C` — **Maximum number of characters for an event attribute value in a custom channel response** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-20A1359C` — **CreateSmsTemplate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-211AA0F8` — **Number of import files per import job** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-22143048` — **UpdatePushTemplate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-27084BF9` — **UpdateEndpointsBatch operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-283A6638` — **Maximum number of event attributes per endpoint in a custom channel response** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-323B59AE` — **UpdateCampaign operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-333E663A` — **UpdateEndpoint operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-34FB2630` — **Maximum number of characters in a voice template** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-39643E10` — **Number of SMS messages that can be sent each second (sending rate)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3C767F9E` — **CreateInAppTemplate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-41F2C85D` — **Number of attributes assigned to the Attributes, Metrics, and UserAttributes parameters collectively** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-4407470A` — **GetEndpoint operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-44D8849B` — **Maximum size of an invocation payload (request and response) for a Lambda function** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-46514212` — **Maximum number of custom attribute values per attribute key** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-4A31FA0E` — **Maximum number of characters in an SMS template** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-4AC67C61` — **Maximum number of characters for an event attribute name in a custom channel response** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-4CFE22DD` — **Invocation payload size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-4D2BBF82` — **DeleteCampaign operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4D68DFD0` — **Maximum size of an individual event** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-4FE3F5C9` — **Maximum number of custom attribute keys per app** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-515FC177` — **Maximum message size, including attachments** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-5160B7E0` — **Number of endpoints with the same user ID** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-55406C36` — **UpdateEndpointsBatch operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-580B96A2` — **Maximum number of recommended attributes per endpoint or user** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-5D20177E` — **SendMessages operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5D254524` — **Maximum number of characters in the default template parts of a push notification template** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-5D4A1FC6` — **Maximum number of characters in APN-specific template parts of a push notification template** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-604A66DF` — **Apple Push Notification service (APNs) message payload size per message** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-625F7367` — **Number of verified identities** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-64B71623` — **Firebase Cloud Messaging (FCM) message payload size per message** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6733389F` — **UpdatePushTemplate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6B6A4B75` — **SendUsersMessages operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6BA826DB` — **Maximum length of a recommended attribute value that's retrieved from Amazon Personalize** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6D703411` — **Number of Amazon SNS topics for two-way SMS per account** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-6FAB1B15` — **Maximum number of characters in Baidu-specific template parts of a push notification template** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-702C5879` — **GetEndpoint operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-72A1F6B5` — **All other operations burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-733BED32` — **UpdateEmailTemplate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-740E6D0F` — **DeleteEndpoint operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-74FC19BA` — **PhoneNumberValidate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-768FB8FB` — **UpdateSegment operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-79EC8125` — **Number of voice messages that can be sent from a single originating phone number per second** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-7AAEDF6B` — **Number of attributes assigned to the Attributes parameter** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-7E3252BF` — **CreateSmsTemplate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8A34A67D` — **DeleteSegment operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8C220D3D` — **CreateEmailTemplate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8F134A4E` — **Number of EndpointBatchItem objects in an EndpointBatchRequest payload** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-8FBB07F4` — **CreateVoiceTemplate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-90D8DA58` — **UpdateEmailTemplate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9142FA7C` — **UpdateEndpoint operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9318E2F4` — **Number of voice messages that can be sent per minute** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-98A9B620` — **UpdateInAppTemplate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-99319FFB` — **Maximum size of a request** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-9AE43654` — **Number of emails that can be sent each second (sending rate)** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9CF9DDA0` — **SendUsersMessages operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A206F458` — **Maximum size per endpoint** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-A255138B` — **CreateCampaign operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A2957BEB` — **Number of voice messages that can be sent during a 24-hour period** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-A5332206` — **Maximum number of recommendations per endpoint or user** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-A742486B` — **Number of recipients per message** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-A7D30E78` — **SMS spending threshold** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-A9CF2F09` — **UpdateSmsTemplate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AB04D53C` — **DeleteCampaign operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AC82394D` — **CreateSegment operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B008BB16` — **CreatePushTemplate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B09B5654` — **Maximum number of characters in ADM-specific template parts of a push notification template** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B1044409` — **Number of characters in a voice message** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B1934D4C` — **Maximum number of recommended attributes per endpoint or user (AWS Lambda function)** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-B5E24C24` — **CreateCampaign operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B6F19F2C` — **Maximum length of a recommended attribute name** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-BB6E4BFB` — **Number of attributes assigned to the UserAttributes parameter** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-BBD1EBDF` — **Amazon Device Messaging (ADM) message payload size per message** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-C32B9F4C` — **UpdateVoiceTemplate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C407DD59` — **CreateEmailTemplate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C477DE56` — **Number of voice configuration sets per AWS region** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-C4CADB07` — **Maximum number of model configurations per message template** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-C8E63E9B` — **UpdateSmsTemplate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D0CC64F8` — **UpdateCampaign operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D10E8F93` — **All other operations rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D4695B37` — **Maximum segment size per campaign** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D5F199FA` — **Number of values assigned to the Attributes parameter attributes per attribute** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-D7778D32` — **Maximum number of characters per attribute value** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D862A171` — **Maximum number of model configurations per account** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-D8EA67D3` — **UpdateVoiceTemplate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DC81CDCA` — **Maximum number of attribute keys and metric keys for each event per request** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-DD05AA08` — **Maximum length of a recommended attribute display name** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-DE86E513` — **Maximum number of push notifications that can be sent per second in a campaign** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-DEDDBACD` — **Maximum number of custom event types per app** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-E02683D7` — **DeleteSegment operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E30F449E` — **PhoneNumberValidate operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E5E7458F` — **Maximum number of events in a request** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-E6F8CC8E` — **Attribute name length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-E72E950C` — **Maximum number of dimensions that can be used to create a segment** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-E8BFE267` — **Maximum number of characters per attribute key** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-EB037E37` — **Maximum segment size per journey** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-EB57023C` — **Voice message length** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-F123C43A` — **PutEvents operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F179D122` — **Number of emails that can be sent per 24-hour period (sending quota)** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-F1EE9BC5` — **SendMessages operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F2841F8A` — **DeleteEndpoint operation rate quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F2C2908E` — **Maximum amount of time to wait for a Lambda function to process data** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-F5A3090E` — **CreatePushTemplate operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F625D3DB` — **Number of identities that you can verify** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-F62D0221` — **Number of values assigned to the UserAttributes parameter attributes per attribute** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-FB330AEF` — **Number of voice messages that can be sent to a single recipient during a 24-hour period** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-FC4EDB5E` — **CreateSegment operation burst quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `polly` (15 offene Quotas)

- `L-00C9620B` — **StartSpeechSynthesisTask lexicon count** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-17639580` — **SynthesizeSpeech billed character count** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-18255867` — **Rate of StartSpeechSynthesisTask (standard) requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-18474792` — **SynthesizeSpeech total character count** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-261DF501` — **SynthesizeSpeech lexicon count** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-3E095342` — **Rate of StartSpeechSynthesisTask (generative) requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-43330D37` — **Rate of GetSpeechSynthesisTask and ListSpeechSynthesisTasks requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6144E1AC` — **Lexicon size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-77D5DB9E` — **StartSpeechSynthesisTask total characters limit** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-79B4630F` — **StartSpeechSynthesisTask billed characters count** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-7E184727` — **Rate of SynthesizeSpeech (generative) requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9FB8AA30` — **Rate of SynthesizeSpeech (standard) requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A65CEC2D` — **Rate of SynthesizeSpeech (neural) requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B9A743A4` — **Rate of StartSpeechSynthesisTask (neural) requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D93DD9F2` — **Rate of lexicon management requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `profile` (5 offene Quotas)

- `L-3A29C525` — **Object and profile maximum size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-63975AF3` — **Maximum size of all objects for a profile** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B59352A0` — **Maximum number of segment snapshots per day** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-DFAEAED3` — **Maximum number of profile history records per profile** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-E17DC7C3` — **Objects per profile** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `qldb` (2 offene Quotas)

- `L-22B6E165` — **QLDB exports per ledger** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-91B08359` — **QLDB streams per ledger** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.

## `qt-platform` (12 offene Quotas)

- `L-072080F6` — **Concurrent .NET jobs with the Microsoft Visual Studio Extension per IAM Identity Center account** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-0BC013B2` — **mainframe Technical Document Generation Monthly Lines of Code** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-3EFD14C6` — **mainframe Lines of Code per Job** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-666F92B7` — **mainframe Decomposition Lines of Code** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6D744CF7` — **Concurrent .NET web jobs per IAM Identity Center account** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-A6B59AB2` — **mainframe Analyze Lines of Code** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-B5CFC3D3` — **mainframe Transform of Lines of Code** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-BFAAF0CB` — **Concurrent mainframe jobs per IAM Identity Center account** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-C59A2C65` — **.NET monthly lines of code (web & IDE)** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D322D236` — **mainframe Reforge Lines of Code** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D79BB1C9` — **Workspaces per AWS IAM Identity Center** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-DEC3FFCF` — **mainframe Business Document Generation Monthly Lines of Code** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.

## `quicksight` (6 offene Quotas)

- `L-01C190BD` — **API_CREATE-INGESTION: Calls per 24 hour period from Standard edition** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-92D2E884` — **The maximum amount of time to wait for a dataset preview** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-BF25D425` — **Email aliases per group for email reports** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-C2064901` — **Data Prep: Fields per dataset** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-E3375426` — **API_CREATE-INGESTION: Calls per 24 hour period from Enterprise edition** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-F1EA8033` — **Query timeout for visuals** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.

## `rds` (6 offene Quotas)

- `L-BDB2F348` — **Data API maximum result set size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-C0506D15` — **Data API maximum size of JSON response string** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D87A28C7` — **Data API HTTP request body size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-E3721453` — **Data API maximum concurrent cluster-secret pairs** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-E79969BF` — **Data API maximum concurrent requests** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-ECDFB241` — **Data API requests per second** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `redshift` (15 offene Quotas)

- `L-01DE90DD` — **Tables for xlplus cluster node type with a single-node cluster** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-21B48DE6` — **Stored procedures in a database** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-24D7B305` — **Concurrency level (query slots) for all user-defined manual WLM queues** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-4D30B127` — **Single row size when loading by COPY** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-4E1FE923` — **Schemas in each database per cluster** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-7438E5E3` — **Tables for xlplus cluster node type with a multiple-node cluster** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-7CB1CC00` — **Maximum number of connections for RA3 nodes** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-8AFA7F04` — **Column limit for external tables with pseudocolumns when using AWS Glue Data Catalog** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-986F545D` — **Tables for large cluster node type** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-99F53FC8` — **Tables for 4xlarge cluster node type** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-A4D89F59` — **Tables for xlarge cluster node type** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-CA4E81F8` — **User-defined databases in a cluster** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-D236BDB3` — **Allowed string value size per ION or JSON file when using AWS Glue Data Catalog** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D8ECCA81` — **Tables for 8xlarge cluster node type** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-FA4166C9` — **Tables for 16xlarge cluster node type** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `rekognition` (79 offene Quotas)

- `L-0366BB0F` — **Transactions per second per account for the Amazon Rekognition Image operation ListCollections** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-03F18989` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation CreateProjectVersion** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-06ACBDE8` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation DescribeProjects** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-08B7635A` — **Transactions per second per account for the Amazon Rekognition Video stored video start operation StartCelebrityRecognition** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0FB781AE` — **Transactions per second per account for the Amazon Rekognition Streaming Video Events operation UpdateStreamProcessor** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-108100B3` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation: ListDatasetLabels** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-12019FB0` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation DescribeProjectVersions** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-220834FB` — **Transactions per second per account for the Amazon Rekognition Image operation DeleteFaces** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-39854D9A` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation: CreateDataset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-3B051C64` — **Transactions per second per account for the Amazon Rekognition Video stored video get operation GetFaceSearch** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-41805FEB` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation: ListDatasetEntries** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-43CBEB68` — **Transactions per second per account for the Amazon Rekognition Image operation SearchFacesByImage** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4E7ADAC1` — **Transactions per second per account for the Amazon Rekognition Video stored video get operation GetFaceDetection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-513570CC` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation: UpdateDatasetEntries** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-532A3DAC` — **Transactions per second per account for the Amazon Rekognition operation: SearchUsers** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5346A13A` — **Transactions per second per account for the Amazon Rekognition Image operation DeleteCollection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-55A22B20` — **Transactions per second per account for the Amazon Rekognition Video stored video start operation StartSegmentDetection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5AA330BC` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation ListProjectPolicies** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5C10FBD9` — **Transactions per second per account for the Amazon Rekognition Video stored video get operation GetTextDetection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5EAC8E57` — **Transactions per second per account for the Amazon Rekognition Video stored video get operation GetLabelDetection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5FF750C4` — **Transactions per second per account for the Amazon Rekognition Image operation RecognizeCelebrities** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-66AB9558` — **Transactions per second per account for the Amazon Rekognition Streaming Video Events operation DeleteStreamProcessor** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6F294C5B` — **Transactions per second per account for the Amazon Rekognition Image personal protective equipment operation DetectProtectiveEquipment** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6FDFFAF5` — **Transactions per second per account for the Amazon Rekognition Image operation DescribeCollection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-71159A7C` — **Transactions per second per account for the Amazon Rekognition Video stored video get operation GetPersonTracking** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-711B1E8A` — **Transactions per second per account for the Amazon Rekognition operation: ListTagsForResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-71793F35` — **Transactions per second per account for the Amazon Rekognition Streaming Video Events operation StartStreamProcessor** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-73A341CE` — **Transactions per second per account for the Amazon Rekognition Image operation CompareFaces** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7C13EBAD` — **Transactions per second per account for the Amazon Rekognition Image operation IndexFaces** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-7E97BCDC` — **Maximum number of images per Amazon Rekognition Custom Labels detection test dataset** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-7F4D1AC4` — **Transactions per second per account for the Amazon Rekognition Image operation DetectModerationLabels** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-82C6694D` — **Transactions per second per account for the Amazon Rekognition Streaming Video Events operation DescribeStreamProcessor** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-832B35BA` — **Transactions per second per account for the Amazon Rekognition operation: StartMediaAnalysisJob** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-85890340` — **Transactions per second per account for the Amazon Rekognition Streaming Video Events operation StopStreamProcessor** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-87CF5BA6` — **Transactions per second per account for the Amazon Rekognition Image operation DetectText** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8CA99658` — **Transactions per second per account for the Amazon Rekognition Video stored video start operation StartFaceSearch** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-90C845BC` — **Transactions per second per account for the Amazon Rekognition Video stored video start operation StartTextDetection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-96D6749B` — **Maximum number of images per Amazon Rekognition Custom Labels classification training dataset** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-970B5808` — **Transactions per second per account for the Amazon Rekognition Image operation ListFaces** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-973FFF99` — **Transactions per second per account for the Amazon Rekognition Image operation GetCelebrityInfo** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9802772B` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation StopProjectVersion** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-99829151` — **Transactions per second per account for the Amazon Rekognition Image operation SearchFaces** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-9A87C986` — **Transactions per second per account for the Amazon Rekognition operation: CreateUser** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A144FAD3` — **Transactions per second per account for the Amazon Rekognition Video stored video get operation GetCelebrityRecognition** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A33540CC` — **Transactions per second per account for the Amazon Rekognition Video stored video get operation GetContentModeration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A5121FD7` — **Transactions per second per account for the Amazon Rekognition Image operation DetectFaces** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A6079699` — **Concurrent Amazon Rekognition Video stored video jobs per account** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-A958BCFA` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation PutProjectPolicy** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AA48F869` — **Transactions per second per account for the Amazon Rekognition Video stored video start operation StartFaceDetection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AA6AE486` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation DeleteProjectPolicy** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AB95BCCD` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation CreateProject** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AD2642BA` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation: DistributeDatasetEntries** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-B82310D8` — **Maximum number of images per Amazon Rekognition Media Analysis job** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-BC04C31B` — **Transactions per second per account for the Amazon Rekognition operation: UntagResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BDE2ACBF` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation DeleteProject** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BF8F67AA` — **Transactions per second per account for the Amazon Rekognition operation: ListUsers** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C141F2F9` — **Transactions per second per account for the Amazon Rekognition operation: TagResource** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C46E6F2E` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation StartProjectVersion** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-C8E3347A` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation CopyProjectVersion** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CCFEF1AD` — **Maximum number of images per Amazon Rekognition Custom Labels classification test dataset** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-CE977716` — **Transactions per second per account for the Amazon Rekognition Image operation CreateCollection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-CF317234` — **Transactions per second per account for the Amazon Rekognition Streaming Video Events operation ListStreamProcessors** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D319BBAF` — **Transactions per second per account for the Amazon Rekognition operation: SearchUsersByImage** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D56ABB32` — **Transactions per second per account for the Amazon Rekognition operation: DisassociateFaces** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D6034D02` — **Transactions per second per account for the Amazon Rekognition Streaming Video Events operation CreateStreamProcessor** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D66335E5` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation DeleteProjectVersion** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D8895012` — **Maximum number of images per Amazon Rekognition Custom Labels detection training dataset** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-DBC0DD5B` — **Transactions per second per account for the Amazon Rekognition operation: AssociateFaces** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-DFE4726A` — **Transactions per second per account for the Amazon Rekognition Video stored video start operation StartPersonTracking** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E082B236` — **Transactions per second per account for the Amazon Rekognition Video stored video start operation StartContentModeration** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E0C6F70E` — **Transactions per second per account for the Amazon Rekognition operation: ListMediaAnalysisJobs** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E112E6C6` — **Transactions per second per account for the Amazon Rekognition operation: DeleteUser** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E29B542B` — **Transactions per second per account for the Amazon Rekognition Image operation DetectLabels** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EA71C84A` — **Transactions per second per account for individual Amazon Rekognition Custom Labels data plane operation DetectCustomLabels** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EEF61D56` — **Transactions per second per account for the Amazon Rekognition operation: GetMediaAnalysisJob** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-EF2DFA3A` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation: DescribeDataset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F54C1CEA` — **Transactions per second per account for the Amazon Rekognition Video stored video get operation GetSegmentDetection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F72BEA0D` — **Transactions per second per account for the Amazon Rekognition Custom Labels operation: DeleteDataset** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-FBD555BC` — **Transactions per second per account for the Amazon Rekognition Video stored video start operation StartLabelDetection** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `repostspace` (24 offene Quotas)

- `L-0B22FBC9` — **Token refill rate for SendInvites API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0E12E984` — **Token refill rate for ListTagsForResource API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-173CE406` — **Token refill rate for DeregisterAdmin API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-185C3A35` — **Standard private re:Post size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-291A9E46` — **Token refill rate for UpdateSpace API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-4311E6E0` — **Rate of CreateSpace API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-48DDB811` — **Token refill rate for ListSpaces API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5CA43569` — **Token refill rate for DeleteSpace API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5DA8E4B2` — **Rate of RegisterAdmin API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-5DF45BC4` — **Free private re:Post size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-69C945E4` — **Token refill rate for TagResource API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6E628E2D` — **Rate of TagResource API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-720B7455` — **Token refill rate for UntagResource API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-8AAF8EA2` — **Rate of DeleteSpace API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-95EAC37F` — **Rate of ListTagsForResource API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-99CE318E` — **Rate of UpdateSpace API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-A3894671` — **Rate of SendInvites API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AA78BA51` — **Rate of DeregisterAdmin API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-D8E09F48` — **Token refill rate for RegisterAdmin API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E307E23A` — **Token refill rate for GetSpace API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E494DB7F` — **Rate of GetSpace API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E68D3B02` — **Token refill rate for CreateSpace API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E9789367` — **Rate of ListSpaces API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F6573C98` — **Rate of UntagResource API requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `resiliencehub` (12 offene Quotas)

- `L-013E1BB6` — **Number of EKS clusters to import** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-05336C5D` — **Retention period of past assessments/recommendations in days** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-3275C9FD` — **Number of metric exports per month** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-37EF5CB4` — **Number of recommendation templates per application per month** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-3D296B58` — **Number of AWS CloudFormation stacks to import** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-4EBD1E5A` — **Number of Compliance Readiness Policies** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-63BA9671` — **Retention period of past recommendation templates in days** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-6BE17D5B` — **Number of namespaces to import for an EKS cluster** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-BF1D24DC` — **Number of assessments per application per month** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-CB78A3C3` — **Template size in bytes** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-CEF638A1` — **Number of Terraform state files to import** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-D41E7350` — **Terraform state file maximum size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.

## `resource-explorer-2` (1 offene Quota)

- `L-0C73063D` — **Search TPS quota** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `robomaker` (22 offene Quotas)

- `L-04ECBB71` — **Simulation Job Creation Rate Per Minute** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-0DED0FF4` — **Batch timeout** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-15E423AD` — **Concurrent deployment jobs** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-19B1F5F2` — **Fleets** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-275E9052` — **Robots per fleet** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-335D1CF0` — **Worlds Per Generation Job** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-3CD5069F` — **Source size** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-40FACCBF` — **Robots** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-4D288B5C` — **Versions per simulation application** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-61591119` — **Concurrent GPU simulation jobs** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-6CFB8C09` — **Concurrent simulation job batches** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-7651BB34` — **Concurrent World Generation Jobs** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-7E2BA58F` — **Simulation duration** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-925F020F` — **Minimum batch timeout** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-949954FD` — **Simulation job requests per batch** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-99FBC089` — **GPU Simulation Job Creation Rate Per Minute** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-AE5043DD` — **Versions per robot application** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-B47404F4` — **Concurrent World Export Jobs** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.
- `L-C2C8236B` — **World Templates Per Account** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-CEB47779` — **Minimum simulation duration** — `CONFIG_LIMIT`: Payload, configuration, retention, or capacity limit; no current resource count has the same unit or semantics.
- `L-D5AF2EE5` — **Worlds Per Export Job** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-FE0C173F` — **Concurrent simulation jobs** — `CONCURRENCY`: Concurrency or transient workload limit; list APIs cannot provide an authoritative current usage value for the quota.

## `rolesanywhere` (8 offene Quotas)

- `L-0017E049` — **Combined rate of CRL requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-19368711` — **CRLs per trust anchor** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-1A26F220` — **Combined rate of subject requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-471D7A75` — **Certificates per trust anchor** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-A9D9612A` — **Rate of CreateSession requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-BCE17F1C` — **Combined rate of tagging requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E7B077D9` — **Combined rate of trust anchor requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-F8680437` — **Combined rate of profile requests** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

## `route53resolver` (1 offene Quota)

- `L-1B2BDF0A` — **Domains in a file imported from S3** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `rtbfabric` (5 offene Quotas)

- `L-0D7BE865` — **Subnets per gateway** — `RESOURCE_MAPPING`: Resource-like quota; no unambiguous paginated API-to-quota mapping is registered for this service/quota code, so deriving a count could produce a misleading measurement.
- `L-4CB472F0` — **Transactions per second (TPS) per inbound or outbound external link** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-6149EBBA` — **External outbound links supported** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.
- `L-93F89653` — **Transactions per second (TPS) per link** — `USAGE_METRIC`: Request/throughput rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-E93A25F4` — **External inbound links supported** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

## `rum` (1 offene Quota)

- `L-35851224` — **RUM Events per second per AWS Account** — `UNSUPPORTED`: No local inventory or official UsageMetric mapping was found for this quota in the catalog and registered checks.

