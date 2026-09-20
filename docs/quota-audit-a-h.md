# Restkatalog-Audit A–H

Der lokale Service-Quotas-Katalog wurde vollständig gegen die registrierten Checks geprüft. Jeder offene Quota-Code wird unten einzeln aufgeführt. Rate-, Kapazitäts-, Größen-, Laufzeit- und nicht eindeutig abbildbare Parent-Limits bleiben bewusst `UNSUPPORTED`; eindeutig paginierbare Resource Counts werden implementiert.

# Open quota audit A–H

Total open entries: **2172**


## access-analyzer

- `L-4599575C` — Concurrent policy generations
- `L-5EFCE71D` — CloudTrail log files processed per policy generation
- `L-8750DAE0` — Access previews per analyzer per hour
- `L-94099EDD` — Policy generation CloudTrail data size
- `L-96F55078` — Policy generation CloudTrail time range
- `L-FD4CD927` — Policy generations per day

## acm

- `L-3808DC70` — Imported certificates in last 365 days
- `L-DA1D8B98` — ACM certificates created in last 365 days
- `L-FB94F0B0` — Domain names per ACM certificate

## acm-pca

- `L-01B8608D` — Rate of CreateCertificateAuthority requests
- `L-0CD1C07A` — Rate of UntagCertificateAuthority requests
- `L-1725E639` — Rate of GetCertificate requests
- `L-20AFF03D` — Rate of ListPermissions requests
- `L-3549B861` — Rate of GetPolicy requests
- `L-4065FDCB` — Rate of DeleteCertificateAuthority requests
- `L-46ADAC63` — Rate of DescribeCertificateAuthority requests
- `L-506CC328` — Rate of PutPolicy requests
- `L-511291FD` — Rate of DeletePermission requests
- `L-5A3CF806` — Rate of ListCertificateAuthorities requests
- `L-5D3ECC67` — Number of private certificates for each CA
- `L-6C533034` — Rate of GetCertificateAuthorityCertificate requests
- `L-6C9448CC` — Rate of DescribeCertificateAuthorityAuditReport requests
- `L-773738D3` — Rate of CreatePermission requests
- `L-7D3D103D` — Rate of GetCertificateAuthorityCsr requests
- `L-8842A328` — Rate of RevokeCertificate requests
- `L-8FDDE81D` — Rate of UpdateCertificateAuthority requests
- `L-AF91D77C` — Rate of ListTags requests
- `L-C0A08797` — Rate of CreateCertificateAuthorityAuditReport requests
- `L-CAFB4993` — Rate of IssueCertificate requests
- `L-D0C21409` — Rate of ImportCertificateAuthorityCertificate requests
- `L-DFF54388` — Number of revoked private certificates for each CA with complete CRLs enabled
- `L-E464E2C8` — Rate of TagCertificateAuthority requests
- `L-F3EBB4C3` — Rate of RestoreCertificateAuthority requests
- `L-F4B48431` — Rate of DeletePolicy requests
- `L-F99AB81B` — Number of private certificates for each CA using complete CRLs

## aiops

- `L-4CD81CD5` — Monthly investigations
- `L-5EC19707` — Investigation groups
- `L-EF31E0C4` — Concurrent active investigations

## airflow

- `L-4BA0CB82` — Larger environments per account per Region (xlarge, 2xlarge)
- `L-52DCDA32` — Web servers per environment
- `L-78AC1883` — Workers per environment

## amplify

- `L-2A8ABB91` — Concurrent jobs
- `L-2FC3A2FA` — Maximum app creations per hour
- `L-85685B2E` — Subdomains per domain
- `L-895E890C` — Build artifact size
- `L-A0FC4951` — Environment cache artifact size
- `L-CE88B60E` — Request tokens per second
- `L-D95E5509` — Manual deploy ZIP file size
- `L-EC4C0FC7` — Cache artifact size

## amplifyuibuilder

- `L-E4AD9560` — Views per app: the SDK ships no view listing. The client offers
  only `ListCodegenJobs`, `ListComponents`, `ListForms`, `ListTagsForResource`
  and `ListThemes`, so there is no inventory to count.
- `L-4FE3AB63` — Component size
- `L-A25B72F2` — Form size
- `L-CA57203B` — View size
- `L-D500C0BA` — Theme size

## apigateway

- `L-20859C74` — AWS Lambda authorizer result size
- `L-3A613F94` — Stage Variable Key Length
- `L-46624B39` — API Payload Size
- `L-5244589D` — Method ARN Length
- `L-60AC41CD` — WebSocket Idle Connection Timeout
- `L-8A5B8E43` — Throttle rate
- `L-8B81B02C` — Maximum resource policy size in bytes
- `L-8C2F9A1D` — Maximum API caching TTL
- `L-8E6A5A87` — Maximum Iterations In Mapping Template
- `L-9C147DE4` — Edge API URL Length
- `L-9ED1E49A` — WebSocket new connections rate
- `L-A6CCE716` — Connection duration for WebSocket API
- `L-A7033131` — Regional API URL Length
- `L-B2CF62DC` — Stage Variable Value Length
- `L-CC2525B6` — Maximum Cached Response Size
- `L-CDF5615A` — Throttle burst rate
- `L-E11F7D5D` — WebSocket frame size
- `L-E1465507` — WebSocket new connections burst rate
- `L-E5AE38E3` — Maximum integration timeout in milliseconds
- `L-E9EEB922` — Maximum Combined Header Size
- `L-FD0EB744` — WebSocket message payload size

## app-integrations

- `L-060921B0` — GetDataIntegration rate quota
- `L-07582D55` — DeleteApplication rate quota
- `L-10F823E6` — UpdateEventIntegration rate quota
- `L-13BD4910` — UpdateApplication rate quota
- `L-1DA717FF` — UpdateApplication burst quota
- `L-1EE39104` — ListTagsForResource burst quota
- `L-226FBD21` — TagResource rate quota
- `L-2377BC54` — CreateDataIntegration rate quota
- `L-259B8C8C` — DeleteApplication burst quota
- `L-25C641A6` — DeleteEventIntegration burst quota
- `L-2BC013CC` — ListApplications burst quota
- `L-2D5AAB01` — DeleteDataIntegration rate quota
- `L-2E8BE8F8` — ListEventIntegrations rate quota
- `L-3D290D13` — UpdateEventIntegration burst quota
- `L-3D345023` — ListEventIntegrationAssociations rate quota
- `L-4244482D` — ListEventIntegrations burst quota
- `L-4544738C` — ListApplications rate quota
- `L-460DAB40` — DeleteDataIntegration burst quota
- `L-4762EDD4` — CreateApplication burst quota
- `L-5B65DD22` — ListDataIntegrations burst quota
- `L-5D46E37D` — ListDataIntegrationAssociations rate quota
- `L-5FA3019D` — UpdateDataIntegration burst quota
- `L-5FEEEA91` — GetDataIntegration burst quota
- `L-6968951A` — UpdateDataIntegration rate quota
- `L-7169D3B6` — CreateDataIntegration burst quota
- `L-7B44E10B` — ListEventIntegrationAssociations burst quota
- `L-8606E8AE` — CreateEventIntegration burst quota
- `L-933331A4` — GetEventIntegration burst quota
- `L-9A23D5EA` — UntagResource burst quota
- `L-9D7D12D1` — GetApplication rate quota
- `L-A13B7A8E` — CreateApplication rate quota
- `L-A95BD014` — ListDataIntegrationAssociations burst quota
- `L-AC0948D4` — UntagResource rate quota
- `L-B15BD2F7` — GetEventIntegration rate quota
- `L-BE476A66` — ListTagsForResource rate quota
- `L-BFEE2250` — ListDataIntegrations rate quota
- `L-D1B8F8B6` — GetApplication burst quota
- `L-D22B0B1B` — CreateEventIntegration rate quota
- `L-DECE3419` — ListApplicationAssociations burst quota
- `L-E03AF6AA` — TagResource burst quota
- `L-EBE739FE` — ListApplicationAssociations rate quota
- `L-F3E11209` — DeleteEventIntegration rate quota

## appconfig

- `L-48F9B951` — Configuration size limit in AWS AppConfig hosted configuration store
- `L-A5FC0339` — Deployment size limit

## appflow

- `L-08C0216C` — Rate of Salesforce flow runs
- `L-0F498C1E` — Amazon EventBridge event size
- `L-120EC365` — Salesforce event size
- `L-1C312742` — Rate of Marketo flow runs
- `L-31313F92` — Rate of Slack flow runs
- `L-5BA24048` — Rate of TrendMicro flow runs
- `L-72533C43` — Rate of Veeva flow runs
- `L-787B0C0A` — ServiceNow records
- `L-7A25FF64` — Rate of Amazon AppFlow flow runs
- `L-7B39106B` — Salesforce flow run data export size
- `L-82E46C0E` — Amplitude flow run size
- `L-83886F7C` — Rate of Amazon S3 flow runs
- `L-8D48E59D` — Marketo flow run size
- `L-AB51459B` — Rate of ServiceNow flow runs
- `L-ABFA35F9` — Rate of Salesforce Pardot flow runs
- `L-B2798F93` — Concurrent flow runs
- `L-B83E07B6` — Rate of Singular flow runs
- `L-B96D9407` — Monthly flow runs
- `L-B9D35708` — Rate of Zendesk flow runs
- `L-C2298606` — Google Analytics metrics
- `L-CB07633A` — Google Analytics dimensions
- `L-D365AAEF` — Amazon AppFlow flow run size
- `L-DC8DB590` — Rate of Google Analytics flow runs
- `L-DF14FA4F` — Rate of Datadog flow runs
- `L-E4F85654` — Rate of Dynatrace flow runs
- `L-F2770EE5` — Salesforce flow run data import size
- `L-F3D880AA` — Rate of Infor Nexus flow runs
- `L-FE9BF330` — Rate of Amplitude flow runs

## application-signals

- `L-2C8EDAF0` — Rate of PutGroupingConfiguration requests
- `L-660777C0` — Number of SLOs per Service
- `L-692A17A9` — Rate of GetServiceLevelObjective requests
- `L-6BBF1A92` — Rate of ListServices requests
- `L-715DC88B` — Rate of ListServiceStates requests
- `L-7A03F44C` — Rate of ListGroupingAttributeDefinitions requests
- `L-7A9D456C` — Rate of UntagResource requests
- `L-7AB759D6` — Rate of UpdateServiceLevelObjective requests
- `L-7F8DB46D` — Rate of ListServiceDependents requests
- `L-A1810D82` — Rate of ListServiceLevelObjectiveExclusionWindows requests
- `L-A3B40D72` — Rate of ListServiceDependencies requests
- `L-A755C830` — Rate of BatchUpdateExclusionWindows requests
- `L-A7EC90F1` — Rate of GetService requests
- `L-B4EFDB9E` — Rate of ListServiceLevelObjectives requests
- `L-B7AF0347` — Rate of DeleteGroupingConfiguration requests
- `L-BC1D91EF` — Rate of CreateServiceLevelObjective requests
- `L-C48E6360` — Rate of BatchGetServiceLevelObjectiveBudgetReport requests
- `L-CD5EC149` — Rate of ListServiceOperations requests
- `L-D898488F` — Rate of ListAuditFindings requests
- `L-E65D4614` — Rate of ListTagsForResource requests
- `L-EA133927` — Rate of DeleteServiceLevelObjective requests
- `L-EB837E0B` — Rate of StartDiscovery requests
- `L-FCC0FB4B` — Rate of TagResource requests

## appmesh

- `L-33E8F9C9` — Connected Envoy processes per virtual gateway
- `L-606A910B` — Connected Envoy processes per virtual node

## appstream2

- `L-7549EFF1` — Graphics desktop 2xlarge streaming instances for fleets
- `L-9B6418E0` — Concurrent image updates
- `L-B3B2E1D8` — Graphics desktop 2xlarge streaming instances for image builders

## appsync

- `L-10498098` — Event APIs - Rate of connections per API
- `L-16CCBB05` — Event APIs - Publish payload size
- `L-1BB7D45F` — All APIs - Resolvers, functions, and handlers response size
- `L-27770490` — Event APIs - Rate of request tokens
- `L-352DA8E7` — GraphQL APIs - Schema document size
- `L-4456C49D` — Graphql APIs - Rate of subscription invalidation requests
- `L-4DE70025` — All APIs - Handler, resolver, and function code size
- `L-51A37BC6` — All APIs - Number of custom domain names
- `L-5684A2A5` — All APIs - Iterations per loops in resolvers, functions, and handlers
- `L-58A9E1D6` — GraphQL APIs - Number of caching keys
- `L-5DE70651` — GraphQL APIs - Rate of outbound messages per API
- `L-629488CF` — All APIs - Request execution time
- `L-69193794` — GraphQL APIs - Max Batch Size per request
- `L-7DE80FA2` — Event APIs - Number of segments allowed in a channel
- `L-7FC6D61A` — GraphQL APIs - Request mapping template size
- `L-97EB21C3` — GraphQL APIs - Resolvers executed in a single request
- `L-A1B022A0` — GraphQL APIs - Rate of inbound messages per API
- `L-A1CF8F5B` — Event APIs - Number of characters allowed in a channel segment
- `L-AA33EB36` — All APIs - Subscriptions per client connection
- `L-B6E463BF` — Event APIs - Batch size per publish request
- `L-B94CDCB7` — GraphQL APIs - Response mapping template size
- `L-C01DB6E6` — GraphQL APIs - Rate of connections per API
- `L-D33F7C2A` — Event APIs - Rate of publish requests per client connection
- `L-D91E563A` — Event APIs - Rate of inbound events per API
- `L-F21064F0` — All APIs - Subscription payload size
- `L-F643C244` — Event APIs - Rate of outbound messages per API
- `L-FC5E46D0` — GraphQL APIs - Rate of request tokens

## aps

- `L-0F151AA2` — Templates in alert manager definition file
- `L-110BFC6B` — HA tracker clusters
- `L-140BEF25` — Query bytes for instant queries
- `L-2551415B` — Query time range in days
- `L-2C2449DB` — LabelSet limits per workspace
- `L-3316EF76` — Alert manager definition file size
- `L-3D15CDB4` — Rules per workspace
- `L-3E2A717A` — Alert payload size in Alert Manager
- `L-40DA9328` — Active metrics with metadata per workspace
- `L-4340E931` — Number of RemoteWrite API operations per workspace in transactions per second
- `L-44FE2FA3` — Query bytes for range queries
- `L-469A77CF` — Metadata per metric
- `L-46D5E194` — Inhibition rules in alert manager definition file
- `L-4D4AB00D` — Query series fetched
- `L-5A151448` — Active series per workspace
- `L-8491EB93` — Number of API operations per region in transactions per second
- `L-8DEDEE8E` — Rule evaluation interval
- `L-8E142053` — Label size
- `L-AA9AE19E` — Number of other Prometheus-compatible API operations per workspace in transactions per second
- `L-B71C1602` — Request size
- `L-BDF9895D` — Alert aggregation group size in alert manager definition file
- `L-C15FCA36` — Silences per workspace
- `L-C62641E3` — Rule group namespace definition file size
- `L-CDA4AB0F` — Labels per metric series
- `L-D01F3F3F` — Query samples
- `L-D5FD0534` — Number of QueryMetrics API operations per workspace in transactions per second
- `L-E3E60B3E` — Nodes in alert manager routing tree
- `L-E9CD1A4F` — Alerts in Alert Manager
- `L-ECC75BFE` — Metadata length
- `L-F4BCE0BA` — Ingestion rate per workspace
- `L-F6DD1217` — Number of GetSeries, GetLabels and GetMetricMetadata API operations per workspace in transactions per second

## athena

- `L-076245C0` — Replenishment rate of BatchGetNamedQuery API calls
- `L-07F4444F` — Replenishment rate of GetQueryResults API calls
- `L-0F303755` — Burst multiplier quota for StopQueryExecution API
- `L-136E993A` — Burst multiplier quota for DeleteNamedQuery API
- `L-3702C1C1` — Burst multiplier quota for GetQueryResults API
- `L-3CE0BBA0` — Active DDL queries
- `L-41075247` — Replenishment rate of DeleteNamedQuery API calls
- `L-4FF11DD3` — Replenishment rate of StartQueryExecution API calls
- `L-52EFA794` — Replenishment rate of BatchGetQueryExecution API calls
- `L-56A94400` — DDL query timeout
- `L-5A8D5237` — Apache Spark DPU concurrency
- `L-70FD91F7` — Replenishment rate of ListQueryExecutions API calls
- `L-722F8D5C` — Burst multiplier quota for StartQueryExecution API
- `L-76AFE6F2` — Replenishment rate of CreateNamedQuery API calls
- `L-7A12A1E6` — Burst multiplier quota for CreateNamedQuery API
- `L-82E47245` — Replenishment rate of ListNamedQueries API calls
- `L-9D86AA19` — Replenishment rate of GetQueryExecution API calls
- `L-A6257554` — Burst multiplier quota for ListNamedQueries API
- `L-AC64E3A0` — Burst multiplier quota for BatchGetNamedQuery API
- `L-C60BEAE0` — Burst multiplier quota for GetQueryExecution API
- `L-CC64F7CE` — Burst multiplier quota for GetNamedQuery API
- `L-D0D8C912` — Replenishment rate of GetNamedQuery API calls
- `L-D8C0E3AF` — Burst multiplier quota for BatchGetQueryExecution API
- `L-E80DC288` — DML query timeout
- `L-EFB619E3` — Replenishment rate of StopQueryExecution API calls
- `L-FC5F6546` — Active DML queries
- `L-FE3693EE` — Burst multiplier quota for ListQueryExecutions API

## backup

- `L-C0A8C14B` — Maximum backup nest level
- `L-FB1D55EC` — Metadata tags per backup

## batch

- `L-0194C9AB` — Transactions per second for SubmitServiceJob
- `L-65F8BA2C` — Submitted state jobs limit
- `L-6B86CF1E` — Job payload size limit
- `L-A2F30F35` — Service Job serviceRequestPayload size
- `L-AD075A76` — Job dependencies limit
- `L-B15D0E72` — Service Job total payload size
- `L-E6A2743D` — Job definition size limit
- `L-E985971C` — Transactions per second for SubmitJob limit
- `L-F9381E33` — Maximum array size limit

## bedrock

- `L-007D91B8` — Batch inference job size for Qwen3 Coder 480B (in GB)
- `L-00CA92AA` — Minimum number of records per batch inference job for Qwen3 Coder 30B
- `L-00DFDB26` — (Knowledge Bases) RetrieveAndGenerateStream requests per second
- `L-01F37E14` — Model units per provisioned model for Cohere Command Light
- `L-01F3CD81` — (Guardrails) On-demand ApplyGuardrail Content filter policy text units per second
- `L-02D6293C` — Batch inference job size (in GB) for Claude 3.7 Sonnet
- `L-02D831F1` — On-demand model inference tokens per minute for Mistral AI Mistral 7B Instruct
- `L-02DB18B4` — Records per input file per batch inference job for Claude Sonnet 4
- `L-02DFBB76` — Global cross-region model inference tokens per minute for Cohere Embed V4
- `L-036E14D8` — On-demand model inference tokens per minute for OpenAI GPT OSS 20B
- `L-0406044C` — (Model customization) Scheduled customization jobs
- `L-0451886A` — CreateAgentActionGroup requests per second
- `L-0495104E` — (Knowledge Bases) User query size
- `L-04F1DD0C` — (Prompt management) DeletePrompt requests per second
- `L-052AA08C` — Batch inference job size (in GB) for OpenAI GPT OSS 120b
- `L-05E453B4` — GetAgentActionGroup requests per second
- `L-067F7E01` — Batch inference input file size (in GB) for Claude 3 Sonnet
- `L-0700C8EB` — On-demand model inference requests per minute for Meta Llama 2 13B
- `L-072E11FC` — Records per batch inference job for Mistral Small
- `L-07D73971` — (Automated Reasoning) StartAutomatedReasoningPolicyTestWorkflow requests per second
- `L-086556D1` — (Guardrails) On-demand ApplyGuardrail contextual grounding policy text units per second
- `L-091522BC` — (Flows) PrepareFlow requests per second
- `L-09A792C8` — Records per batch inference job for Qwen3 32B
- `L-0ABA0A81` — (Prompt management) CreatePromptVersion requests per second
- `L-0B2687F4` — Cross-region model inference tokens per minute for Meta Llama 3.2 3B Instruct
- `L-0C5F7593` — Sum of in-progress and submitted batch inference jobs using a base model for DeepSeek v3
- `L-0C92D61A` — (Data Automation) Maximum Levels of Field Hierarchy
- `L-0CB120A9` — (Automated Reasoning) GetAutomatedReasoningPolicyAnnotations requests per second
- `L-0D428547` — Batch inference input file size for Qwen3 235B (in GB)
- `L-0DD4EC92` — (Knowledge Bases) Rerank requests per second
- `L-0DF688AB` — Throttle rate limit for InvokeDataAutomationAsync
- `L-0E3D7CF9` — Throttle rate limit for CreateDataAutomationProject
- `L-0E729086` — Batch inference input file size (in GB) for Claude 3 Opus
- `L-0E8CAF89` — (Data Automation) Maximum audio file size (MB)
- `L-0EA49C8E` — (Flows) CreateFlowVersion requests per second
- `L-0EF69BEA` — Batch inference input file size (in GB) for OpenAI GPT OSS 20b
- `L-0F052E16` — Batch inference job size (in GB) for Mistral Small
- `L-0FA1782C` — Model invocation max tokens per day for OpenAI GPT OSS 20B (doubled for cross-region calls)
- `L-1074C53D` — Model units per provisioned model for Amazon Titan Text Embeddings V2
- `L-10AE7314` — Throttle rate limit for ListDataAutomationProjects
- `L-10DE37DB` — GetAgentAlias requests per second
- `L-11512E58` — On-demand model inference requests per minute for Cohere Rerank 3.5
- `L-124DCF3D` — (Guardrails) On-demand ApplyGuardrail Denied topic policy text units per second
- `L-166C69FA` — DeleteAgentAlias requests per second
- `L-16E25672` — Records per batch inference job for Claude 3 Sonnet
- `L-17F95AA4` — On-demand model inference tokens per minute for Cohere Command R
- `L-185CB521` — Minimum number of records per batch inference job for Llama 3.2 3B Instruct
- `L-1870BD3C` — Model units per provisioned model for Cohere Embed Multilingual
- `L-19329652` — (Data Automation) Maximum number of Blueprints per Start Inference request (Videos)
- `L-19E52681` — Batch inference job size (in GB) for Nova Lite V1
- `L-1A69C08F` — Minimum number of records per batch inference job for Titan Multimodal Embeddings G1
- `L-1C81957C` — Throttle rate limit for GetDataAutomationProject
- `L-1CF3E033` — Batch inference input file size (in GB) for Llama 3.1 70B Instruct
- `L-1D3E59A3` — Cross-Region model inference requests per minute for Anthropic Claude 3.5 Sonnet V2
- `L-1DA9F79C` — (Data Automation) InvokeEntityIngestionAsync - Person - Max number of tokens
- `L-1E0DA3DF` — Minimum number of records per batch inference job for Claude 3.5 Sonnet
- `L-1E2B9998` — Records per batch inference job for Claude 3.5 Sonnet
- `L-1E9F6637` — (Flows) DeleteFlowAlias requests per second
- `L-1EC9C5DF` — Minimum number of records per batch inference job for Llama 3.1 70B Instruct
- `L-1EFED863` — (Data Automation) (Console) Maximum document file size (MB)
- `L-1F644C2A` — Records per batch inference job for Claude 3 Haiku
- `L-1FA30AE7` — Minimum number of records per batch inference job for Claude 3.5 Sonnet v2
- `L-1FC48CF3` — UpdateAgentActionGroup requests per second
- `L-209848DD` — (Data Automation) Maximum number of list fields per Blueprint
- `L-20CFCD61` — On-demand model inference requests per minute for Meta Llama 3.2 1B Instruct
- `L-21D1371E` — GetAgentKnowledgeBase requests per second
- `L-224F3DE4` — (Knowledge Bases) Files to add or update per ingestion job
- `L-229A5DEC` — Global cross-region model inference tokens per day for Anthropic Claude Sonnet 4.5 V1 1M Context Length
- `L-22F701C5` — Model invocation max tokens per day for Anthropic Claude Sonnet 4 V1 (doubled for cross-region calls)
- `L-240F3183` — Model units per provisioned model for Stability.ai Stable Diffusion XL 0.8
- `L-247B684D` — On-demand model inference tokens per minute for Meta Llama 2 70B
- `L-254CACF4` — On-demand model inference requests per minute for Anthropic Claude 3.5 Sonnet
- `L-25B50707` — On-demand model inference requests per minute for OpenAI GPT OSS 120B
- `L-268D592E` — Model units per provisioned model for Meta Llama 2 13B
- `L-26B15D4D` — Batch inference job size (in GB) for Nova Pro V1
- `L-26BB089C` — (Flows) ListFlowAliases requests per second
- `L-26C560CE` — On-demand model inference requests per minute for Amazon Titan Text Embeddings V2
- `L-273A0D03` — Throttle rate limit for DeleteDataAutomationProject
- `L-274AA31F` — Records per batch inference job for Claude 3.5 Haiku
- `L-27C57EE8` — Global cross-region model inference tokens per minute for Anthropic Claude Sonnet 4.5 V1
- `L-295FBA3E` — Records per input file per batch inference job for Qwen3 235B
- `L-29998DC2` — (Knowledge Bases) Ingestion job size
- `L-2A3EB975` — Minimum number of records per batch inference job for Nova Pro V1
- `L-2B715ABD` — On-demand model inference tokens per minute for Amazon Titan Image Generator G1
- `L-2BB465D6` — (Flows) UpdateFlow requests per second
- `L-2BC3F4E3` — (Flows) GetFlowAlias requests per second
- `L-2D7A58CF` — PrepareAgent requests per second
- `L-2DC80978` — On-demand model inference requests per minute for Anthropic Claude 3 Haiku
- `L-2EBEF050` — Model units per provisioned model for Meta Llama 2 70B
- `L-2F9B4FC2` — On-demand model inference requests per minute for Meta Llama 3.2 3B Instruct
- `L-2FE3C16F` — (Knowledge Bases) CreateKnowledgeBase requests per second
- `L-31EB70D1` — Throttle rate limit for CreateBlueprint
- `L-320F5AFC` — Batch inference job size (in GB) for Claude 3 Opus
- `L-32F732DE` — Model units per provisioned model for Amazon Titan Multimodal Embeddings G1
- `L-345B029F` — (Automated Reasoning) DeleteAutomatedReasoningPolicyTestCase requests per second
- `L-36AE5758` — (Knowledge Bases) Maximum number of files for Foundation Models as a parser
- `L-37B69F3F` — Batch inference input file size for Qwen3 32B (in GB)
- `L-381AD9EE` — Model invocation max tokens per day for Anthropic Claude Sonnet 4.5 V1 (doubled for cross-region calls)
- `L-3849F0B7` — On-demand model inference requests per minute for Stability.ai Stable Diffusion XL 0.8
- `L-3875BCCF` — On-demand model inference tokens per minute for Qwen3 235B a22b 2507 V1
- `L-39FA8DCA` — Minimum number of records per batch inference job for Nova Lite V1
- `L-3A7ED9C0` — Batch inference job size (in GB) for Llama 3.3 70B Instruct
- `L-3B3BFACF` — On-demand model inference requests per minute for Cohere Command
- `L-3B82104D` — (Model customization) Sum of training and validation records for a Titan Text G1 - Lite v1 Fine-tuning job
- `L-3BD2251E` — Records per batch inference job for Titan Multimodal Embeddings G1
- `L-3C5D1B25` — Records per batch inference job for OpenAI GPT OSS 120b
- `L-3CAACDCF` — Batch inference input file size for Titan Text Embeddings V2 (in GB)
- `L-3D8CC480` — Cross-region model inference requests per minute for Anthropic Claude 3.7 Sonnet V1
- `L-3E961CAB` — (Data Automation) InvokeDataAutomationAsync - Audio - Max number of concurrent jobs
- `L-3F0ECEDC` — Model units per provisioned model for AI21 Labs Jurassic-2 Ultra
- `L-3F110E0F` — Cross-region model inference requests per minute for Amazon Nova Micro
- `L-4090E58E` — Batch inference job size (in GB) for Llama 3.2 3B Instruct
- `L-409754A1` — (Knowledge Bases) IngestKnowledgeBaseDocuments requests per second
- `L-41FDDA6B` — Model invocation max tokens per day for OpenAI GPT OSS 120B (doubled for cross-region calls)
- `L-41FFF7F7` — UpdateAgent requests per second
- `L-42ABE687` — Batch inference input file size (in GB) for Claude 3 Haiku
- `L-447BB329` — Batch inference input file size (in GB) for Titan Multimodal Embeddings G1
- `L-44992E63` — On-demand model inference tokens per minute for Amazon Titan Text Express
- `L-454B6C93` — (Knowledge Bases) Ingestion job file size
- `L-46591118` — Cross-region model inference requests per minute for Anthropic Claude 3 Sonnet
- `L-46BC975A` — (Prompt management) CreatePrompt requests per second
- `L-4777C575` — (Data Automation) Maximum video length (Minutes)
- `L-478319B0` — Records per input file per batch inference job for Llama 3.2 1B Instruct
- `L-479B647F` — Cross-region model inference tokens per minute for Anthropic Claude 3.5 Sonnet
- `L-4821684D` — Records per batch inference job for Llama 3.2 90B Instruct
- `L-490F4D1F` — On-demand model inference tokens per minute for Mistral AI Mixtral 8X7BB Instruct
- `L-4A6BFAB1` — Cross-region model inference requests per minute for Anthropic Claude Sonnet 4.5 V1
- `L-4A6D2F15` — Model units per provisioned model for Anthropic Claude Instant V1 100K
- `L-4B244563` — Minimum number of records per batch inference job for OpenAI GPT OSS 120b
- `L-4B26E44A` — Global cross-region model inference tokens per minute for Anthropic Claude Sonnet 4.5 V1 1M Context Length
- `L-4B9F76B0` — Cross-region model inference tokens per minute for Mistral Pixtral Large 25.02 V1
- `L-4C35BB2A` — On-demand model inference tokens per minute for Anthropic Claude 3 Sonnet
- `L-4C3F0FE6` — Cross-region model inference tokens per minute for Cohere Embed V4
- `L-4C584163` — Batch inference job size (in GB) for Titan Multimodal Embeddings G1
- `L-4CB86209` — Throttle rate limit for Bedrock Data Automation Runtime: ListTagsForResource
- `L-4CD00D47` — (Data Automation) Maximum Audio Sample Rate (Hz)
- `L-4DBDD5C9` — (Automated Reasoning) GetAutomatedReasoningPolicy requests per second
- `L-4E7EE0B5` — Sum of in-progress and submitted batch inference jobs using a base model for Claude 3.5 Sonnet
- `L-4E833B8F` — On-demand model inference tokens per minute for Cohere Command
- `L-50C45667` — (Knowledge Bases) ListKnowledgeBaseDocuments requests per second
- `L-50E31465` — (Data Automation) Maximum document file size (MB)
- `L-51B0DEE7` — Records per input file per batch inference job for Llama 3.2 90B Instruct
- `L-51CDA0E1` — (Automated Reasoning) DeleteAutomatedReasoningPolicy requests per second
- `L-529EC606` — (Knowledge Bases) UpdateKnowledgeBase requests per second
- `L-534E6885` — Minimum number of records per batch inference job for Nova Micro V1
- `L-539B5996` — Minimum number of records per batch inference job for Llama 3.2 1B Instruct
- `L-548A1A32` — On-demand model inference requests per minute for Qwen3 235B a22b 2507 V1
- `L-54CA9AAA` — (Knowledge Bases) DeleteKnowledgeBaseDocuments requests per second
- `L-5594A7BA` — Batch inference job size (in GB) for OpenAI GPT OSS 20b
- `L-559DCC33` — Cross-region model inference requests per minute for Anthropic Claude Sonnet 4 V1
- `L-55C9AD31` — Throttle rate limit for ListBlueprints
- `L-5618D36B` — (Guardrails) Contextual grounding query length in text units
- `L-5755FAB6` — (Guardrails) On-demand ApplyGuardrail Denied topic policy text units per second (standard)
- `L-57DC56A1` — Records per batch inference job for Nova Micro V1
- `L-5818283A` — Minimum number of records per batch inference job for Qwen3 Coder 480B
- `L-58BE175A` — Cross-region model inference tokens per minute for Anthropic Claude Haiku 4.5
- `L-59759B4A` — Cross-region model inference tokens per minute for Anthropic Claude Sonnet 4 V1
- `L-5A222661` — (Model customization) Sum of training and validation records for a Meta Llama 2 70B v1 Fine-tuning job
- `L-5AB0EE48` — Records per input file per batch inference job for Claude 3.5 Sonnet
- `L-5BF45557` — Minimum number of records per batch inference job for Llama 3.2 11B Instruct
- `L-5CBDB5BC` — Batch inference input file size (in GB) for Claude 3.5 Sonnet v2
- `L-5D07A961` — Minimum number of records per batch inference job for OpenAI GPT OSS 20b
- `L-5DD391B1` — (Automated Reasoning) ListAutomatedReasoningPolicyTestCases requests per second
- `L-5DF13F64` — Cross-region model inference tokens per minute for Anthropic Claude 3 Sonnet
- `L-5E04C7E2` — (Knowledge Bases) ListDataSources requests per second
- `L-5E29F315` — Model units per provisioned model for Cohere Command
- `L-5EBE3E09` — (Knowledge Bases) CreateDataSource requests per second
- `L-6120CF2D` — Model invocation max tokens per day for Anthropic Claude Haiku 4.5 (doubled for cross-region calls)
- `L-616A3F5B` — Cross-region model inference requests per minute for Anthropic Claude 3 Haiku
- `L-6284B54D` — Batch inference job size (in GB) for Claude 3.5 Sonnet
- `L-62A27283` — Throttle rate limit for CreateBlueprintVersion
- `L-6326A422` — (Automated Reasoning) CreateAutomatedReasoningPolicy requests per second
- `L-640FAA80` — (Data Automation) Description length for fields (Characters)
- `L-642905B5` — Records per input file per batch inference job for Claude 3 Opus
- `L-66EE6E0B` — On-demand model inference requests per minute for Qwen3 Coder 30B a3b V1
- `L-674F42D5` — Cross-region model inference requests per minute for Mistral Pixtral Large 25.02 V1
- `L-674F621D` — On-demand model inference requests per minute for Meta Llama 2 Chat 13B
- `L-67BD0D49` — Sum of in-progress and submitted batch inference jobs using a base model for Claude 3 Sonnet
- `L-68AE6C02` — (Model customization) Sum of training and validation records for a Meta Llama 2 13B v1 Fine-tuning job
- `L-68FC8D47` — Batch inference input file size (in GB) for Nova Pro V1
- `L-69B1E2CD` — (Data Automation) Maximum number of Blueprints per Start Inference request (Images)
- `L-6B0A9FAD` — Cross-region model inference requests per minute for Meta Llama 3.2 3B Instruct
- `L-6B20E60F` — DeleteAgentVersion requests per second
- `L-6B2DA87E` — APIs per Agent
- `L-6B3D3DE4` — (Guardrails) On-demand ApplyGuardrail Content filter policy text units per second (standard)
- `L-6C3B9A50` — (Knowledge Bases) ListIngestionJobs requests per second
- `L-6DB35E51` — On-demand model inference tokens per minute for Meta Llama 2 Chat 13B
- `L-6E3CDA2D` — Characters in Agent instructions
- `L-6E888CC2` — Cross-region model inference tokens per minute for Anthropic Claude 3.7 Sonnet V1
- `L-6EBFEB27` — Records per batch inference job for Claude 3.5 Sonnet v2
- `L-6F139B4D` — (Guardrails) Contextual grounding response length in text units
- `L-6F14193C` — On-demand model inference tokens per minute for Meta Llama 3.2 1B Instruct
- `L-6F2B2616` — Minimum number of records per batch inference job for Titan Text Embeddings V2
- `L-707418DE` — CreateAgent requests per second
- `L-70876FA2` — (Evaluation) Size of prompt
- `L-7089DC7D` — Global cross-region model inference requests per minute for Cohere Embed V4
- `L-70AD2F8F` — Throttle rate limit for Bedrock Data Automation Runtime: UntagResource
- `L-70BE83E9` — On-demand model inference tokens per minute for Amazon Titan Text Lite
- `L-712788A5` — GetAgent requests per second
- `L-7150BC56` — (Knowledge Bases) DeleteKnowledgeBase requests per second
- `L-721735BA` — (Evaluation) Number of prompts in a custom prompt dataset
- `L-7334E629` — (Automated Reasoning) CancelAutomatedReasoningPolicyBuildWorkflow requests per second
- `L-73573F44` — Model units per provisioned model for Anthropic Claude V2 18K
- `L-737CE37C` — (Flows) CreateFlowAlias requests per second
- `L-73ACE256` — (Flows) ListFlowVersions requests per second
- `L-73BBA086` — (Model customization) Sum of training and validation records for a Titan Image Generator G1 V1 Fine-tuning job
- `L-7478F443` — Model units per provisioned model for Anthropic Claude V2.1 18K
- `L-749C38BD` — (Automated Reasoning) GetAutomatedReasoningPolicyBuildWorkflow requests per second
- `L-74B5B793` — On-demand model inference tokens per minute for Amazon Titan Text Embeddings
- `L-75D9A33A` — On-demand model inference requests per minute for AI21 Labs Jurassic-2 Mid
- `L-77854CA1` — (Knowledge Bases) Files to delete per ingestion job
- `L-77C372BE` — (Flows) GetFlowVersion requests per second
- `L-79301C5B` — Batch inference job size (in GB) for Claude 3 Haiku
- `L-795ADAB0` — Global cross-region model inference tokens per day for Cohere Embed V4
- `L-79BA683B` — (Model customization) Sum of training and validation records for a Titan Text G1 - Express v1 Fine-tuning job
- `L-7C42E72A` — Cross-region model inference tokens per minute for Amazon Nova Lite
- `L-7C4CB0BA` — (Automated Reasoning) Annotations in policy
- `L-7D24C2A2` — (Prompt management) GetPrompt requests per second
- `L-7D9F04A9` — (Automated Reasoning) GetAutomatedReasoningPolicyTestCase requests per second
- `L-7DBB06FD` — On-demand model inference requests per minute for Amazon Titan Image Generator G1
- `L-7F512C61` — Throttle rate limit for GetBlueprint
- `L-8111AFAC` — Batch inference input file size (in GB) for Llama 3.2 3B Instruct
- `L-8129BF10` — Model units per provisioned model for Amazon Titan Text G1 - Express 8K
- `L-81E26054` — Records per input file per batch inference job for Titan Multimodal Embeddings G1
- `L-829AE0B9` — (Data Automation) Maximum image file size (MB)
- `L-83FDDF24` — DeleteAgentActionGroup requests per second
- `L-8453046B` — (Knowledge Bases) UpdateDataSource requests per second
- `L-8651ED26` — Records per input file per batch inference job for Llama 3.1 405B Instruct
- `L-871FF812` — UpdateAgentAlias requests per second
- `L-87482B04` — Minimum number of records per batch inference job for Llama 3.1 8B Instruct
- `L-879F6850` — On-demand model inference requests per minute for Amazon Titan Text Embeddings
- `L-87E3FFAC` — (Flows) GetFlow requests per second
- `L-884C068A` — (Automated Reasoning) ListAutomatedReasoningPolicyBuildWorkflows requests per second
- `L-89197AE6` — Records per batch inference job for Nova Pro V1
- `L-893F8BF9` — (Guardrails) Contextual grounding source length in text units
- `L-895C7A6C` — (Data Automation) InvokeDataAutomationAsync - Video - Max number of concurrent jobs
- `L-897F8151` — Records per input file per batch inference job for Claude 3.5 Sonnet v2
- `L-89F8391A` — Cross-region model inference requests per minute for Amazon Nova Lite
- `L-8A686BB7` — (Automated Reasoning) GetAutomatedReasoningPolicyTestResult requests per second
- `L-8A6B31EE` — Records per batch inference job for Claude Sonnet 4
- `L-8AF2815B` — (Data Automation) Maximum Number of pages per document
- `L-8B216E37` — Records per input file per batch inference job for Qwen3 Coder 30B
- `L-8CB739C8` — Records per input file per batch inference job for Qwen3 Coder 480B
- `L-8CE99163` — On-demand model inference tokens per minute for Anthropic Claude 3 Haiku
- `L-8CEDED9C` — On-demand model inference requests per minute for Anthropic Claude Instant
- `L-8D07E980` — Records per batch inference job for Llama 3.1 70B Instruct
- `L-8D4EA85C` — Batch inference job size (in GB) for Llama 3.2 11B Instruct
- `L-8D4ED20B` — (Knowledge Bases) Concurrent IngestKnowledgeBaseDocuments and DeleteKnowledgeBaseDocuments requests per account
- `L-8E129B28` — Batch inference input file size (in GB) for Llama 3.2 11B Instruct
- `L-8E63548F` — UpdateAgentKnowledgeBase requests per second
- `L-8EA73537` — Cross-region model inference tokens per minute for Anthropic Claude Sonnet 4.5 V1 1M Context Length
- `L-8F302008` — Batch inference job size (in GB) for Llama 3.1 8B Instruct
- `L-9072D6F0` — (Guardrails) On-demand ApplyGuardrail requests per second
- `L-9149A536` — Model units per provisioned model for Stability.ai Stable Diffusion XL 1.0
- `L-91554672` — (Model customization) Sum of training and validation records for a Titan Text G1 - Lite v1 Continued Pre-Training job
- `L-916C9264` — Records per batch inference job for Nova Lite V1
- `L-92F3BE6F` — Throttle rate limit for Bedrock Data Automation Runtime: TagResource
- `L-92F81E14` — On-demand model inference tokens per minute for Qwen3 Coder 30B a3b V1
- `L-9342B636` — Model units per provisioned model for AI21 Labs Jurassic-2 Mid
- `L-934360E8` — Batch inference input file size (in GB) for Claude 3.5 Sonnet
- `L-94612705` — Batch inference job size for Qwen3 235B (in GB)
- `L-95CACD43` — Records per batch inference job for Llama 3.2 11B Instruct
- `L-9602E0D9` — (Flows) CreateFlow requests per second
- `L-963BB4DE` — Throttle rate limit for Bedrock Data Automation: ListTagsForResource
- `L-97A8CC77` — Model units per provisioned model for Cohere Embed English
- `L-982DE2DB` — Records per batch inference job for Llama 3.2 3B Instruct
- `L-987117C6` — ListAgentVersions requests per second
- `L-987C98F5` — Batch inference job size (in GB) for Claude 3.5 Haiku
- `L-99105855` — (Data Automation) Minimum Audio Sample Rate (Hz)
- `L-99471E7A` — (Automated Reasoning) ListAutomatedReasoningPolicies requests per second
- `L-995BEC0E` — (Knowledge Bases) IngestKnowledgeBaseDocuments total payload size
- `L-99AE898F` — (Knowledge Bases) DeleteDataSource requests per second
- `L-9A11C666` — Global cross-region model inference tokens per minute for Anthropic Claude Haiku 4.5
- `L-9B17C979` — (Automated Reasoning) ExportAutomatedReasoningPolicyVersion requests per second
- `L-9B651738` — Records per input file per batch inference job for Nova Pro V1
- `L-9B9B20DB` — (Automated Reasoning) GetAutomatedReasoningPolicyBuildWorkflowResultAssets requests per second
- `L-9C450F60` — (Data Automation) Maximum video file size (MB)
- `L-9CFEE1D8` — Minimum number of records per batch inference job for Qwen3 235B
- `L-9D2E32B8` — Minimum number of records per batch inference job for Qwen3 32B
- `L-9D3DC9B2` — (Automated Reasoning) ListAutomatedReasoningPolicyTestResults requests per second
- `L-9D7C8A75` — (Automated Reasoning) UpdateAutomatedReasoningPolicyTestCase requests per second
- `L-9DC5F595` — On-demand model inference tokens per minute for OpenAI GPT OSS 120B
- `L-9E3C255A` — (Data Automation) InvokeDataAutomationAsync - Document - Max number of concurrent jobs
- `L-9E5BD0C6` — On-demand model inference requests per minute for Cohere Embed Multilingual
- `L-9EAB0D12` — On-demand model inference requests per minute for Amazon Titan Text Express
- `L-9EB71894` — Model invocation max tokens per day for Anthropic Claude 3.7 Sonnet V1 (doubled for cross-region calls)
- `L-9EF11C18` — Records per input file per batch inference job for OpenAI GPT OSS 120b
- `L-9EF212F4` — ListAgentKnowledgeBases requests per second
- `L-9EF56DA1` — (Automated Reasoning) UpdateAutomatedReasoningPolicy requests per second
- `L-9F13DDE7` — Batch inference input file size (in GB) for Mistral Large 2 (24.07)
- `L-9F4DB459` — (Guardrails) On-demand ApplyGuardrail Word filter policy text units per second
- `L-A052927A` — Cross-region model inference requests per minute for Anthropic Claude Sonnet 4.5 V1 1M Context Length
- `L-A115DE95` — Model invocation max tokens per day for Qwen3 32B V1 (doubled for cross-region calls)
- `L-A12FFE89` — (Automated Reasoning) Source document size (MB)
- `L-A21CC341` — (Knowledge Bases) ListKnowledgeBases requests per second
- `L-A2BE277A` — On-demand model inference tokens per minute for Cohere Embed English
- `L-A31D2B40` — Cross-region model inference requests per minute for Meta Llama 3.2 1B Instruct
- `L-A3D5E9F8` — Batch inference job size (in GB) for Claude 3.5 Sonnet v2
- `L-A48E31B4` — On-demand model inference requests per minute for AI21 Labs Jurassic-2 Ultra
- `L-A49CA90F` — On-demand model inference requests per minute for Cohere Command R
- `L-A4A6DDE4` — (Data Automation) Maximum Resolution
- `L-A4EBFDE7` — Model units per provisioned model for Amazon Titan Lite V1 4K
- `L-A4F5E139` — On-demand model inference tokens per minute for AI21 Labs Jurassic-2 Ultra
- `L-A50569E5` — On-demand model inference tokens per minute for Anthropic Claude 3.5 Sonnet
- `L-A596AFC0` — (Data Automation) InvokeDataAutomationAsync - Max number of open jobs
- `L-A5CEDB91` — Minimum number of records per batch inference job for Llama 3.1 405B Instruct
- `L-A63633C5` — Model units per provisioned model for Anthropic Claude V2.1 200K
- `L-A70F1DE3` — On-demand model inference requests per minute for Amazon Titan Text Lite
- `L-A7382519` — Batch inference input file size for Qwen3 Coder 30B (in GB)
- `L-A7EDC29B` — On-demand model inference tokens per minute for Meta Llama 3.2 3B Instruct
- `L-A83ECA24` — Batch inference job size (in GB) for Mistral Large 2 (24.07)
- `L-A985813D` — Records per input file per batch inference job for Claude 3.7 Sonnet
- `L-AA411D03` — Records per batch inference job for Llama 3.1 405B Instruct
- `L-AAB0080F` — On-demand model inference requests per minute for Amazon Rerank 1.0
- `L-AAC5F6D6` — Records per batch inference job for Titan Text Embeddings V2
- `L-AB971C9B` — Batch inference job size (in GB) for Claude 3 Sonnet
- `L-ABA9742A` — (Data Automation) Maximum audio length (Minutes)
- `L-ABC24664` — On-demand model inference tokens per minute for Amazon Titan Multimodal Embeddings G1
- `L-ABEE1010` — On-demand model inference tokens per minute for AI21 Labs Jurassic-2 Mid
- `L-AC6F8476` — Model units per provisioned model for Meta Llama 2 Chat 13B
- `L-ACA7B6C2` — Batch inference input file size (in GB) for Llama 3.2 90B Instruct
- `L-ADB4B3D7` — On-demand model inference requests per minute for Cohere Command R Plus
- `L-ADCC1A3F` — Model invocation max tokens per day for Qwen3 Coder 30B a3b V1 (doubled for cross-region calls)
- `L-AE7F26D4` — Minimum number of records per batch inference job for Claude 3 Haiku
- `L-AED2B25B` — Batch inference job size for Qwen3 32B (in GB)
- `L-AF7F0545` — On-demand model inference requests per minute for OpenAI GPT OSS 20B
- `L-AFA1CDAB` — (Knowledge Bases) RetrieveAndGenerate requests per second
- `L-AFE8E0CD` — Records per input file per batch inference job for Llama 3.1 8B Instruct
- `L-B05C5C8E` — On-demand model inference tokens per minute for Meta Llama 2 Chat 70B
- `L-B0D9183E` — On-demand model inference tokens per minute for Anthropic Claude V2
- `L-B2ADD004` — Batch inference job size (in GB) for Llama 3.1 70B Instruct
- `L-B46AC24C` — (Knowledge Bases) GetKnowledgeBase requests per second
- `L-B48488BD` — Minimum number of records per batch inference job for Claude 3.5 Haiku
- `L-B5C049AE` — Global cross-region model inference tokens per day for Anthropic Claude Haiku 4.5
- `L-B63536E3` — On-demand model inference tokens per minute for Cohere Command Light
- `L-B688EFA5` — Batch inference input file size (in GB) for Claude 3.5 Haiku
- `L-B6A2F07B` — Throttle rate limit for Bedrock Data Automation: TagResource
- `L-B7BF1255` — (Automated Reasoning) StartAutomatedReasoningPolicyBuildWorkflow requests per second
- `L-B7C52139` — On-demand model inference tokens per minute for Qwen3 32B V1
- `L-B802A131` — On-demand model inference requests per minute for Cohere Command Light
- `L-B83CA9E3` — ListAgents requests per second
- `L-B8626674` — Records per input file per batch inference job for Nova Lite V1
- `L-B87081C1` — Records per batch inference job for Qwen3 Coder 480B
- `L-B8DED09F` — Batch inference input file size (in GB) for Llama 3.2 1B Instruct
- `L-B99072E7` — (Knowledge Bases) GetDataSource requests per second
- `L-BA177AC2` — Throttle rate limit for DeleteBlueprint
- `L-BA9E2685` — Records per batch inference job for Qwen3 235B
- `L-BAE2EB93` — Records per input file per batch inference job for Mistral Large 2 (24.07)
- `L-BB313AA3` — (Model customization) Sum of training and validation records for a Titan Multimodal Embeddings G1 v1 Fine-tuning job
- `L-BC0281B9` — Minimum number of records per batch inference job for DeepSeek v3
- `L-BC182137` — Global cross-region model inference tokens per day for Anthropic Claude Sonnet 4.5 V1
- `L-BC7417B6` — (Flows) UpdateFlowAlias requests per second
- `L-BCF9AED9` — Batch inference input file size (in GB) for Llama 3.1 405B Instruct
- `L-BD343E2A` — (Data Automation) Maximum number of Blueprints per Start Inference request (Audios)
- `L-BD9FDA6F` — Cross-region model inference tokens per minute for Meta Llama 3.2 1B Instruct
- `L-BDD176EF` — (Data Automation) InvokeDataAutomationAsync - Image - Max number of concurrent jobs
- `L-BEAE3E04` — Batch inference input file size for Qwen3 Coder 480B (in GB)
- `L-BF8FAABD` — Records per input file per batch inference job for Qwen3 32B
- `L-BFA0FE84` — Minimum number of records per batch inference job for Claude 3.7 Sonnet
- `L-BFA815EF` — (Data Automation) (Console) Maximum number of pages per document file
- `L-C0326783` — Cross-region model inference tokens per minute for Amazon Nova Pro
- `L-C0CACF50` — (Model customization) Sum of training and validation records for a Titan Text G1 - Premier v1 Fine-tuning job
- `L-C0D53EFB` — Global cross-region model inference requests per minute for Anthropic Claude Sonnet 4.5 V1 1M Context Length
- `L-C15B8AA6` — (Flows) DeleteFlow requests per second
- `L-C2F86908` — On-demand model inference tokens per minute for Cohere Embed Multilingual
- `L-C2FA9AEC` — Sum of in-progress and submitted batch inference jobs using a base model for Claude 3.5 Sonnet v2
- `L-C39B6D57` — Records per input file per batch inference job for Claude 3.5 Haiku
- `L-C3BA7ADC` — Sum of in-progress and submitted batch inference jobs using a base model for Qwen3 Coder 480B
- `L-C4522D0D` — Model units per provisioned model for Anthropic Claude V2 100K
- `L-C479D0A2` — ListAgentAliases requests per second
- `L-C482C4CA` — GetAgentVersion requests per second
- `L-C549AE85` — Model units per provisioned model for Cohere Command R Plus
- `L-C5913DD6` — (Automated Reasoning) CreateAutomatedReasoningPolicyVersion requests per second
- `L-C68D8E7F` — DeleteAgent requests per second
- `L-C79C2150` — Batch inference job size (in GB) for Nova Micro V1
- `L-C7DC86D2` — ListAgentActionGroups requests per second
- `L-CA1FB1BE` — Throttle rate limit for UpdateDataAutomationProject
- `L-CA80888F` — Records per batch inference job for Mistral Large 2 (24.07)
- `L-CAF2175F` — Batch inference job size (in GB) for Llama 3.2 90B Instruct
- `L-CB18C933` — Batch inference job size for DeepSeek v3 (in GB)
- `L-CBAEEDF6` — Batch inference input file size (in GB) for Llama 3.3 70B Instruct
- `L-CC58F0A8` — On-demand model inference requests per minute for Stability.ai Stable Diffusion XL 1.0
- `L-CCA5DF70` — Cross-region model inference requests per minute for Anthropic Claude Haiku 4.5
- `L-CD43D76B` — (Data Automation) Minimum audio length (Miliseconds)
- `L-CDD9DC4A` — (Model customization) Sum of training and validation records for a Titan Text G1 - Express v1 Continued Pre-Training job
- `L-CF987B82` — (Knowledge Bases) GenerateQuery requests per second
- `L-CFCAAB0E` — (Guardrails) On-demand ApplyGuardrail Sensitive information filter policy text units per second
- `L-CFF972CC` — AssociateAgentKnowledgeBase requests per second
- `L-D1151D45` — Records per input file per batch inference job for Titan Text Embeddings V2
- `L-D11DCD9B` — On-demand model inference requests per minute for Meta Llama 2 Chat 70B
- `L-D1374B71` — (Knowledge Bases) GetIngestionJob requests per second
- `L-D19DD0CE` — (Flows) ListFlows requests per second
- `L-D30E6B4B` — Records per input file per batch inference job for Llama 3.2 11B Instruct
- `L-D32CEBC2` — Batch inference input file size (in GB) for Mistral Small
- `L-D4C72CE2` — Minimum number of records per batch inference job for Llama 3.2 90B Instruct
- `L-D50EA4E4` — Batch inference job size (in GB) for Llama 3.1 405B Instruct
- `L-D56DF585` — Records per input file per batch inference job for Nova Micro V1
- `L-D5C2E582` — On-demand model inference requests per minute for Meta Llama 2 70B
- `L-D9A35062` — On-demand model inference requests per minute for Mistral 7B Instruct
- `L-D9F0CC0D` — On-demand model inference tokens per minute for Meta Llama 2 13B
- `L-DB84CE56` — Global cross-region model inference requests per minute for Anthropic Claude Sonnet 4.5 V1
- `L-DC7FF66C` — Cross-region model inference tokens per minute for Amazon Nova Micro
- `L-DCADBC78` — Cross-region model inference tokens per minute for Anthropic Claude 3 Haiku
- `L-DDB13222` — Throttle rate limit for Bedrock Data Automation: UntagResource
- `L-DE0A7679` — Minimum number of records per batch inference job for Mistral Small
- `L-DE24F5BC` — (Prompt management) ListPrompts requests per second
- `L-DE641971` — On-demand model inference tokens per minute for Amazon Titan Text Embeddings V2
- `L-DF0E34D4` — On-demand model inference requests per minute for Amazon Titan Multimodal Embeddings G1
- `L-DF85B2D2` — Throttle rate limit for UpdateBlueprint
- `L-DFDD7036` — Records per batch inference job for Qwen3 Coder 30B
- `L-E038D932` — Records per input file per batch inference job for Llama 3.1 70B Instruct
- `L-E06E7FD6` — Minimum number of records per batch inference job for Llama 3.3 70B Instruct
- `L-E107194C` — Model invocation max tokens per day for Anthropic Claude Sonnet 4.5 V1 1M Context Length (doubled for cross-region calls)
- `L-E14A4A4C` — CreateAgentAlias requests per second
- `L-E293C7C7` — Records per batch inference job for Llama 3.3 70B Instruct
- `L-E31283B0` — Batch inference job size (in GB) for Claude Sonnet 4
- `L-E428575E` — (Knowledge Bases) StartIngestionJob requests per second
- `L-E432BE02` — (Evaluation) Task time for workers
- `L-E4D5D109` — Model invocation max tokens per day for Qwen3 235B a22b 2507 V1 (doubled for cross-region calls)
- `L-E5084BBA` — Global cross-region model inference requests per minute for Anthropic Claude Haiku 4.5
- `L-E5418429` — Batch inference input file size for DeepSeek v3 (in GB)
- `L-E553E123` — (Flows) ValidateFlowDefinition requests per second
- `L-E6489B37` — Records per input file per batch inference job for Mistral Small
- `L-E855A326` — Batch inference input file size (in GB) for OpenAI GPT OSS 120b
- `L-E880C759` — On-demand model inference requests per minute for Qwen3 32B V1
- `L-E8FA49DB` — Records per batch inference job for Claude 3 Opus
- `L-E93C745B` — Records per input file per batch inference job for Claude 3 Sonnet
- `L-E953E4AB` — Model units per provisioned model for Meta Llama 2 Chat 70B
- `L-E9AF2411` — DisassociateAgentKnowledgeBase requests per second
- `L-EA319DB4` — Records per input file per batch inference job for DeepSeek v3
- `L-EAA9E7C9` — (Data Automation) Maximum number of Blueprints per Start Inference request (Documents)
- `L-EAD257E4` — (Automated Reasoning) GetAutomatedReasoningPolicyNextScenario requests per second
- `L-EB8C1F30` — Cross-region model inference requests per minute for Cohere Embed V4
- `L-EBB72C32` — Records per input file per batch inference job for Claude 3 Haiku
- `L-ED46B8C5` — Cross-region model inference requests per minute for Amazon Nova Pro
- `L-ED4DC88B` — (Prompt management) UpdatePrompt requests per second
- `L-EF804815` — Records per input file per batch inference job for OpenAI GPT OSS 20b
- `L-F0D0E0B9` — (Knowledge Bases) Retrieve requests per second
- `L-F12318F0` — Minimum number of records per batch inference job for Mistral Large 2 (24.07)
- `L-F1BB08BB` — Model invocation max tokens per day for Cohere Embed V4 (doubled for cross-region calls)
- `L-F20FBC17` — (Automated Reasoning) DeleteAutomatedReasoningPolicyBuildWorkflow requests per second
- `L-F2469446` — Model units per provisioned model for Cohere Command R
- `L-F2DCFA42` — (Automated Reasoning) UpdateAutomatedReasoningPolicyAnnotations requests per second
- `L-F2E6F90D` — Records per input file per batch inference job for Llama 3.2 3B Instruct
- `L-F361DF0F` — Records per batch inference job for OpenAI GPT OSS 20b
- `L-F36E54E0` — Batch inference input file size (in GB) for Nova Micro V1
- `L-F3A3096C` — Batch inference input file size (in GB) for Llama 3.1 8B Instruct
- `L-F3B698BE` — On-demand model inference requests per minute for Anthropic Claude V2
- `L-F406804E` — On-demand model inference requests per minute for Anthropic Claude 3 Sonnet
- `L-F424A1E3` — Model units per provisioned model for Amazon Titan Image Generator G1
- `L-F457545D` — Cross-region model inference requests per minute for Anthropic Claude 3.5 Sonnet
- `L-F4B97433` — Batch inference job size for Qwen3 Coder 30B (in GB)
- `L-F4DDD3EB` — Cross-region model inference tokens per minute for Anthropic Claude Sonnet 4.5 V1
- `L-F5353579` — (Automated Reasoning) Source document tokens
- `L-F5ACA0A6` — (Automated Reasoning) CreateAutomatedReasoningPolicyTestCase requests per second
- `L-F60B56CC` — Batch inference input file size (in GB) for Nova Lite V1
- `L-F611997D` — Batch inference input file size (in GB) for Claude Sonnet 4
- `L-F63AB5A7` — (Knowledge Bases) GetKnowledgeBaseDocuments requests per second
- `L-F65B864B` — (Knowledge Bases) Maximum number of files for BDA parser
- `L-F687AD4D` — Batch inference job size for Titan Text Embeddings V2 (in GB)
- `L-F7007F39` — On-demand model inference tokens per minute for Anthropic Claude Instant
- `L-F72F26EE` — Minimum number of records per batch inference job for Claude Sonnet 4
- `L-F762E842` — (Knowledge Bases) Files to ingest per IngestKnowledgeBaseDocuments job.
- `L-F77743B5` — Records per input file per batch inference job for Llama 3.3 70B Instruct
- `L-F777E93B` — Batch inference job size (in GB) for Llama 3.2 1B Instruct
- `L-F81D0C4B` — Records per batch inference job for DeepSeek v3
- `L-F879F645` — Model units per provisioned model for Amazon Titan Embeddings G1 - Text
- `L-F8B0126D` — Batch inference input file size (in GB) for Claude 3.7 Sonnet
- `L-FA06C205` — Records per batch inference job for Llama 3.1 8B Instruct
- `L-FA9A1EBB` — Minimum number of records per batch inference job for Claude 3 Opus
- `L-FABEE48F` — Records per batch inference job for Claude 3.7 Sonnet
- `L-FC4A46BE` — Throttle rate limit for GetDataAutomationStatus
- `L-FC6C0CDB` — (Flows) DeleteFlowVersion requests per second
- `L-FD938632` — On-demand model inference requests per minute for Mistral Mixtral 8x7b Instruct
- `L-FE6BC3E4` — Minimum number of records per batch inference job for Claude 3 Sonnet
- `L-FEE1DCB6` — On-demand model inference tokens per minute for Cohere Command R Plus
- `L-FF73AE42` — Records per batch inference job for Llama 3.2 1B Instruct
- `L-FF8B4E28` — Cross-Region model inference tokens per minute for Anthropic Claude 3.5 Sonnet V2
- `L-FF8E7864` — On-demand model inference requests per minute for Cohere Embed English

## bedrock-agentcore

- `L-180EDCA2` — Rate of GetEvent requests
- `L-1D35AE05` — Message size
- `L-1D9B7520` — Rate of DeleteEvent requests
- `L-57F6BA66` — Rate of DeleteMemory requests
- `L-59AF2B24` — Rate of CreateEvent requests
- `L-5F98329B` — Rate of GetMemoryRecord requests
- `L-7EA1F1FC` — Rate of UpdateMemory requests
- `L-801A491D` — Rate of BatchDeleteMemoryRecords requests
- `L-80B4FBA5` — Rate of ListMemoryRecords requests
- `L-82C17831` — Rate of ListMemories requests
- `L-890C813A` — Rate of BatchCreateMemoryRecords requests
- `L-898013A7` — Messages per event
- `L-8E7F90A5` — Rate of CreateMemory requests
- `L-9484366D` — Event size
- `L-A0E37F52` — Rate of BatchUpdateMemoryRecords requests
- `L-A16713AA` — Rate of ListSessions requests
- `L-A37DB4C7` — Rate of CreateEvent requests per actor per session not including conversational payloads
- `L-A73B53F2` — Rate of DeleteMemoryRecord requests
- `L-AD5A1610` — Rate of ListActors requests
- `L-BC0EE484` — Rate of CreateEvent requests per actor per session including conversational payloads
- `L-C4725965` — Rate of ListEvents requests
- `L-E3D6644C` — Tokens per minute for long-term memory extraction
- `L-EB2B5C4A` — Rate of RetrieveMemoryRecords requests
- `L-EC8EB7A6` — Rate of GetMemory requests

## cases

- `L-05D04EFD` — DeleteCaseRule rate quota
- `L-085C6605` — CreateCase burst quota
- `L-1320C83D` — GetTemplate burst quota
- `L-1D2B06EC` — UpdateCase burst quota
- `L-1ECD16ED` — TagResource burst quota
- `L-1F185B9F` — CreateRelatedItem rate quota
- `L-1F4F11B7` — ListTemplates rate quota
- `L-23C4A953` — CreateCaseRule burst quota
- `L-26EE2CFC` — CreateTemplate rate quota
- `L-2A8092BB` — BatchGetField rate quota
- `L-2AD9F9AD` — UpdateTemplate burst quota
- `L-2C517B14` — BatchGetCaseRule rate quota
- `L-3255B73C` — ListDomains burst quota
- `L-3B58A5D3` — SearchRelatedItems rate quota
- `L-497703F2` — CreateField rate quota
- `L-4A51BF9E` — GetCaseAuditEvents burst quota
- `L-4B3D8F5F` — ListLayouts rate quota
- `L-4CE16517` — ListTagsForResource burst quota
- `L-4DCBEEA7` — UpdateCaseRule rate quota
- `L-515ED5E2` — UntagResource rate quota
- `L-533535BF` — SearchCases burst quota
- `L-5462CD7A` — PutCaseEventConfiguration rate quota
- `L-55E43513` — ListCaseRules burst quota
- `L-5A125C02` — CreateRelatedItem burst quota
- `L-5E8805C5` — SearchRelatedItems burst quota
- `L-6363E76B` — GetCaseAuditEvents rate quota
- `L-648204D1` — BatchGetCaseRule burst quota
- `L-6743683C` — UpdateLayout burst quota
- `L-6FE92BD9` — UpdateCase rate quota
- `L-74EA148C` — GetCaseEventConfiguration burst quota
- `L-7736E0FB` — CreateLayout rate quota
- `L-7CF7A4F0` — ListFields burst quota
- `L-7D6B0EAF` — GetCase burst quota
- `L-845575A5` — CreateCaseRule rate quota
- `L-85809F5E` — ListFieldOptions burst quota
- `L-8AA97C3E` — GetTemplate rate quota
- `L-8B6DA341` — GetCase rate quota
- `L-8FEA710A` — CreateCase rate quota
- `L-960AA7D7` — ListLayouts burst quota
- `L-97677C0C` — ListDomains rate quota
- `L-9B7552E3` — GetDomain burst quota
- `L-9BEF063B` — CreateDomain rate quota
- `L-A246B577` — ListCasesForContact rate quota
- `L-A298B896` — BatchPutFieldOptions burst quota
- `L-A96CA735` — UpdateField burst quota
- `L-AA3996A0` — SearchCases rate quota
- `L-AE0F3125` — UntagResource burst quota
- `L-B3860F14` — GetLayout burst quota
- `L-B3BCA676` — ListTemplates burst quota
- `L-B4BF7E31` — CreateDomain burst quota
- `L-B5BE889D` — UpdateTemplate rate quota
- `L-B5E6891E` — UpdateCaseRule burst quota
- `L-B7E2C410` — ListFieldOptions rate quota
- `L-C0E6C678` — TagResource rate quota
- `L-CC009CC4` — UpdateField rate quota
- `L-D3F1EBFD` — BatchGetField burst quota
- `L-D4F270D6` — PutCaseEventConfiguration burst quota
- `L-D69B27B2` — GetCaseEventConfiguration rate quota
- `L-D69D3749` — UpdateLayout rate quota
- `L-D750A577` — ListFields rate quota
- `L-E017C84B` — DeleteCaseRule burst quota
- `L-E5EE4EDA` — GetLayout rate quota
- `L-E77680D7` — CreateTemplate burst quota
- `L-F4DAA62B` — CreateField burst quota
- `L-F5011010` — BatchPutFieldOptions rate quota
- `L-F62E3726` — ListTagsForResource rate quota
- `L-FD0EC666` — GetDomain rate quota
- `L-FE18F7CC` — ListCaseRules rate quota
- `L-FF304B65` — ListCasesForContact burst quota
- `L-FF9E638C` — CreateLayout burst quota

## cassandra

- `L-0659E12E` — Max clustering key size
- `L-17766544` — Table-level read throughput quota
- `L-29E90199` — Concurrent DDL operations
- `L-2C5B14BD` — Account-level write throughput quota (Provisioned mode)
- `L-2FC1B9A1` — Max subqueries per IN SELECT statement
- `L-324B5396` — Max partition key size
- `L-3D8ED127` — Table-level write throughput quota
- `L-4C49F3DB` — Max amount of data restored using Point-in-time Recovery (PITR)
- `L-5823D982` — Max static data per logical partition
- `L-6632AD49` — Max write capacity for a table using change-data-capture (CDC)
- `L-66AD5703` — Max row size
- `L-7F2EAE05` — Max amount of data restored using add Region operations
- `L-E08A04C1` — Max Schema size
- `L-E7DB0CFF` — Account-level read throughput quota (Provisioned mode)
- `L-F41E662B` — Max concurrent table restores using Point-in-time Recovery (PITR)

## chime

- `L-06A9F29A` — Amazon Chime SDK Messaging - DescribeChannel API requests per second
- `L-06F4BAB8` — Amazon Chime SDK Messaging - ListChannelMembershipsForAppInstanceUser API requests per second
- `L-0A68E24C` — Amazon Chime SDK Identity - AppInstance API requests per second
- `L-0AC3ED57` — Amazon Chime SDK Messaging - Maximum Channels per AppInstance
- `L-0E2E2226` — Amazon Chime SDK meetings - Concurrent video streams subscribed per attendee
- `L-0EB74667` — Amazon Chime SDK Messaging - Maximum concurrent active connections per AppInstanceUser
- `L-13B02A3D` — Amazon Chime SDK Identity - DescribeAppInstanceUser API requests per second
- `L-154D84D0` — Amazon Chime SDK meetings - Replica meetings per primary meeting
- `L-1AB05505` — Amazon Chime SDK meetings - UnTagResource API rate in requests per second
- `L-1DB18BA9` — Amazon Chime SDK Identity - ListAppInstances API requests per second
- `L-21762DC9` — Amazon Chime SDK SIP trunking and voice - UpdateSipMediaApplicationCall API rate limit
- `L-2C15A6A8` — Amazon Chime SDK meetings - DeleteAttendee API rate in requests per second
- `L-32923D03` — Amazon Chime SDK PSTN Audio - SIP Media Application Active Call Limit
- `L-37BA0833` — Amazon  Chime SDK meetings - ListAttendees API rate in requests per second
- `L-37E67822` — Amazon Chime SDK Messaging - ListChannelMessages API requests per second
- `L-398B2BD6` — Amazon Chime SDK meetings - DeleteAttendee API burst rate in requests per second
- `L-3BB10AA7` — Amazon Chime SDK meetings - TagResource API rate in requests per second
- `L-3C5ED081` — Amazon Chime SDK Identity - DescribeAppInstance API requests per second
- `L-3CC08C2F` — Amazon Chime SDK meetings - UpdateAttendeeCapabilities API rate in requests per second
- `L-3E511C5B` — Amazon Chime SDK Messaging - Maximum ChannelModerators per Channel
- `L-426F5480` — Amazon Chime SDK Messaging - BatchCreateChannelMembership API requests per second
- `L-44BD764A` — Amazon Chime SDK meetings - BatchUpdateAttendeeCapabilitiesExcept API rate in requests per second
- `L-48F4CA7A` — Amazon Chime SDK meetings - DeleteMeeting API rate in requests per second
- `L-53F2D722` — Amazon Chime SDK Messaging - Channel API requests per second
- `L-563605EA` — Amazon Chime SDK meetings - CreateAttendee API rate in requests per second
- `L-58DEE317` — Amazon Chime SDK Identity - Chime SDK Identity API requests per second
- `L-58F5D62D` — Amazon Chime SDK meetings - GetMeeting API burst rate in requests per second
- `L-5F1ABF39` — Amazon Chime SDK meetings - CreateMeetingWithAttendees API rate in requests per second
- `L-63907FE3` — Amazon Chime SDK meetings - All meeting management API burst rate in requests per second
- `L-674630CB` — Amazon Chime SDK meetings - UpdateAttendeeCapabilities API burst rate in requests per second
- `L-6B38EB2F` — Amazon Chime SDK meetings - CreateAttendee API burst rate in requests per second
- `L-6FAB55D2` — Amazon Chime SDK meetings - GetMeeting API rate in requests per second
- `L-74978BCC` — Amazon Chime SDK Messaging - Websocket connect API requests per second
- `L-771FFB29` — Amazon Chime SDK meetings - ListMeetings API burst rate in requests per second
- `L-7846C766` — Amazon Chime SDK meetings - BatchUpdateAttendeeCapabilitiesExcept API burst rate in requests per second
- `L-793B6D9C` — Amazon Chime SDK meetings - ListMeetings API rate in requests per second
- `L-7B4DA565` — Amazon Chime SDK meetings - BatchCreateAttendees API rate in requests per second
- `L-7CE8F2DD` — Amazon Chime SDK Messaging - Maximum ChannelMemberships in CHANNEL_DETAILS events for prefetch
- `L-8013F35C` — Amazon Chime SDK SIP trunking and voice - Voice Connector Active Call Limit
- `L-804108DA` — Amazon Chime SDK media pipeline - API rate
- `L-8A6E3C7B` — Amazon Chime SDK meetings - CreateMeeting API rate in requests per second
- `L-91426809` — Amazon Chime SDK meetings - CreateMeetingWithAttendees API burst rate in requests per second
- `L-98193B78` — Amazon Chime SDK meetings - BatchCreateAttendees API burst rate in requests per second
- `L-9A2511FF` — Amazon Chime SDK Messaging - Maximum ChannelMemberships per Channel
- `L-9B0D42EC` — Amazon Chime SDK Messaging - Requests per second of create or delete channel memberships, bans, and moderators for a specific channel
- `L-9F286451` — Amazon Chime SDK meetings - Concurrent meeting quota
- `L-A42FC7C2` — Amazon Chime SDK meetings - DeleteMeeting API burst rate in requests per second
- `L-A92E8EF9` — Amazon Chime SDK Messaging - AppInstanceUser API requests per second
- `L-AC1D2091` — Amazon Chime SDK meetings - Concurrent video streams published per meeting
- `L-B103920E` — Amazon Chime SDK meetings - ListTagsForResource API rate in requests per second
- `L-B17C47C8` — Amazon Chime SDK Messaging - ListChannels API requests per second
- `L-B1CE561B` — Amazon Chime SDK meetings - Attendees per meeting
- `L-B2BA1F32` — Amazon Chime SDK Messaging - Maximum ChannelMessages in CHANNEL_DETAILS events for prefetch
- `L-B5609908` — Amazon Chime SDK Messaging - Listing channel memberships API requests per second
- `L-B6F2C623` — Amazon Chime SDK SIP trunking and voice - calls per second (CPS)
- `L-BB2EEB39` — Amazon Chime SDK Messaging - GetChannelMessage API requests per second
- `L-C115F428` — Amazon Chime SDK SIP trunking and voice - CreateSipMediaApplicationCall API rate limit
- `L-C875D9AA` — Amazon Chime SDK meetings - ListAttendees API burst rate in requests per second
- `L-CF24303F` — Amazon Chime SDK call analytics - API rate
- `L-D99DAB65` — Amazon Chime SDK Identity - AppInstanceUser API requests per second
- `L-DA021F73` — Amazon Chime SDK meetings - TagResource API burst rate in requests per second
- `L-E79A53C7` — Amazon Chime SDK meetings - ListTagsForResource API rate in requests per second
- `L-E8D9FB57` — Amazon Chime SDK Messaging - ListChannelsModeratedByAppInstanceUser API requests per second
- `L-E95601F2` — Amazon Chime SDK Messaging - Maximum CHANNEL_DETAILS events for prefetch
- `L-EA3B8D9B` — Amazon Chime SDK Identity - ListAppInstanceUsers API requests per second
- `L-F147F728` — Amazon Chime SDK meetings - All meeting management API rate in requests per second
- `L-F4340C7E` — Amazon Chime SDK media pipeline - Amazon Kinesis Video Stream pool API rate
- `L-FA316003` — Amazon Chime SDK meetings - UnTagResource API burst rate in requests per second
- `L-FE35185B` — Amazon Chime SDK Messaging - ChannelMessage API requests per second
- `L-FE9F896D` — Amazon Chime SDK meetings - CreateMeeting API burst rate in requests per second

## cleanrooms

- `L-08F7F01C` — Configured tables per protected query
- `L-093F1424` — Rate of ListIdNamespaceAssociations requests
- `L-0A3E7551` — Rate of GetSchema requests
- `L-0AD7EAD3` — Rate of CreateConfiguredTableAssociationAnalysisRule requests
- `L-0BF5D984` — Query text length on Clean Rooms SQL analytics engine
- `L-0FB3F147` — Rate of GetConfiguredTableAnalysisRule requests
- `L-133DD466` — Rate of CreatePrivacyBudgetTemplate requests
- `L-14E81699` — Columns per configured table allowlist
- `L-18630DF3` — Rate of GetIdNamespaceAssociation requests
- `L-1BCDF035` — Rate of GetConfiguredTableAssociation requests
- `L-1F2FB8F2` — Rate of GetProtectedJob requests
- `L-207110E9` — Rate of CreateIdNamespaceAssociation requests
- `L-23D4B294` — Rate of GetSchemaAnalysisRule requests
- `L-26B93E43` — Concurrent PySpark job vCPU usage per account
- `L-2BCA0376` — Rate of ListProtectedQueries requests
- `L-314AA705` — Rate of BatchGetSchemaAnalysisRule requests
- `L-3159A189` — Concurrent SQL query vCPU usage per account
- `L-339A44FE` — Rate of TagResource requests
- `L-37644F21` — Rate of DeletePrivacyBudgetTemplate requests
- `L-39FE5CA0` — Rate of UpdateConfiguredTableAnalysisRule requests
- `L-3CFEE53C` — Rate of ListCollaborationAnalysisTemplates requests
- `L-422E468C` — Rate of UpdateProtectedQuery requests
- `L-43C36E0F` — Rate of UpdateAnalysisTemplate requests
- `L-43DCB767` — Rate of UpdateConfiguredAudienceModelAssociation requests
- `L-44815395` — Rate of DeleteIdMappingTable requests
- `L-4645126D` — Query text length on Spark analytics engine
- `L-4678811D` — Rate of GetCollaborationPrivacyBudgetTemplate requests
- `L-46ADBA29` — Rate of DeleteMember requests
- `L-47C1561A` — Rate of ListAnalysisTemplates requests
- `L-4EFF30C3` — Rate of DeleteAnalysisTemplate requests
- `L-4FA6F2CA` — Rate of ListConfiguredTables requests
- `L-51EC588A` — Rate of PreviewPrivacyImpact requests
- `L-53CCCC3A` — Rate of StartProtectedJob requests
- `L-57B36CC8` — Rate of DeleteConfiguredAudienceModelAssociation requests
- `L-58076094` — Rate of CreateConfiguredTableAssociation requests
- `L-59F4710C` — Rate of StartProtectedQuery requests
- `L-5B356E2B` — Rate of GetProtectedQuery requests
- `L-5D65AE8D` — Rate of CreateCollaborationChangeRequest requests
- `L-5EDF6508` — Rate of GetAnalysisTemplate requests
- `L-60AA2A10` — Rate of GetConfiguredAudienceModelAssociation requests
- `L-60C9F5C8` — Rate of ListCollaborations requests
- `L-659B47CC` — Rate of ListMembers requests
- `L-6EE33BE8` — Rate of GetMembership requests
- `L-6FF866CD` — Rate of DeleteConfiguredTableAnalysisRule requests
- `L-71F0D659` — Rate of CreateCollaboration requests
- `L-73071115` — Rate of ListCollaborationIdNamespaceAssociations requests
- `L-75B5199D` — Rate of PopulateIdMappingTable requests
- `L-804ACCF8` — Rate of GetCollaborationIdNamespaceAssociation requests
- `L-80DB73D7` — Rate of DeleteMembership requests
- `L-82F4A89C` — Rate of ListCollaborationConfiguredAudienceModelAssociations requests
- `L-84D87AAE` — Rate of GetIdMappingTable requests
- `L-88914C24` — Rate of DeleteConfiguredTableAssociation requests
- `L-8B32F74B` — Rate of GetCollaborationAnalysisTemplate requests
- `L-8C954508` — Rate of ListSchemas requests
- `L-8CF613B7` — Rate of ListMemberships requests
- `L-8EADB354` — Rate of ListPrivacyBudgetTemplates requests
- `L-971686CB` — Rate of CreateConfiguredTable requests
- `L-978BC400` — Rate of ListTagsForResource requests
- `L-98BDB219` — Rate of CreateAnalysisTemplate requests
- `L-9FC85564` — Rate of GetConfiguredTable requests
- `L-AA1FCC92` — Rate of CreateConfiguredTableAnalysisRule requests
- `L-AA83E042` — Rate of CreateMembership requests
- `L-BA5CF250` — Rate of ListProtectedJobs requests
- `L-BAAD82E2` — Rate of GetCollaborationChangeRequest requests
- `L-BC5338D1` — Rate of UpdateConfiguredTableAssociation requests
- `L-C0D69AA0` — Rate of DeleteConfiguredTable requests
- `L-C176B0B6` — Rate of DeleteConfiguredTableAssociationAnalysisRule requests
- `L-C21604A2` — Rate of GetPrivacyBudgetTemplate requests
- `L-C36D988B` — Rate of ListPrivacyBudgets requests
- `L-C3A930AB` — Rate of GetCollaborationConfiguredAudienceModelAssociation requests
- `L-C5494CAA` — Rate of ListConfiguredAudienceModelAssociations requests
- `L-C6B48C80` — Query text length (using differential privacy)
- `L-CDE3C47C` — Rate of ListCollaborationPrivacyBudgetTemplates requests
- `L-CEBF94E4` — Rate of CreateIdMappingTable requests
- `L-D29A24D7` — Rate of GetConfiguredTableAssociationAnalysisRule requests
- `L-D3626550` — Rate of UpdateProtectedJob requests
- `L-D3DE47CF` — Rate of ListIdMappingTables requests
- `L-D4ACC820` — Rate of BatchGetCollaborationAnalysisTemplate requests
- `L-D90468BB` — Rate of ListConfiguredTableAssociations requests
- `L-DA8821F5` — Rate of DeleteIdNamespaceAssociation requests
- `L-DB68AF19` — Rate of ListCollaborationChangeRequests requests
- `L-DDC82272` — Rate of UpdateCollaboration requests
- `L-DF39885E` — Rate of UpdateIdMappingTable requests
- `L-DF3C63EF` — Rate of UpdateConfiguredTable requests
- `L-E555FCAB` — Rate of UpdatePrivacyBudgetTemplate requests
- `L-E95B9B79` — Rate of ListCollaborationPrivacyBudgets requests
- `L-EA789CE8` — Rate of GetCollaboration requests
- `L-ED22C809` — Rate of CreateConfiguredAudienceModelAssociation requests
- `L-ED3352DE` — Analysis rule size
- `L-F0A87380` — Rate of DeleteCollaboration requests
- `L-F434A8C7` — Rate of UntagResource requests
- `L-F84196BB` — Rate of UpdateIdNamespaceAssociation requests
- `L-FA0B0432` — Rate of BatchGetSchema requests
- `L-FD7BEEA1` — Rate of UpdateConfiguredTableAssociationAnalysisRule requests

## cleanrooms-ml

- `L-0636843D` — Active audience export jobs per audience generation job
- `L-CDB92F4A` — Active configured model algorithms per membership

## cloud9

- `L-5D26553C` — SSH development environments for this user
- `L-65F36924` — Members per development environment
- `L-A29EDECE` — SSH development environments for this account
- `L-C1302C17` — EC2 development environments for this user

## cloudformation

- `L-05123385` — Nested modules
- `L-084D8074` — Throttle rate limit for DescribeGeneratedTemplate
- `L-0BF4426F` — Throttle rate limit for DescribeResourceScan
- `L-0D1C7C93` — Throttle rate limit for ListGeneratedTemplates
- `L-146A985F` — Throttle rate limit for ExecuteChangeSet
- `L-1A14E2E4` — Throttle rate limit for StartResourceScan
- `L-1DFD712D` — Throttle rate limit for DescribeAccountLimits
- `L-20C6DAFE` — Throttle rate limit for PublishType
- `L-20DF2AC3` — Throttle rate limit for ValidateTemplate
- `L-23572CD8` — Throttle rate limit for ListChangeSets
- `L-24CF89C9` — Throttle rate limit for DetectStackDrift
- `L-255CB302` — Throttle rate limit for DescribeTypeRegistration
- `L-2780AB78` — Throttle rate limit for GetGeneratedTemplate
- `L-28B8E003` — Throttle rate limit for DeleteStackInstances
- `L-2C86E8BE` — Throttle rate limit for ListStackResources
- `L-2E8B8349` — Throttle rate limit for DescribePublisher
- `L-314F0FAF` — Throttle rate limit for ListResourceScanRelatedResources
- `L-330C21EA` — Throttle rate limit for ListStackSetOperations
- `L-36B104FB` — Throttle rate limit for DescribeOrganizationsAccess
- `L-3D1500B6` — Throttle rate limit for CreateChangeSet
- `L-40DA9BBE` — Throttle rate limit for UpdateStackInstances
- `L-421EA159` — Throttle rate limit for BatchDescribeTypeConfigurations
- `L-4276301D` — Wait Condition Signal Data Size
- `L-4731FE6F` — Hooks per resource
- `L-476C2455` — Throttle rate limit for DescribeStackSet
- `L-5019DE71` — Throttle rate limit for ListImports
- `L-507712A5` — Throttle rate limit for DetectStackResourceDrift
- `L-56D7F024` — Throttle rate limit for DeleteStackSet
- `L-5E5E4FDB` — Throttle rate limit for DescribeStackResource
- `L-5F6B90AB` — Throttle rate limit for ActivateOrganizationsAccess
- `L-600058B9` — Stacks imported using S3 object per stack set operation
- `L-6286B93B` — Throttle rate limit for DescribeStackSetOperation
- `L-6A4B2F69` — Stack instance operations per administrator account
- `L-6AD11AD7` — Throttle rate limit for GetStackPolicy
- `L-6C32EB43` — Throttle rate limit for DescribeStackDriftDetectionStatus
- `L-6CD0CA38` — Throttle rate limit for ContinueUpdateRollback
- `L-7460249E` — Throttle rate limit for DescribeType
- `L-7D45582C` — Throttle rate limit for DeleteGeneratedTemplate
- `L-81A7E618` — Throttle rate limit for DetectStackSetDrift
- `L-8497B9EB` — Throttle rate limit for ListStackSetOperationResults
- `L-85EB5DEC` — Throttle rate limit for ListStackSetAutoDeploymentTargets
- `L-86064319` — Throttle rate limit for ListStackInstances
- `L-87CC5A1D` — Throttle rate limit for ListStacks
- `L-87E26E99` — Throttle rate limit for UpdateStack
- `L-8AC284BF` — Throttle rate limit for ListStackInstanceResourceDrifts
- `L-9013C9F2` — Throttle rate limit for ListStackSets
- `L-940CC882` — Throttle rate limit for RollbackStack
- `L-96426F7F` — Throttle rate limit for GetTemplateSummary
- `L-9643581C` — Throttle rate limit for RegisterType
- `L-98DE792C` — Throttle rate limit for StopStackSetOperation
- `L-9C5C273A` — Throttle rate limit for SetStackPolicy
- `L-9C92580D` — Throttle rate limit for GetTemplate
- `L-A2C10225` — Throttle rate limit for DescribeStackResourceDrifts
- `L-AD7355DC` — Throttle rate limit for CancelUpdateStack
- `L-AF237941` — Throttle rate limit for DeleteStack
- `L-AF3916A4` — Throttle rate limit for ListTypeRegistrations
- `L-B3EB153E` — Throttle rate limit for SetTypeDefaultVersion
- `L-B8580123` — Throttle rate limit for DescribeStackResources
- `L-BC67E796` — Throttle rate limit for ListTypes
- `L-BD33AD4A` — Throttle rate limit for ListResourceScans
- `L-BDAD37B8` — Throttle rate limit for CreateStack
- `L-C5C9D8DB` — Throttle rate limit for EstimateTemplateCost
- `L-C870E9A3` — Throttle rate limit for DescribeChangeSet
- `L-CCAA7E63` — Throttle rate limit for DeleteChangeSet
- `L-CD7C16FE` — Throttle rate limit for CreateStackInstances
- `L-CF64D430` — Throttle rate limit for UpdateGeneratedTemplate
- `L-D2B2F0FF` — Stacks imported using inline stack ids per stack set operation
- `L-D5FE38FA` — Throttle rate limit for DescribeStacks
- `L-D76C738E` — Throttle rate limit for ListResourceScanResources
- `L-DCDA1233` — Throttle rate limit for ListExports
- `L-E141E579` — Throttle rate limit for UpdateStackSet
- `L-E388DB0A` — Hook configuration size
- `L-E466BCCD` — Throttle rate limit for CreateGeneratedTemplate
- `L-E4780309` — Throttle rate limit for SignalResource
- `L-E7256C02` — Throttle rate limit for ListTypeVersions
- `L-EFC95CFF` — Template Parameter Value Length
- `L-F0B38CF3` — Throttle rate limit for CreateStackSet
- `L-F3F1561B` — Throttle rate limit for DeregisterType
- `L-F4BB1228` — Throttle rate limit for DescribeStackEvents
- `L-F5B7238C` — Throttle rate limit for UpdateTerminationProtection
- `L-F9FF79DB` — Throttle rate limit for DescribeStackInstance
- `L-FFB2925A` — Custom Resource Response Data

## cloudhsm

- `L-0B35A0E6` — Number of concurrent clients
- `L-0D8B0541` — HSMs per CloudHSM cluster
- `L-194EB2B8` — Minimum length of a password
- `L-36814031` — Keys per CloudHSM cluster
- `L-772318AE` — Length of a Username
- `L-95BA35D1` — HSMs per AWS Region and AWS account
- `L-F847CBBF` — Users per CloudHSM cluster
- `L-F9BBB650` — Length of a password

## cloudshell

- `L-91D31FC1` — Home directory size
- `L-937D704D` — Monthly usage
- `L-AFB6CE78` — Data retention
- `L-C2A56602` — Concurrent shells

## cloudtrail

- `L-08352D4A` — Transactions per second (TPS) for the StartImport API
- `L-08F66A51` — Transactions per second (TPS) for the SearchSampleQueries API
- `L-0DE8FCE1` — Transactions per second (TPS) for the AddTags API
- `L-102075A9` — Transactions per second (TPS) for the GetImport API
- `L-1433C85D` — Event size
- `L-235E2A41` — Transactions per second (TPS) for the PutResourcePolicy API
- `L-262F8D6F` — Transactions per second (TPS) for the GetEventSelectors API
- `L-2A4525B6` — Transactions per second (TPS) for the PutEventSelectors API
- `L-2AAD1FD3` — Transactions per second (TPS) for the DescribeQuery API
- `L-3044E773` — Transactions per second (TPS) for the GetQueryResults API
- `L-33958DE7` — Events per PutAuditEvents request
- `L-33C67BE1` — Transactions per second (TPS) for the GetEventDataStore API
- `L-3AD9B964` — Transactions per second (TPS) for the DeleteChannel API
- `L-400AA82D` — Transactions per second (TPS) for the DeleteResourcePolicy API
- `L-42572559` — Transactions per second (TPS) for the DeleteDashboard API
- `L-46286FE1` — Transactions per second (TPS) for the CreateEventDataStore API
- `L-4964C79E` — Transactions per second (TPS) for the StopEventDataStoreIngestion API
- `L-531B4597` — Transactions per second (TPS) for the UpdateDashboard API
- `L-54F77C56` — Transactions per second (TPS) for the ListTrails API
- `L-58D9CABD` — Transactions per second (TPS) for the ListEventDataStores API
- `L-5E4FC5D2` — Transactions per second (TPS) for the GetTrailStatus API
- `L-62E172F7` — Transactions per second (TPS) for the ListPublicKeys API
- `L-631CF1F1` — Transactions per second (TPS) for the CancelQuery API
- `L-66AE0662` — Transactions per second (TPS) for the GetResourcePolicy API
- `L-6826A2E9` — Transactions per second (TPS) for the LookupEvents API
- `L-694E6530` — Concurrent dashboard refreshes
- `L-72996F38` — Concurrent queries
- `L-773FB33E` — Transactions per second (TPS) for the StartLogging API
- `L-7A3F9D4B` — Transactions per second (TPS) for the GetChannel API
- `L-7AC9FF3E` — Transactions per second (TPS) for the DescribeTrails API
- `L-8191F390` — Transactions per second (TPS) for the StartDashboardRefresh API
- `L-81CCF560` — Transactions per second (TPS) for the ListInsightsMetricData API
- `L-82338BB4` — Transactions per second (TPS) for the UpdateEventDataStore API
- `L-865ADF4E` — Transactions per second (TPS) for the UpdateTrail API
- `L-866533BF` — Transactions per second (TPS) for the DeleteTrail API
- `L-8719FDD4` — Transactions per second (TPS) for the PutInsightSelectors API
- `L-888731F1` — Transactions per second (TPS) for the RestoreEventDataStore API
- `L-88C956C4` — Transactions per second (TPS) for the RegisterOrganizationDelegatedAdmin API
- `L-8F9F4270` — Transactions per second (TPS) for the ListChannels API
- `L-9260AF5B` — Transactions per second (TPS) for the GetTrail API
- `L-9552D44E` — Transactions per second (TPS) for the StopLogging API
- `L-961309DE` — Transactions per second (TPS) for the CreateDashboard API
- `L-98AA9EBA` — Transactions per second (TPS) for the EnableFederation API
- `L-9B1A1B4A` — Transactions per second (TPS) for the UpdateChannel API
- `L-9F37432B` — Transactions per second (TPS) for the DeleteEventDataStore API
- `L-A0136C1A` — CloudTrail file size sent to Amazon S3
- `L-A4CD5068` — Transactions per second (TPS) for the ListImportFailures API
- `L-A60E6D1D` — Transactions per second (TPS) for the PutAuditEvents API
- `L-AD66B35A` — Transactions per second (TPS) for the ListTags API
- `L-AFFDFD7B` — Transactions per second (TPS) for the ListImports API
- `L-B4D176B9` — Transactions per second (TPS) for the StopImport API
- `L-B643CFE7` — Transactions per second (TPS) for the ListDashboards API
- `L-BEA14027` — Transactions per second (TPS) for the DeregisterOrganizationDelegatedAdmin API
- `L-BEC68768` — Transactions per second (TPS) for the CreateChannel API
- `L-C46BC83A` — Transactions per second (TPS) for the GetDashboard API
- `L-C9DC023A` — Transactions per second (TPS) for the CreateTrail API
- `L-D0872747` — Transactions per second (TPS) for the ListQueries API
- `L-D08C1460` — Transactions per second (TPS) for the DisableFederation API
- `L-E2417ECC` — Transactions per second (TPS) for the GetInsightSelectors API
- `L-EA524270` — Transactions per second (TPS) for the StartEventDataStoreIngestion API
- `L-EBC99F5D` — Transactions per second (TPS) for the StartQuery API
- `L-EF071748` — Transactions per second (TPS) for the RemoveTags API

## codeartifact

- `L-0B362111` — GetAuthorizationToken requests per second
- `L-3072382D` — ListPackageVersionAssets requests per second
- `L-308A4050` — CopyPackageVersions requests per second
- `L-37894301` — Requests per second using a single authentication token
- `L-3E27C79F` — PublishPackageVersion requests per second
- `L-5B2BD2E1` — Assets per package version
- `L-5D176989` — Upstream repositories searched
- `L-6010CAF9` — ListPackages requests per second
- `L-6C12FB34` — GetPackageVersionAsset requests per second
- `L-A649E766` — Write requests per second from a single AWS account
- `L-AA0DC56D` — Asset file size
- `L-BD902DFC` — Requests without authentication token per IP address
- `L-CBBCDF5C` — ListPackageVersions requests per second
- `L-F39CF68A` — Read requests per second from a single AWS account

## codebuild

- `L-376C4764` — Minimum period for build timeout in minutes
- `L-390F410B` — Concurrent requests for information on build projects
- `L-42CB2FCC` — Concurrent request for information about builds

## codedeploy

- `L-31E782CD` — Number of instances that can be passed to the BatchGetOnPremisesInstances API action
- `L-5FB5F09F` — Traffic that can be shifted in one increment during an AWS Lambda deployment
- `L-604B54B8` — AWS Lambda deployment run in hours
- `L-69184564` — Minutes a blue/green deployment can wait after a successful deployment before terminating instances from the original deployment
- `L-696A9A65` — Size of tag key
- `L-826E27D8` — Tags in a deployment group
- `L-86A1A2E1` — Minutes between the first and last traffic shift during an AWS Lambda canary or linear deployment
- `L-9231961D` — Minutes until a deployment fails if a lifecycle event doesn't start
- `L-A58C473C` — Hours between the completion of a deployment and the termination of the original instances during an EC2/On-Premises blue/green deployment
- `L-B2AEFF5A` — Size of tag value
- `L-B8C6A115` — Hours between the deployment of a revision and when traffic shifts to the replacement instances during an EC2/On-Premises blue/green deployment
- `L-BB837EF6` — Seconds until a deployment lifecycle event fails if not completed
- `L-D4ED2A8C` — Size of deployment group name
- `L-DC0E5D95` — EC2/On-Premises blue/green deployment run in hours
- `L-F0A94AA0` — EC2/On-Premises in-place deployment run in hours

## codeguru-reviewer

- `L-F5129FC6` — Allowed Code Reviews

## codepipeline

- `L-182AE5D8` — Action configuration key length
- `L-1E23CE75` — Total AWS CodeCommit or GitHub source artifact size
- `L-31A751EC` — Total period for execution history
- `L-3ECA8567` — Total input artifact size for AWS CloudFormation deployments
- `L-447DD651` — AWS CloudFormation action timeout
- `L-5AA45A27` — Action timeout
- `L-6F95DA01` — Action configuration value length
- `L-87C878A5` — AWS CodeDeploy ECS (Blue/Green) action timeout
- `L-912817AD` — AWS Lambda action timeout
- `L-9D72EF0D` — Total Amazon S3 source artifact size
- `L-A95CB60D` — Approval action timeout
- `L-ABB870A7` — Amazon S3 deployment action timeout
- `L-C57FFB43` — Minimum actions
- `L-C5885C1C` — Total pipelines with change detection set to periodically checking for source changes
- `L-C8CB041B` — Minimum stages per pipeline
- `L-CE1F2EE9` — AWS CodeDeploy action timeout
- `L-DCBA35EE` — Total image definitions JSON file size
- `L-F2AD11A6` — Total source artifact size for Amazon EBS deployments
- `L-F7192911` — AWS CodeBuild action timeout
- `L-F8F56C9F` — Total JSON object size for Parameter Overrides

## cognito-identity

- `L-0BF99E8D` — Rate of GetOpenIdTokenForDeveloperIdentity requests
- `L-0D31D6D2` — Rate of UntagResource requests
- `L-14403AD5` — User pool providers per identity pool
- `L-1F1BC060` — Role-based access control rules
- `L-29CA570C` — Identity pool name size
- `L-50C9AAB8` — Rate of ListTagsForResource requests
- `L-5AE9F13D` — Rate of GetCredentialsForIdentity requests
- `L-A38ADA84` — Rate of GetId requests
- `L-B08F14B9` — Login provider name size
- `L-DAF3EAFF` — Rate of TagResource requests
- `L-DBF99350` — Rate of ListIdentities requests
- `L-E97D135E` — Rate of GetOpenIdToken requests
- `L-EAF710D2` — List API call results

## cognito-idp

- `L-026ADBA3` — Rate of UserAuthentication requests
- `L-04F7DFB8` — Rate of UserPoolClientUpdate requests per user pool
- `L-12C4D74A` — Rate of UserPoolClientUpdate requests per account
- `L-181E40D0` — Rate of UserPoolResourceRead requests per user pool
- `L-259E3368` — Rate of UserList requests
- `L-3F0DE77D` — Groups per user
- `L-55545DC8` — Rate of UserResourceRead requests
- `L-574C86AE` — Rate of UserResourceUpdate requests
- `L-5987B8A0` — Rate of UserCreation requests
- `L-60A0B411` — Rate of UserPoolUpdate requests
- `L-6621E65D` — Rate of UserUpdate requests
- `L-681BB884` — User import jobs per user pool
- `L-74D3DD04` — Rate of ClientAuthentication requests per account
- `L-7D6E8ED3` — Rate of UserAccountRecovery requests
- `L-A01C9633` — Rate of UserPoolResourceRead requests per account
- `L-A412573D` — Rate of UserPoolClientRead requests per account
- `L-B7575496` — Rate of UserPoolResourceUpdate requests per account
- `L-BB3E7CCF` — Rate of UserFederation requests
- `L-BC27731B` — Rate of UserPoolResourceUpdate requests per user pool
- `L-CFFBE34A` — Rate of UserPoolRead requests
- `L-D6BD5178` — Rate of UserRead requests
- `L-F122EFFD` — Rate of UserPoolClientRead requests per user pool
- `L-F21F8BB4` — Rate of UserToken requests

## cognito-sync

- `L-239B0C0A` — Bulk publish wait time
- `L-2625A4A0` — Datasets per identity
- `L-4CD747A5` — Dataset name size
- `L-97A9518B` — Records per dataset
- `L-C5EE478A` — Dataset size

## comprehend

- `L-0B530363` — StopEntitiesDetectionJob throttle limit in transactions per second
- `L-0F06FE42` — ListEventsDetectionJobs throttle limit in transactions per second
- `L-10AEC0BE` — StopSentimentDetectionJob throttle limit in transactions per second
- `L-13861BA2` — ListSentimentDetectionJobs throttle limit in transactions per second
- `L-13A0494F` — DescribeTopicsDetectionJob throttle limit in transactions per second
- `L-1EEF8E8F` — StopPiiEntitiesDetectionJob throttle limit in transactions per second
- `L-230B53F3` — StartTargetedSentimentDetectionJob throttle limit in transactions per second
- `L-243FFDDD` — CreateDocumentClassifier throttle limit in transactions per second
- `L-3E342F88` — DescribeKeyPhrasesDetectionJob throttle limit in transactions per second
- `L-3FD9ACEB` — StartDominantLanguageDetectionJob throttle limit in transactions per second
- `L-40A899B3` — ListEntitiesDetectionJobs throttle limit in transactions per second
- `L-428EEE9B` — DescribeEntitiesDetectionJob throttle limit in transactions per second
- `L-438FD9AD` — ListTopicsDetectionJobs throttle limit in transactions per second
- `L-4D712CC8` — StartKeyPhrasesDetectionJob throttle limit in transactions per second
- `L-4DD99000` — StopTargetedSentimentDetectionJob throttle limit in transactions per second
- `L-5454BD4C` — ListPiiEntitiesDetectionJobs throttle limit in transactions per second
- `L-5674A323` — StartDocumentClassificationJob throttle limit in transactions per second
- `L-5BADD54F` — ListEntityRecognizers throttle limit in transactions per second
- `L-60ABC79C` — DescribeDominantLanguageDetectionJob throttle limit in transactions per second
- `L-67D99149` — StopDominantLanguageDetectionJob throttle limit in transactions per second
- `L-68C199F3` — StartEventsDetectionJob throttle limit in transactions per second
- `L-6ECBDFF6` — UntagResource throttle limit in transactions per second
- `L-7820536E` — ListDocumentClassifiers throttle limit in transactions per second
- `L-7B91C94D` — StartSentimentDetectionJob throttle limit in transactions per second
- `L-8532F92C` — ListDominantLanguageDetectionJobs throttle limit in transactions per second
- `L-8DD67684` — StartEntitiesDetectionJob throttle limit in transactions per second
- `L-91446453` — DescribeDocumentClassificationJob throttle limit in transactions per second
- `L-9A845B3A` — TagResource throttle limit in transactions per second
- `L-9E526A5F` — DescribeTargetedSentimentDetectionJob throttle limit in transactions per second
- `L-A1AF2FE3` — DescribeEventsDetectionJob throttle limit in transactions per second
- `L-A1F7E693` — ListDocumentClassificationJobs throttle limit in transactions per second
- `L-A207C175` — CreateEntityRecognizer throttle limit in transactions per second
- `L-C220288F` — ListTargetedSentimentDetectionJobs throttle limit in transactions per second
- `L-C39735E0` — DescribeDocumentClassifier throttle limit in transactions per second
- `L-C7E12CA2` — StopKeyPhrasesDetectionJob throttle limit in transactions per second
- `L-CA1326CD` — StopEventsDetectionJob throttle limit in transactions per second
- `L-CF92EEE2` — StopTrainingEntityRecognizer throttle limit in transactions per second
- `L-D4C039C8` — ListTagsForResource throttle limit in transactions per second
- `L-D6BBB77F` — DeleteDocumentClassifier throttle limit in transactions per second
- `L-E0EFA344` — DescribeSentimentDetectionJob throttle limit in transactions per second
- `L-E1D53C9F` — StopTrainingDocumentClassifier throttle limit in transactions per second
- `L-E7F70588` — DeleteEntityRecognizer throttle limit in transactions per second
- `L-E9B0ABA2` — ListKeyPhrasesDetectionJobs throttle limit in transactions per second
- `L-E9F2B1B1` — DescribePiiEntitiesDetectionJob throttle limit in transactions per second
- `L-F039F1E3` — DescribeEntityRecognizer throttle limit in transactions per second
- `L-F91E977B` — StartTopicsDetectionJob throttle limit in transactions per second
- `L-FBEC67FF` — StartPiiEntitiesDetectionJob throttle limit in transactions per second

## connect

- `L-000B6A1A` — Rate of UpdateTaskTemplate API requests
- `L-01980B0F` — Rate of AssociateRoutingProfileQueues API requests
- `L-020883A7` — Rate of UpdateUserHierarchyGroupName API requests
- `L-02F9E992` — Rate of CreateDataTableAttribute API requests
- `L-0711FF1F` — Rate of ListRules API requests
- `L-08DF489D` — Rate of DescribeAgentStatus API requests
- `L-09AAE068` — Rate of ListHoursOfOperations API requests
- `L-0D791E12` — Rate of ListTaskTemplates API requests
- `L-0E9EA5C5` — Rate of BatchDescribeDataTableValue API requests
- `L-100FDD6A` — Rate of EvaluateDataTableValues API requests
- `L-1210FC76` — Rate of ResumeContact API requests
- `L-12900DCA` — Rate of ListSecurityProfilePermissions API requests
- `L-12A6C748` — Rate of SearchAgentStatuses API requests
- `L-12AB7C57` — Concurrent active calls per instance
- `L-1317E3B0` — Rate of UpdateQueueHoursOfOperation API requests
- `L-159E202B` — Rate of CreateSecurityProfile API requests
- `L-1643345D` — Rate of DescribeDataTableAttribute API requests
- `L-16BF00C7` — Rate of ListRoutingProfileQueues API requests
- `L-1775C3F8` — Rate of UpdateUserHierarchyStructure API requests
- `L-17DC1373` — Rate of UpdateSecurityProfile API requests
- `L-18108401` — Rate of UpdateContactSchedule API requests
- `L-185BE3DB` — Rate of CreateTaskTemplate API requests
- `L-1955649E` — Rate of DescribeDataTable API requests
- `L-19D865C6` — Rate of DeleteContactFlowModule API requests
- `L-1A44121A` — Rate of CreateIntegrationAssociation API requests
- `L-1AB8E9D9` — Rate of CreateVocabulary API requests
- `L-1AF438BB` — Rate of CreatePushNotificationRegistration API requests
- `L-1F455046` — Rate of DisassociateSecurityKey API requests
- `L-21385E28` — Rate of ClaimPhoneNumber API requests
- `L-22C4CED1` — Rate of SuspendContactRecording API requests
- `L-22F9A3D8` — Rate of DescribeVocabulary API requests
- `L-230B11C5` — Rate of MonitorContact API requests
- `L-241FA7AE` — Supervisors per staffing group
- `L-25E54F7C` — Rate of DisassociateLexBot API requests
- `L-26D9F60B` — Rate of UntagResource API requests
- `L-272F1E62` — Rate of CreateQuickConnect API requests
- `L-2AADC77E` — Rate of CreateInstance API requests
- `L-2AF5EEF5` — Rate of DescribeSecurityProfile API requests
- `L-2BDBF248` — Rate of DismissUserContact API requests
- `L-2BE4D75F` — External voice transfer connectors per account
- `L-2CCBA953` — Rate of AssociateUserProficiencies API requests
- `L-2D464A68` — Rate of CreateHoursOfOperationOverride API requests
- `L-2DB48531` — Rate of UpdateAgentStatus API requests
- `L-2DE43297` — Rate of DescribeQuickConnect API requests
- `L-2E719449` — Rate of GetMetricDataV2 API requests
- `L-2F996DE6` — Rate of DescribeInstanceAttribute API requests
- `L-2FC23A76` — Rate of StopContactStreaming API requests
- `L-30488271` — Rate of DeleteUser API requests
- `L-30929A21` — Rate of ListRoutingProfiles API requests
- `L-3118109A` — Rate of CreateAgentStatus API requests
- `L-3233242F` — Concurrent uploads per instance
- `L-3324D6A9` — Rate of UpdateDataTableMetadata API requests
- `L-3481440F` — Rate of SearchSecurityProfiles API requests
- `L-34F440B5` — Rate of DescribePhoneNumber API requests
- `L-371095B8` — Rate of DescribeContact API requests
- `L-3741AF59` — Rate of UpdateContactFlowName API requests
- `L-379E909D` — Rate of GetTrafficDistribution API requests
- `L-37E92540` — Rate of UpdateParticipantRoleConfig API requests
- `L-3A13A048` — File size per upload of capacity plan overrides
- `L-3A7EFE53` — Rate of ListRoutingProfileManualAssignmentQueues API requests
- `L-3EEA2922` — Rate of StartContactRecording API requests
- `L-3F3E67D1` — Rate of SearchResourceTags API requests
- `L-3F6301E8` — Rate of DescribePrompt API requests
- `L-408DD6C6` — Rate of StartOutboundChatContact API requests
- `L-40BDE29F` — Rate of DescribeRule API requests
- `L-40C15531` — Rate of UpdateContact API requests
- `L-40F4B10D` — Rate of UpdateInstanceAttribute API requests
- `L-4161472A` — Rate of DeleteDataTable API requests
- `L-418ABD80` — Rate of UpdateUserRoutingProfile API requests
- `L-41C7214A` — Rate of DescribeContactFlow API requests
- `L-43B4F8CE` — Rate of TransferContact API requests
- `L-4409B44A` — Rate of DeleteTrafficDistributionGroup API requests
- `L-44302794` — Rate of UpdateHoursOfOperationOverride API requests
- `L-44B5DA37` — Rate of ListQuickConnects API requests
- `L-44BB2CC5` — Rate of SearchHoursOfOperations API requests
- `L-456FA19E` — Rate of ListHoursOfOperationOverrides API requests
- `L-45BAE507` — Rate of AssociateLexBot API requests
- `L-4641705A` — Rate of ListContactFlows API requests
- `L-467CADD3` — Rate of ListLexBots API requests
- `L-476CE930` — Rate of BatchUpdateDataTableValue API requests
- `L-4AAC8E79` — Rate of UpdateRoutingProfileName API requests
- `L-4AE2F6BF` — Rate of AssociateLambdaFunction API requests
- `L-4C062DDC` — Rate of UpdateContactFlowContent API requests
- `L-4E9BCC96` — Rate of StartOutboundVoiceContact API requests
- `L-4EA7C312` — Rate of UpdateQueueMaxContacts API requests
- `L-4FBE591E` — Rate of SearchUserHierarchyGroups API requests
- `L-50B4DE11` — Rate of PutUserStatus API requests
- `L-50C3EE60` — Rate of UntagContact API requests
- `L-50D07AB9` — Rate of DescribeUserHierarchyGroup API requests
- `L-52794498` — Rate of GetMetricData API requests
- `L-53E03705` — Rate of DisassociateUserProficiencies API requests
- `L-56B34560` — Rate of DescribeContactFlowModule API requests
- `L-5755F8EC` — Rate of CreateUseCase API requests
- `L-57DF9146` — Rate of DescribeInstanceStorageConfig API requests
- `L-57EBCF95` — Rate of DeleteHoursOfOperation API requests
- `L-59F577B1` — Schedules per instance
- `L-5A3065E6` — Rate of UpdateUserProficiencies API requests
- `L-5AB302E1` — Rate of UpdateQueueStatus API requests
- `L-5AD48B1A` — Rate of ReplicateInstance API requests
- `L-5AF7EB96` — Rate of GetContactAttributes API requests
- `L-5B601B18` — Rate of AssociateSecurityKey API requests
- `L-5C79A188` — Rate of DescribeHoursOfOperationOverride API requests
- `L-5CB19903` — Rate of ListInstanceAttributes API requests
- `L-5CE2FEE8` — Capacity planning scenarios per instance
- `L-5CFC10A5` — Rate of StartWebRTCContact API requests
- `L-5D8210C3` — Rate of UpdateUserPhoneConfig API requests
- `L-5E9E65F2` — Rate of UpdateRoutingProfileQueues API requests
- `L-5F32FD78` — Rate of DescribeUserHierarchyStructure API requests
- `L-601C68F6` — Rate of ListTagsForResource API requests
- `L-60553137` — Concurrent active tasks per instance
- `L-6271E27A` — Rate of ListQueueQuickConnects API requests
- `L-62CF8E4F` — Capacity plans per instance
- `L-64992552` — Forecast groups per instance
- `L-64B27051` — Rate of UpdateUserSecurityProfiles API requests
- `L-650BD10F` — Rate of StopContact API requests
- `L-66B5F86E` — Rate of UpdateUserIdentityInfo API requests
- `L-6751163B` — Rate of DeleteUserHierarchyGroup API requests
- `L-67F605FD` — Staffing groups per supervisor
- `L-6840C932` — Rate of ListContactReferences API requests
- `L-68E1D2C7` — Rate of ListDataTablePrimaryValues API requests
- `L-6C658B70` — Rate of SearchVocabularies API requests
- `L-6DF53542` — Rate of ListBots API requests
- `L-6E6B18DB` — Rate of UpdateHoursOfOperation API requests
- `L-6F6E1C97` — Rate of SearchHoursOfOperationOverrides API requests
- `L-6FB811CE` — Rate of SearchQuickConnects API requests
- `L-71DDC3F5` — Agents per schedule
- `L-731F613E` — Rate of AssociateDefaultVocabulary API requests
- `L-7408C40F` — Rate of SearchDataTables API requests
- `L-753B94AB` — Rate of DescribePredefinedAttribute API requests
- `L-75490F5A` — Rate of CreatePredefinedAttribute API requests
- `L-759067FC` — Rate of PauseContact API requests
- `L-75EE66CE` — Rate of CreateRule API requests
- `L-76EF4B62` — Rate of DisassociateInstanceStorageConfig API requests
- `L-76F318C5` — Rate of BatchPutContact API requests
- `L-781E5E85` — Rate of CreateTrafficDistributionGroup API requests
- `L-78937F3A` — Rate of ListDefaultVocabularies API requests
- `L-78A553AE` — Rate of DeleteVocabulary API requests
- `L-79564E52` — Reports per instance
- `L-7AA5113F` — Rate of DeleteRule API requests
- `L-7DBD293C` — Rate of SendIntegrationEvent API requests
- `L-7FA26DC8` — Rate of ResumeContactRecording API requests
- `L-80204DDC` — Rate of UpdateContactFlowModuleMetadata API requests
- `L-80A82D5F` — Rate of ListApprovedOrigins API requests
- `L-8157C163` — Rate of SearchQueues API requests
- `L-82C99962` — Rate of GetContactMetrics API requests
- `L-83963769` — Rate of DisassociateRoutingProfileQueues API requests
- `L-839A2EDC` — Rate of DescribeRoutingProfile API requests
- `L-84CCC70A` — Rate of DeletePredefinedAttribute API requests
- `L-8787723E` — Rate of AssociateApprovedOrigin API requests
- `L-87C02971` — Rate of GetTaskTemplate API requests
- `L-89B2A386` — Rate of ListContactFlowModules API requests
- `L-8B34D696` — Rate of AssociateContactWithUser API requests
- `L-8BFD043A` — Rate of ListInstanceStorageConfigs API requests
- `L-8C43A191` — Rate of AssociateBot API requests
- `L-8CE99751` — Rate of CreateRoutingProfile API requests
- `L-8FAD6E1F` — Shift activities per instance
- `L-8FE21897` — Rate of CreateParticipant API requests
- `L-91A40F24` — Rate of ReleasePhoneNumber API requests
- `L-93006646` — Rate of ListDataTables API requests
- `L-93412F17` — Rate of StartContactStreaming API requests
- `L-96329A5A` — Rate of UpdateContactFlowMetadata API requests
- `L-986AE5E3` — Scheduled reports per instance
- `L-98A4FE2C` — Rate of DeleteDataTableAttribute API requests
- `L-98C95556` — Rate of ListInstances API requests
- `L-9959E55D` — Rate of ListPhoneNumbers API requests
- `L-9AA558F3` — Rate of GetFederationToken API requests
- `L-9B84048E` — Rate of StartScreenSharing API requests
- `L-9CF39F22` — Rate of DeleteIntegrationAssociation API requests
- `L-9DAC7B1B` — Rate of SearchRoutingProfiles API requests
- `L-9E54B88B` — Rate of GetCurrentUserData API requests
- `L-9FF2F6AB` — Staffing groups per Forecast group
- `L-A0E2082D` — Voice ID integration associations per instance
- `L-A218697D` — Rate of CreateContactFlow API requests
- `L-A250B0F6` — Rate of UpdateQueueName API requests
- `L-A277A9A0` — Rate of DeleteHoursOfOperationOverride API requests
- `L-A3079FC2` — Staffing groups per instance
- `L-A408782D` — Rate of ListSecurityProfiles API requests
- `L-A59C54EE` — Rate of ListUserProficiencies API requests
- `L-A6BE227D` — Rate of ListIntegrationAssociations API requests
- `L-A84FDAD7` — Rate of UpdateQuickConnectName API requests
- `L-A9886A7C` — Rate of ListPrompts API requests
- `L-AA48CD49` — Rate of StartChatContact API requests
- `L-AAE06E27` — Rate of TagContact API requests
- `L-AEAF5C4B` — Rate of UpdateUserHierarchy API requests
- `L-AEE2C982` — Rate of UpdateInstanceStorageConfig API requests
- `L-AEFB3FB7` — Rate of UpdateRule API requests
- `L-AF3C38D5` — Rate of SearchAvailablePhoneNumbers API requests
- `L-AFE616A6` — Rate of AssociateQueueQuickConnects API requests
- `L-B07B2C56` — Rate of ListPhoneNumbersV2 API requests
- `L-B117F12F` — Concurrent active emails per instance
- `L-B1987D6A` — Rate of AssociateInstanceStorageConfig  API requests
- `L-B1EC95D9` — Rate of UpdateQueueOutboundCallerConfig API requests
- `L-B29D0CD1` — Rate of UpdateQuickConnectConfig API requests
- `L-B7E1268D` — Rate of UpdatePhoneNumber API requests
- `L-B9220F3B` — Rate of DeleteInstance API requests
- `L-BA434818` — Rate of DeletePushNotificationRegistration API requests
- `L-BBBDDEDC` — Rate of DeleteContactFlow API requests
- `L-BC61DC58` — Rate of DisassociateQueueQuickConnects API requests
- `L-BD0B57EC` — Rate of DeleteSecurityProfile API requests
- `L-BE2447CC` — Rate of ListPredefinedAttributes API requests
- `L-C06273D6` — Rate of DisassociateBot API requests
- `L-C174EC88` — Shift activities per shift profile
- `L-C1DA0AD4` — Rate of StopContactRecording API requests
- `L-C260F37F` — Rate of UpdateContactFlowModuleContent API requests
- `L-C32AFAAE` — Rate of CreateHoursOfOperation API requests
- `L-C56E3A3C` — Rate of ListQueues API requests
- `L-C595FFE9` — Rate of DisassociateApprovedOrigin API requests
- `L-C5C511CD` — Rate of DisassociateLambdaFunction API requests
- `L-C8237495` — Rate of UpdateRoutingProfileDefaultOutboundQueue API requests
- `L-C970C7E8` — Contact Lens connectors per account
- `L-CBDEE3E4` — Rate of CreateUser API requests
- `L-CCC38177` — Rate of ListUsers API requests
- `L-CDC861C1` — Rate of DeleteUseCase API requests
- `L-CEDB17C8` — Rate of UpdateDataTablePrimaryValues API requests
- `L-CF8DBCAD` — Capacity plan user data uploads per instance
- `L-D04B6FBE` — Rate of ListUseCases API requests
- `L-D14CF86E` — Rate of DescribeInstance API requests
- `L-D2ECB451` — Rate of AssociatePhoneNumberContactFlow API requests
- `L-D4BA6F6E` — Concurrent active chats per instance
- `L-D6D4A2DA` — Rate of ListAgentStatuses API requests
- `L-D7F21423` — Rate of DeleteTaskTemplate API requests
- `L-D9BB0F83` — Rate of ListLambdaFunctions API requests
- `L-DA469EE8` — Rate of CreateContactFlowModule API requests
- `L-DA88F710` — Maximum active recording sessions from external voice systems per instance
- `L-DB5A7716` — Rate of ListSecurityKeys API requests
- `L-DB5F63B4` — Rate of SearchPredefinedAttributes API requests
- `L-DD5F6903` — Rate of DescribeTrafficDistributionGroup API requests
- `L-DF4FC88B` — Rate of CreateQueue API requests
- `L-E09E7401` — Forecast override uploads per instance
- `L-E0E93115` — Rate of UpdateRoutingProfileConcurrency API requests
- `L-E2244126` — Rate of SearchPrompts API requests
- `L-E230854C` — Rate of UpdateTrafficDistribution API requests
- `L-E2C35CCE` — Rate of SearchUsers API requests
- `L-E423F15D` — Shift profiles per instance
- `L-E4666753` — Historical actuals uploads per instance
- `L-E621D747` — Rate of CreateUserHierarchyGroup API requests
- `L-E644BA2E` — Queues per forecast group
- `L-E6DB6D6D` — Rate of ListUserHierarchyGroups API requests
- `L-E704D621` — Rate of StartTaskContact API requests
- `L-E74D74A6` — Rate of UpdateQueueOutboundEmailConfig API requests
- `L-E8E90FC3` — Rate of BatchCreateDataTableValue API requests
- `L-E908C3A1` — Concurrent campaign active calls per instance
- `L-EA358306` — Rate of TagResource API requests
- `L-EC183450` — Rate of GetEffectiveHoursOfOperations API requests
- `L-EC633E57` — Rate of DeleteQuickConnect API requests
- `L-ECE54E5A` — Shift rotation pattern steps per shift profile
- `L-ED2B0490` — Rate of GetCurrentMetricData API requests
- `L-EE6F0D82` — Rate of DescribeUser API requests
- `L-EF2F987D` — Rate of CreateDataTable API requests
- `L-F001E5ED` — Rate of UpdateContactAttributes API requests
- `L-F6EB2DE1` — Rate of DescribeHoursOfOperation API requests
- `L-F758F15D` — Shift rotation patterns per instance
- `L-F7E8A253` — Rate of DisassociatePhoneNumberContactFlow API requests
- `L-F97FEF0D` — Rate of ListDataTableValues API requests
- `L-F9BE2186` — Capacity plan override uploads per instance
- `L-FA1E1138` — File size per upload of forecast overrides
- `L-FA43E8DF` — Agents per staffing group
- `L-FAC57D08` — Rate of DescribeQueue API requests
- `L-FBA0478F` — Rate of UpdatePredefinedAttribute API requests
- `L-FBDF9277` — File size per upload of capacity plan user data
- `L-FC15C865` — Rate of UpdateDataTableAttribute API requests
- `L-FE3C3BC3` — Rate of BatchDeleteDataTableValue API requests
- `L-FF4585DE` — Rate of ListTrafficDistributionGroups API requests
- `L-FF826748` — File size per upload of historical actuals
- `L-FFF609B4` — Rate of ListDataTableAttributes API requests

## controltower

- `L-04D09B14` — Concurrent account operations quota
- `L-6579BCE4` — Concurrent organization units (OUs) operations quota

## databrew

- `L-935D4120` — Concurrent jobs per AWS account
- `L-B06AE58E` — Node capacity per AWS account

## dataexchange

- `L-2BA57A8A` — Amazon Redshift datashare assets per import job from Redshift
- `L-340ED0B2` — Concurrent in progress jobs to delete data grants
- `L-514CB613` — Asset size in GB
- `L-694A226E` — Assets per import job from Amazon S3
- `L-916D9CEE` — Revisions per addRevisions change set
- `L-B13AFAD0` — Asset per export job from Amazon S3
- `L-D05CF9CD` — Products per data set
- `L-F1756D86` — Concurrent in progress jobs to create data grants

## datasync

- `L-1FEC79AD` — Throughput per task
- `L-DF42D66D` — Files per task

## datazone

- `L-7EC59F3E` — Data source runs/data source/day
- `L-BA2CE78A` — Data Products
- `L-DBBF7161` — Business Glossary Terms

## deadline

- `L-2CCF07BF` — Spot G Instance GPUs per region
- `L-3DE82FE6` — Tasks per step
- `L-3ED8FD3C` — OnDemand vCPUs per region
- `L-5D6BA491` — OnDemand G instance GPUs per region
- `L-711C7611` — Storage for General Purpose SSD (gp3) volumes, in TiB
- `L-9F7AA0C8` — Resource configurations per fleet
- `L-B65B621C` — Wait-and-save vCPUs per region
- `L-BABD8718` — Steps per job
- `L-CF66A041` — Tasks per job
- `L-EFCAFDCA` — License sessions per license endpoint
- `L-F4A135EC` — Spot vCPUs per region
- `L-F9F8B66A` — Associated members per job

## directconnect

- `L-0B7EBFD7` — Public or private virtual interfaces per dedicated connection
- `L-3024BDA6` — Routes per BGP session on private or transit virtual interfaces
- `L-5A971579` — Members per LAG
- `L-65FD60CB` — Direct Connect gateways per transit gateway
- `L-71C3BCCF` — Virtual interfaces per Direct Connect gateway
- `L-7B428EA3` — Transit virtual interfaces per dedicated connection
- `L-7F59CBF8` — Routes per BGP session on public virtual interfaces
- `L-9BCB4CD9` — Transit gateways per AWS Direct Connect gateway
- `L-A1004C93` — Prefixes per transit gateway
- `L-FDE06981` — Virtual private gateways per Direct Connect gateway

## discovery

- `L-5BC4442B` — Inactive agents heartbeating but not collecting data
- `L-9031D934` — Imported server records per account
- `L-AD9963F2` — Active agents sending data to the service
- `L-B88D303A` — Servers per application
- `L-D0845C33` — Deletions of import records per day
- `L-EC09FB9C` — Tags per server
- `L-F2981287` — Applications per account

## dms

- `L-2146F1FD` — Endpoints per instance
- `L-233F27C4` — Number of data files DMS Fleet Advisor can send per hour
- `L-49123F1B` — Number of monitored objects in DMS Fleet Advisor collector
- `L-6FA8C1C1` — The amount of collected data in DMS Fleet Advisor
- `L-70AA6054` — Number of database objects DMS Fleet Advisor can process
- `L-BBDCBDC8` — Total storage

## docdb

- `L-3B0E1499` — Tags per resource

## docdb-elastic

- `L-00CE4D32` — Manual cluster snapshots
- `L-A5B61A35` — Tags per resource
- `L-BA054AA8` — Elastic clusters vCPU limit

## ds

- `L-25146888` — AWS Managed Microsoft AD domain controllers
- `L-92A19B29` — AWS Managed Microsoft AD manual snapshots

## dsql

- `L-9A50E9F1` — Cluster size
- `L-AA07A0EE` — Connections per cluster

## dynamodb

- `L-1BB77E89` — Concurrent control plane operations
- `L-2A593B99` — Maximum Incremental Export concurrent data size
- `L-34F6A552` — Account-level read throughput limit (Provisioned mode)
- `L-34F8CCC8` — Account-level write throughput limit (Provisioned mode)
- `L-6F30DCE1` — Maximum Incremental Export period window
- `L-923BEB7A` — Write throughput limit for DynamoDB Streams (Provisioned mode)
- `L-AB614373` — Table-level write throughput limit
- `L-C2098644` — Minimum Incremental Export period window
- `L-CF0CBE56` — Table-level read throughput limit
- `L-D98E8184` — Maximum Incremental Export concurrent requests
- `L-F3CA5463` — Provisioned capacity decreases per day

## ebs

- `L-028ACFB9` — GetSnapshotBlock requests per snapshot
- `L-1774F84A` — PutSnapshotBlock requests per snapshot
- `L-18E976AB` — ListSnapshotBlocks requests per account
- `L-1D4D9345` — CompleteSnapshot requests per account
- `L-35B31D98` — IOPS modifications for Provisioned IOPS SSD (io2) volumes
- `L-39BD5252` — Max concurrent copy volume operations per account
- `L-59C8FC87` — Storage modifications for General Purpose SSD (gp3) volumes, in TiB
- `L-5F80CA91` — Storage modifications for Provisioned IOPS SSD (io1) volumes, in TiB
- `L-651D1834` — Storage modifications for Cold HDD (sc1) volumes, in TiB
- `L-8656991D` — Concurrent snapshot copies per destination Region
- `L-87C9DEA6` — Storage modifications for Throughput Optimized HDD (st1) volumes, in TiB
- `L-94D7AB7D` — StartSnapshot pending snapshots per account
- `L-98A0B26D` — IOPS modifications for Provisioned IOPS SSD (io1) volumes
- `L-9A0E0F82` — Storage modifications for Provisioned IOPS SSD (io2) volumes, in TiB
- `L-A37D9CF3` — Provisioned Rate for Volume Initialization across concurrent volume creation requests per Region
- `L-AFAE1BE8` — PutSnapshotBlock requests per account
- `L-AFEBDF7A` — StartSnapshot requests per account
- `L-B9F7C487` — Storage modifications for Magnetic (standard) volumes, in TiB
- `L-C125AE42` — GetSnapshotBlock requests per account
- `L-DB2FBAA1` — ListChangedBlocks requests per account
- `L-E137849C` — Time-based snapshot copy throughput per destination Region
- `L-F06E64A8` — Storage modifications for General Purpose SSD (gp2) volumes, in TiB

## ec2

- `L-1216C47A` — Running On-Demand Standard (A, C, D, H, I, M, R, T, Z) instances
- `L-1945791B` — Running On-Demand Inf instances
- `L-24E8B4C0` — Concurrent TRN2 Capacity Blocks per organization
- `L-2C3B7624` — Running On-Demand Trn instances
- `L-34B43A08` — All Standard (A, C, D, H, I, M, R, T, Z) Spot Instance Requests
- `L-3819A6DF` — All G and VT Spot Instance Requests
- `L-417A185B` — Running On-Demand P instances
- `L-43872EB7` — Route Tables per transit gateway
- `L-43DA4232` — Running On-Demand High Memory instances
- `L-62499967` — Pending peering attachments per transit gateway
- `L-6AF8B990` — Entries in a client certificate revocation list for Client VPN endpoints
- `L-6B0D517C` — All Trn Spot Instance Requests
- `L-6E869C2A` — Running On-Demand DL instances
- `L-7212CCBC` — All P4, P3 and P2 Spot Instance Requests
- `L-7295265B` — Running On-Demand X instances
- `L-74FC7D96` — Running On-Demand F instances
- `L-7EA86503` — Concurrent P5en Capacity Blocks per organization
- `L-8131B2C6` — Concurrent P5 Capacity Blocks per organization
- `L-85EED4F7` — All DL Spot Instance Requests
- `L-88CF9481` — All F Spot Instance Requests
- `L-92B73F21` — Dynamic routes advertised from CGW to VPN connection
- `L-9AC70153` — Concurrent P4de Capacity Blocks per organization
- `L-A1B5A36F` — Peering attachments per transit gateway
- `L-AD1D1866` — Concurrent P5e Capacity Blocks per organization
- `L-B36AAB51` — Concurrent P6-B200 Capacity Blocks per organization
- `L-B5D1601B` — All Inf Spot Instance Requests
- `L-B67430DE` — Concurrent P4d Capacity Blocks per organization
- `L-B7E6B313` — Concurrent P6e-GB200 Capacity Blocks per organization
- `L-BCC1FB47` — Routes per transit gateway
- `L-C4947F9A` — Concurrent TRN1 Capacity Blocks per organization
- `L-C4BD4855` — All P5 Spot Instance Requests
- `L-D0B7243C` — New Reserved Instances per month
- `L-D92B9F5B` — VPC Attachment Bandwidth
- `L-DB0BBC4E` — Routes advertised from VPN connection to CGW
- `L-DB2E81BA` — Running On-Demand G and VT instances
- `L-E0233F82` — Attachments per transit gateway
- `L-E3A00192` — All X Spot Instance Requests
- `L-ED8A7771` — Concurrent operations per Client VPN endpoint
- `L-F7808C92` — Running On-Demand HPC instances

## ec2-ipam

- `L-50203861` — Max IPv6 Contig Blocks
- `L-67900804` — Max IPv6 Contig Block Size
- `L-9661390E` — Max IPv4 Contig Block Size
- `L-E9C7F47C` — Max IPv4 Contig Blocks

## ecr

- `L-0A556EFC` — Basic image scans per 24 hours
- `L-1165B4AE` — Minimum layer part size
- `L-16E70933` — Rate of BatchGetImage requests
- `L-343F3D94` — Maximum layer part size
- `L-44194860` — Rate of CompleteLayerUpload requests
- `L-55A41110` — Rate of GetAuthorizationToken requests
- `L-8BE1781E` — Rules per lifecycle policy
- `L-95B28F8D` — Rate of InitiateLayerUpload requests
- `L-9C9D5A08` — Tags per image
- `L-A1670B10` — Rate of UploadLayerPart requests
- `L-A60A366D` — Rate of GetDownloadUrlForLayer requests
- `L-A71EAF5A` — Maximum layer size
- `L-AD52DFB2` — Rate of PutImage requests
- `L-B9173138` — Rate of BatchCheckLayerAvailability requests
- `L-C0B33BA1` — Lifecycle policy length
- `L-CB63E564` — Rate of image scans
- `L-EF8F6F4E` — Layer parts

## ecs

- `L-0314F8C9` — Rate of tasks launched by a service on AWS Fargate
- `L-152B9E01` — Sustained rate of task definition deletion actions (or bucket refill rate)
- `L-1E6DEB89` — Sustained rate of task definition modify actions (or bucket refill rate)
- `L-22AE4B75` — Burst rate of service read actions (or bucket maximum capacity)
- `L-281CBA4C` — Burst rate of cluster resource read actions (or bucket maximum capacity)
- `L-2AB0A1F7` — Subnets per awsvpcConfiguration
- `L-321A0372` — Sustained rate of service read actions (or bucket refill rate)
- `L-35D944A8` — Burst rate of cluster read actions (or bucket maximum capacity)
- `L-3B4FAC68` — Burst rate of cluster resource modify actions (or bucket maximum capacity)
- `L-3CA4FC4A` — Burst rate of setting read actions (or bucket maximum capacity)
- `L-3E3D55FE` — Burst rate of capacity provider modify actions (or bucket maximum capacity)
- `L-40D1D4C5` — Sustained rate of setting modify actions (or bucket refill rate)
- `L-424FFC53` — Burst rate of cluster service resource read actions (or bucket maximum capacity)
- `L-42E25F2A` — Sustained rate of capacity provider read actions (or bucket refill rate)
- `L-43D4E76A` — Sustained rate of cluster read actions (or bucket refill rate)
- `L-5046A93A` — Containers per task definition
- `L-538D7426` — Sustained rate of task definition read actions (or bucket refill rate)
- `L-553993D4` — Sustained rate of agent modify actions (or bucket refill rate)
- `L-5A5FEADE` — Burst rate of capacity provider read actions (or bucket maximum capacity)
- `L-62DC78F9` — Burst rate of cluster modify actions (or bucket maximum capacity)
- `L-64FE0575` — Sustained rate of cluster service resource read actions (or bucket refill rate)
- `L-660A3A36` — Burst rate of task protection actions (or bucket maximum capacity)
- `L-678F155F` — Burst rate of tag modify actions (or bucket maximum capacity)
- `L-6FA51D7A` — Task definition size
- `L-7BCA4F94` — ECS Exec sessions
- `L-80627E8A` — Sustained rate of cluster resource read actions (or bucket refill rate)
- `L-886BDC21` — Burst rate of agent modify actions (or bucket maximum capacity)
- `L-8C118AA8` — Tasks launched per run-task
- `L-8F66404D` — Sustained rate of tag modify actions (or bucket refill rate)
- `L-924E3D47` — Burst rate of task definition read actions (or bucket maximum capacity)
- `L-9383BF97` — Burst rate of task definition deletion actions (or bucket maximum capacity)
- `L-9440138C` — Sustained rate of tag read actions (or bucket refill rate)
- `L-9B84EC66` — Tags per resource
- `L-A04BC52C` — Burst rate of task protection actions (or bucket maximum capacity)
- `L-A2AA9478` — Burst rate of service deployment read actions (or bucket maximum capacity)
- `L-A2DBEAC1` — Sustained rate of service deployment read actions (or bucket refill rate)
- `L-A8AC1C0F` — Sustained rate of task protection actions (or bucket refill rate)
- `L-A9E5EB0F` — Sustained rate of capacity provider modify actions (or bucket refill rate)
- `L-AA0D4951` — Burst rate of service modify actions (or bucket maximum capacity)
- `L-B4EF2B3D` — Burst rate of tag read actions (or bucket maximum capacity)
- `L-C26103FB` — Sustained rate of task protection actions (or bucket refill rate)
- `L-C3AEE9D2` — Sustained rate of cluster resource modify actions (or bucket refill rate)
- `L-C5297B3A` — Sustained rate of service modify actions (or bucket refill rate)
- `L-CA95243C` — Sustained rate of setting read actions (or bucket refill rate)
- `L-CDF9F16B` — Burst rate of task definition modify actions (or bucket maximum capacity)
- `L-D3FB61D9` — Rate of tasks launched by a service on an Amazon EC2 or External instance
- `L-D57338CD` — Security groups per awsvpcConfiguration
- `L-D5AA0F33` — Sustained rate of cluster modify actions (or bucket refill rate)
- `L-D95BCB5D` — Burst rate of setting modify actions (or bucket maximum capacity)
- `L-DD98B2F8` — Container instances per start-task

## elasticache

- `L-75A7B5A4` — Serverless snapshots per day per cache
- `L-8C334AD1` — Nodes per cluster (Memcached)
- `L-943F0F1C` — Users per User Group
- `L-A87EE522` — Subnets per subnet group
- `L-AF354865` — Nodes per cluster (cluster mode enabled)
- `L-DFE45DF3` — Nodes per Region

## elasticbeanstalk

- `L-9838E43F` — Configuration templates

## elasticfilesystem

- `L-06519EB8` — Throughput per NFS client
- `L-1E30FF38` — Minimum wait time between Provisioned Throughput decreases
- `L-207AE8E0` — File system name length
- `L-29770CF9` — Tags
- `L-336A920F` — Rate of file system operations
- `L-48B15094` — Open files per NFS client
- `L-509A1582` — EFS file locks
- `L-6D380DD0` — Mount targets per Availability Zone
- `L-7391004C` — Mount targets per VPC
- `L-7FEABCD7` — File size
- `L-A139E5A7` — File hard links
- `L-B34D07B4` — Maximum read IOPS per file system with Elastic throughput
- `L-B8B14E21` — File system symbolic link (symlink) length
- `L-BFB6FB19` — Provisioned throughput
- `L-C8C0D2A0` — Locks across unique file/process pairs
- `L-CDCE244F` — Bursting throughput
- `L-D6548EE7` — Minimum wait time between Throughput mode changes
- `L-F3C5D9EF` — Directory depth
- `L-FA0AAA42` — Active users per NFS client

## elasticloadbalancing

- `L-057ECE54` — Target Groups per Action per Application Load Balancer
- `L-1A491844` — Listeners per Classic Load Balancer
- `L-23568085` — Network Load Balancer ENIs per VPC
- `L-8A66D0E6` — Reserved Application Load Balancer Capacity Units (LCU) per Region
- `L-A012D4E8` — Condition Wildcards per Rule
- `L-CE3125E5` — Registered Instances per Classic Load Balancer
- `L-EBC0C08B` — Condition Values per Rule
- `L-F31E307C` — CA certificates subject size per trust store

## elasticmapreduce

- `L-0224B14B` — Replenishment rate of AddInstanceGroups calls
- `L-032DEEF2` — Write-ahead logs (EMR WAL)
- `L-03AED1B3` — Replenishment rate of SetKeepJobFlowAliveWhenNoSteps calls
- `L-0E64D90C` — The maximum number of AddInstanceFleet API requests that you can make per second.
- `L-123EDE00` — Replenishment rate of GetClusterSessionCredentials calls
- `L-154D9FF8` — Replenishment rate of PutManagedScalingPolicy calls
- `L-160E516B` — The maximum number of ListSecurityConfigurations API requests that you can make per second.
- `L-16E4E927` — Replenishment rate of CreateSecurityConfiguration calls
- `L-1A0534D7` — Replenishment rate of ListSupportedInstanceTypes calls
- `L-2266B3CF` — The maximum number of ListInstanceGroups API requests that you can make per second.
- `L-2268EC50` — The maximum number of SetVisibileToAllUsers API requests that you can make per second.
- `L-2625B75B` — The maximum number of TerminateJobFlows API requests that you can make per second.
- `L-27ABC861` — The maximum number of ListReleaseLabels API requests that you can make per second.
- `L-27AD4F43` — The maximum number of DescribeSecurityConfiguration API requests that you can make per second.
- `L-283CCA2A` — The maximum number of API requests that you can make per second.
- `L-2C4B0A7F` — The maximum number of ListClusters API requests that you can make per second.
- `L-361D364D` — The maximum number of RemoveAutoScalingPolicy API requests that you can make per second.
- `L-3A2AEB6B` — Replenishment rate of RemoveAutoTerminationPolicy calls
- `L-3AD9CD3B` — Replenishment rate of AddInstanceFleet calls
- `L-3BF7624C` — Replenishment rate of PutAutoTerminationPolicy calls
- `L-40A3F1BE` — Replenishment rate of AddJobFlowSteps calls
- `L-41AA02AE` — The maximum number of ListInstances API requests that you can make per second.
- `L-41EE964A` — Replenishment rate of SetVisibleToAllUsers calls
- `L-432FAB44` — The maximum rate at which your bucket replenishes for all EMR operations.
- `L-49AA2AC0` — The maximum number of CreateSecurityConfiguration API requests that you can make per second.
- `L-49D80F39` — The maximum number of PutBlockPublicAccessConfiguration API requests that you can make per second.
- `L-4C313B42` — The maximum number of GetClusterSessionCredentials API requests that you can make per second.
- `L-4D731391` — Replenishment rate of TerminateJobFlows calls
- `L-5E87FF33` — The maximum number of ModifyInstanceFleet API requests that you can make per second.
- `L-600E341C` — The maximum number of GetBlockPublicAccessConfiguration API requests that you can make per second.
- `L-62231AC0` — Replenishment rate of RunJobFlow calls
- `L-67E5FE4A` — Replenishment rate of RemoveTags calls
- `L-68268EEB` — Replenishment rate of DescribeJobFlows calls
- `L-68E6373A` — The maximum number of RemoveAutoTerminationPolicy API requests that you can make per second.
- `L-72BCD5B1` — Replenishment rate of DescribeStep calls
- `L-73E44B2E` — Replenishment rate of ModifyCluster calls
- `L-76CEF085` — Replenishment rate of ListInstances calls
- `L-7D1BF903` — The maximum number of ListSteps API requests that you can make per second.
- `L-7E42A979` — The maximum number of AddJobFlowSteps API requests that you can make per second.
- `L-8027FD2D` — Replenishment rate of SetTerminationProtection calls
- `L-8029315A` — Replenishment rate of DescribeSecurityConfiguration calls
- `L-815103CB` — The maximum number of CancelSteps API requests that you can make per second.
- `L-81AF5123` — The maximum number of DescribeCluster API requests that you can make per second.
- `L-8273B16C` — The maximum number of ListSupportedInstanceTypes API requests that you can make per second.
- `L-84D58688` — Replenishment rate of ListInstanceGroups calls
- `L-85BA8360` — The maximum number of ListInstanceFleets API requests that you can make per second.
- `L-87EDCC64` — Replenishment rate of ModifyInstanceGroups calls
- `L-888B48A6` — The maximum number of PutAutoScalingPolicy API requests that you can make per second.
- `L-8AF88BF0` — Replenishment rate of ListSteps calls
- `L-94B63BE5` — The maximum number of GetAutoTerminationPolicy API requests that you can make per second.
- `L-9547F71F` — The maximum number of AddTags API requests that you can make per second.
- `L-985D82D4` — Replenishment rate of PutAutoScalingPolicy calls
- `L-996E162C` — Replenishment rate of GetAutoTerminationPolicy calls
- `L-9CCE25C7` — Replenishment rate of AddTags calls
- `L-9EFF5880` — Replenishment rate of ModifyInstanceFleet calls
- `L-9F63B487` — The maximum number of DescribeJobFlows API requests that you can make per second.
- `L-A21DE5E2` — The maximum number of RunJobFlow API requests that you can make per second.
- `L-A3790607` — The maximum number of PutManagedScalingPolicy API requests that you can make per second.
- `L-A3F85680` — The maximum number of ModifyInstanceGroups API requests that you can make per second.
- `L-A552C9A0` — The maximum number of ModifyCluster API requests that you can make per second.
- `L-A90C264E` — Replenishment rate of CancelSteps calls
- `L-AE4BC073` — The maximum number of SetKeepJobFlowAliveWhenNoSteps API requests that you can make per second.
- `L-B0BD2695` — EMR WAL workspaces
- `L-B810434D` — The maximum number of DescribeStep API requests that you can make per second.
- `L-BC4C3BE9` — Replenishment rate of SetKeepJobFlowAliveWhenNoSteps calls
- `L-BF4AD168` — The maximum number of ListBootstrapActions API requests that you can make per second.
- `L-C00B9F83` — The maximum number of RemoveTags API requests that you can make per second.
- `L-C0B235E1` — Replenishment rate of ListInstanceFleets calls
- `L-C7C7D520` — The maximum number of GetManagedScalingPolicy API requests that you can make per second.
- `L-CCF40647` — Replenishment rate of ListBootstrapActions calls
- `L-D145AF1C` — Replenishment rate of ListSecurityConfigurations calls
- `L-D74118B4` — Replenishment rate of DescribeCluster calls
- `L-D79F47D7` — The maximum number of RemoveManagedScalingPolicy API requests that you can make per second.
- `L-E5202B33` — The maximum number of AddInstanceGroups API requests that you can make per second.
- `L-E594D186` — Replenishment rate of PutBlockPublicAccessConfiguration calls
- `L-EA1CF51E` — Replenishment rate of GetManagedScalingPolicy calls
- `L-EB8F427D` — Replenishment rate of DeleteSecurityConfiguration calls
- `L-ECF78C67` — Replenishment rate of ListClusters calls
- `L-F06A869F` — The maximum number of SetTerminationProtection API requests that you can make per second.
- `L-F0B1A0AC` — The maximum number of DeleteSecurityConfiguration API requests that you can make per second.
- `L-F26C371C` — Replenishment rate of ListReleaseLabels calls
- `L-F285819B` — The maximum number of PutAutoTerminationPolicy API requests that you can make per second.
- `L-F5591F89` — Replenishment rate of GetBlockPublicAccessConfiguration calls
- `L-F902E21E` — Replenishment rate of RemoveAutoScalingPolicy calls

## emr-containers

- `L-049C5440` — Throttle burst quota for all EMR on EKS API requests
- `L-0E144DD3` — CreateManagedEndpoint API throttle rate quota
- `L-10C68888` — ListSecurityConfigurations API throttle burst quota
- `L-153AD8B0` — CreateVirtualCluster API throttle burst quota
- `L-23BD7F93` — DescribeJobTemplate API throttle burst quota
- `L-357C187E` — ListSecurityConfigurations API throttle rate quota
- `L-3A14F748` — CreateSecurityConfiguration API throttle rate quota
- `L-3FB59837` — StartJobRun API throttle rate quota
- `L-3FBDB52A` — ListJobTemplates API throttle rate quota
- `L-417184CD` — DescribeJobTemplate API throttle rate quota
- `L-44D0A65F` — DescribeManagedEndpoint API throttle burst quota
- `L-478B4EF8` — DeleteJobTemplate API throttle burst quota
- `L-565434BF` — ListJobRuns API throttle rate quota
- `L-62FC3F88` — ListManagedEndpoints API throttle rate quota
- `L-64915D20` — CancelJobRun API throttle rate quota
- `L-6DDC2BC3` — DescribeSecurityConfiguration API throttle burst quota
- `L-752AC3ED` — CancelJobRun API throttle burst quota
- `L-75EC5049` — DescribeVirtualCluster API throttle rate quota
- `L-7A243F80` — StartJobRun API throttle burst quota
- `L-7AA0FF83` — CreateManagedEndpoint API throttle burst quota
- `L-7BA9C81C` — DeleteJobTemplate API throttle rate quota
- `L-7E8E6AC0` — DeleteManagedEndpoint API throttle burst quota
- `L-87C5AE74` — ListJobRuns API throttle burst quota
- `L-8C2B4C1B` — ListManagedEndpoints API throttle burst quota
- `L-8D61D4A3` — GetManagedEndpointSessionCredentials API throttle rate quota
- `L-9DB0BF8E` — CreateSecurityConfiguration API throttle burst quota
- `L-A8B95F18` — DescribeSecurityConfiguration API throttle rate quota
- `L-A95AA2BC` — DeleteVirtualCluster API throttle rate quota
- `L-BA261527` — DescribeManagedEndpoint API throttle rate quota
- `L-C1362F1E` — DeleteVirtualCluster API throttle burst quota
- `L-C321754F` — DescribeJobRun API throttle rate quota
- `L-C3B42DAF` — DeleteManagedEndpoint API throttle rate quota
- `L-C3E21E6D` — Throttle rate quota for all EMR on EKS API requests
- `L-C54DE4F3` — DescribeJobRun API throttle burst quota
- `L-D039DBDA` — GetManagedEndpointSessionCredentials API throttle burst quota
- `L-D7BA7727` — ListVirtualClusters API throttle rate quota
- `L-DB01B55A` — CreateJobTemplate API throttle rate quota
- `L-E68AE712` — DescribeVirtualCluster API throttle burst quota
- `L-EF7EF009` — ListJobTemplates API throttle burst quota
- `L-F2A91621` — CreateJobTemplate API throttle burst quota
- `L-F61EA729` — ListVirtualClusters API throttle burst quota
- `L-F8831434` — CreateVirtualCluster API throttle rate quota

## emr-serverless

- `L-D05C8A75` — Max concurrent vCPUs per account

## entityresolution

- `L-1E6F8596` — Rate of GetMatchId API requests
- `L-6CABAEA7` — Records per machine learning-based matching workflow
- `L-6FC653B7` — Records per rule-based ID mapping workflow
- `L-973E8499` — Records per provider ID mapping workflow
- `L-B2BB98E6` — Rate of GenerateMatchId API requests
- `L-C5007B10` — Records per rule-based matching workflow
- `L-D806D7C1` — Records per provider service-based matching workflow

## es

- `L-1F053E6F` — Warm instances per domain
- `L-6408ABDE` — Instances per domain
- `L-AE676A72` — Dedicated master instances per domain
- `L-E9BC8C95` — Instances per domain (T2 instance type)

## events

- `L-3C47459F` — Throttle limit in transactions per second for control plane APIs only, API name must be specified in the request (do not use for PutEvents)
- `L-5425B7E9` — DeleteEndpoint throttle limit in transactions per second
- `L-5540C5E3` — Invocations throttle limit in transactions per second
- `L-595D6D42` — Connections
- `L-664C5505` — Event pattern size
- `L-755FD01C` — Rate of invocations per API destination
- `L-9B653E91` — PutEvents throttle limit in transactions per second
- `L-A8AFA624` — UpdateEndpoint throttle limit in transactions per second
- `L-CB72B930` — CreateEndpoint throttle limit in transactions per second
- `L-EAC9A2AC` — Endpoints
- `L-FB1C3A6D` — Api destinations
- `L-FC354966` — Event bus policy size

## evidently

- `L-2992F357` — Rate of PostProjectEvents requests
- `L-4F58F1DC` — Rate of EvaluateFeature requests
- `L-63083ACB` — Total launches per project
- `L-738C873C` — Running experiments per project
- `L-DA4D659A` — Running launches per project
- `L-E477E349` — Total experiments per project
- `L-E6200B63` — Features per project
- `L-ECD3E408` — Rate of BatchEvaluateFeature requests

## fargate

- `L-3032A538` — Fargate On-Demand vCPU resource count
- `L-36FBB829` — Fargate Spot vCPU resource count
- `L-551A4E9D` — Fargate On-Demand Sustained Launch Rate
- `L-6BAD92DD` — Fargate On-Demand Burst Launch Rate
- `L-F6E37E82` — Fargate Spot Burst Launch Rate
- `L-FAA52651` — Fargate Spot Sustained Launch Rate

## finspace

- `L-05F8CB95` — Managed kdb concurrent changeset ingestions
- `L-0FC2034E` — Managed kdb volume write mounts
- `L-8798EB61` — Concurrent dataview version processing
- `L-CD999E75` — Managed kdb volume read mounts

## firehose

- `L-040D05FF` — Rate of CreateDeliveryStream requests
- `L-09E8B729` — Rate of StopDeliveryStreamEncryption requests
- `L-0D32C2BC` — Rate of StartDeliveryStreamEncryption requests
- `L-17D4EADE` — Rate of records
- `L-23F03908` — Dynamic Partitions
- `L-36A7E04C` — Rate of ListTagsForDeliveryStream requests
- `L-3A800C3A` — Rate of DeleteDeliveryStream requests
- `L-47C73A38` — Rate of UntagDeliveryStream requests
- `L-61E2CA1D` — Rate of DescribeDeliveryStream requests
- `L-7681C790` — Rate of Put requests
- `L-937C879B` — Rate of data
- `L-CC1FDDAA` — Rate of UpdateDestination requests
- `L-ED7DA7FC` — Rate of TagDeliveryStream requests
- `L-FDED3C5B` — Rate of ListDeliveryStream requests

## fis

- `L-2FF3254A` — Experiment templates
- `L-6C1E4427` — Experiment duration in hours
- `L-9D601129` — Completed experiment data retention in days
- `L-A5537B7C` — Maximum number of Route Tables in aws:network:route-table-disrupt-cross-region-connectivity
- `L-A7622DAA` — Action duration in hours
- `L-B0012750` — Target ReplicationGroups for aws:elasticache:interrupt-cluster-az-power - Deprecation Planned
- `L-C7DC78F0` — Maximum number of Managed Prefix Lists in aws:network:route-table-disrupt-cross-region-connectivity
- `L-C9A268F2` — Maximum number of routes in aws:network:route-table-disrupt-cross-region-connectivity
- `L-F5FCA485` — Active experiments

## fms

- `L-25F99602` — Amazon VPC instances in scope of a common security group policy
- `L-3DCEAE01` — Custom managed application lists for rules that allow all traffic
- `L-49265FF2` — Custom managed application lists in any content audit security group policy setting
- `L-4E3D82C8` — Custom managed protocol lists in any content audit security group policy setting
- `L-BCA8AD34` — VPCs that a single Network Firewall policy can automatically remediate

## forecast

- `L-3F8C5D53` — Maximum number of files in your Amazon S3 bucket
- `L-4A218FD9` — Maximum number of time series per predictor
- `L-4F7B6EC8` — Maximum number of backtest windows
- `L-60743B41` — Maximum number of tags you can add to a resource
- `L-618F5043` — Maximum number of rows in a dataset
- `L-690B4DB2` — Maximum cumulative size of all files in your Amazon S3 bucket
- `L-710D1193` — Maximum parallel running Stop jobs per resource type
- `L-B77118AF` — Maximum parallel running QueryForecast API tasks
- `L-B8197A69` — Maximum time for which a forecast can be queried on console or QueryForecast API
- `L-BDD6E332` — Maximum parallel running CreatePredictor tasks using AutoML

## gamelift

- `L-11948650` — Build capacity
- `L-24BE0A39` — Player session timeout
- `L-67477D57` — Players per matchmaking ticket
- `L-8EBC4E87` — Strings per string list matchmaking player attribute
- `L-A8C1B434` — Key-value pairs per string to double map matchmaking player attribute
- `L-BFEEB817` — Managed EC2 fleet EBS volume
- `L-CCBBB4DA` — Player attributes per matchmaking player
- `L-E8D8BD94` — Game session log file size
- `L-EC03D793` — Player sessions per game session
- `L-ED58E8F8` — Script capacity

## gameliftstreams

- `L-0597376F` — Files per application
- `L-261849DF` — Gen5n GPUs, eu-central-1
- `L-32B09C2E` — Gen4n GPUs, eu-west-1
- `L-3E4E3BE1` — Application size (GiB)
- `L-4A4CFDD3` — Gen4n GPUs, us-east-1
- `L-4FFB0D13` — Gen5n GPUs, us-east-1
- `L-76A9DAF1` — Gen4n GPUs, us-east-2
- `L-8BB014BB` — Gen4n GPUs, eu-central-1
- `L-8D495FC3` — Gen5n GPUs, us-west-2
- `L-954DDDF7` — Gen4n GPUs, us-west-2
- `L-9CFB776D` — Gen5n GPUs, ap-northeast-1
- `L-9DE2CD9C` — Gen5n GPUs, eu-west-1
- `L-C8CFA70A` — Gen4n GPUs, ap-northeast-1
- `L-E29DEEE7` — Gen5n GPUs, us-east-2

## geo

- `L-004FBC04` — Rate of ListMaps API requests
- `L-0316544D` — Rate of CreateTracker API requests
- `L-05EFD12D` — Rate of GetMapStyleDescriptor API requests
- `L-0A4EAAD0` — Rate of CreatePlaceIndex API requests
- `L-0C20A2F2` — Rate of CreateKey API requests
- `L-0E174A76` — Rate of CalculateRouteMatrix API requests
- `L-123EEE95` — Rate of UpdateMap API requests
- `L-16C77FC0` — Rate of BatchUpdateDevicePosition API requests
- `L-18D30F94` — Rate of geo-routes:SnapToRoads API requests
- `L-1D4EB556` — Rate of BatchGetDevicePosition API requests
- `L-201B3D58` — Rate of SearchPlaceIndexForPosition API requests
- `L-20F1367A` — Rate of SearchPlaceIndexForText API requests
- `L-24CBFF24` — Rate of DeleteTracker API requests
- `L-25528367` — Rate of GetMapGlyphs API requests
- `L-2A3A5399` — Rate of ListGeofences API requests
- `L-2CA6C84D` — Rate of TagResource API requests
- `L-32299313` — Rate of DisassociateTrackerConsumer API requests
- `L-3B5E6DAC` — Rate of ListTrackerConsumers API requests
- `L-3B6F7C26` — Rate of DescribeMap API requests
- `L-42524A80` — Rate of ListGeofenceCollections API requests
- `L-44B9F1A6` — Rate of CalculateRoute API requests
- `L-46173623` — Rate of ForecastGeofenceEvents API requests
- `L-4B4C2391` — Rate of DescribeKey API requests
- `L-4BA89359` — Rate of DescribeTracker API requests
- `L-4D54A4EF` — Rate of UpdateGeofenceCollection API requests
- `L-4D8FB6E2` — Rate of BatchPutGeofence API requests
- `L-55FCDA52` — Rate of GetDevicePosition API requests
- `L-5C766737` — Rate of UpdateTracker API requests
- `L-5FC982A3` — Rate of VerifyDevicePosition API requests
- `L-664067C5` — Rate of AssociateTrackerConsumer API requests
- `L-66B4C7B5` — Rate of DeleteMap API requests
- `L-68C0FF09` — Rate of DescribeGeofenceCollection API requests
- `L-6FC30467` — Rate of geo-places:GetPlace API requests
- `L-772C0B77` — Rate of DescribePlaceIndex API requests
- `L-7746796E` — Rate of geo-places:SearchText API requests
- `L-779B9CA5` — Rate of DeleteGeofenceCollection API requests
- `L-7FB5719A` — Rate of GetMapTile API requests
- `L-80BBD6B4` — Rate of geo-places:Geocode API requests
- `L-8524BC5F` — Rate of geo-maps:GetStaticMap API requests
- `L-85DB3370` — Rate of UpdateRouteCalculator API requests
- `L-8652D4FC` — Rate of geo-routes:CalculateRoutes API requests
- `L-8A769EC2` — Rate of CreateMap API requests
- `L-8C4D918C` — Rate of PutGeofence API requests
- `L-8EACF4A4` — Rate of geo-routes:CalculateRouteMatrix API requests
- `L-9181BDFA` — Rate of geo-routes:CalculateIsolines API requests
- `L-93F5D44A` — Rate of BatchDeleteGeofence API requests
- `L-9A0A3162` — Rate of BatchEvaluateGeofences API requests
- `L-9A60EA62` — Rate of GetDevicePositionHistory API requests
- `L-A8DEDDAD` — Rate of geo-places:Suggest API requests
- `L-AE2D8C2E` — Rate of UpdatePlaceIndex API requests
- `L-AF53BB1C` — Rate of CreateRouteCalculator API requests
- `L-B26E5E95` — Rate of ListDevicePositions API requests
- `L-BE8C4A7E` — Rate of ListKeys API requests
- `L-C236DAD6` — Rate of UntagResource API requests
- `L-C2D15753` — Rate of GetMapSprites API requests
- `L-CA16DE37` — Rate of BatchDeleteDevicePositionHistory API requests
- `L-CB597B2B` — Rate of geo-maps:GetTile API requests
- `L-CF1B7B95` — Rate of GetPlace API requests
- `L-D012773A` — Rate of DeletePlaceIndex API requests
- `L-D3A51B68` — Rate of ListRouteCalculators API requests
- `L-D877D921` — Rate of geo-places:SearchNearby API requests
- `L-DFE2C362` — Rate of CreateGeofenceCollection API requests
- `L-E2610803` — Rate of geo-places:ReverseGeocode API requests
- `L-E2B35742` — Rate of GetGeofence API requests
- `L-E2D2B83E` — Rate of geo-routes:OptimizeWaypoints API requests
- `L-E31E6201` — Rate of UpdateKey API requests
- `L-E3E8B4BC` — Rate of ListPlaceIndexes API requests
- `L-E976E608` — Rate of ListTagsForResource API requests
- `L-EA3098B7` — Rate of DescribeRouteCalculator API requests
- `L-EC3CCC13` — Rate of SearchPlaceIndexForSuggestions API requests
- `L-EF11EFBE` — Rate of DeleteRouteCalculator API requests
- `L-EF9582AD` — Rate of geo-places:Autocomplete API requests
- `L-F0E58BD7` — Rate of ListTrackers API requests
- `L-FF8C0CDC` — Rate of DeleteKey API requests

## glacier

- `L-0D9D2530` — Number of random restore requests.
- `L-153F5D45` — Number of vault tags.
- `L-4BF4C362` — Multipart parts size.
- `L-982DEA76` — Number of multipart parts.
- `L-E0D19AD1` — Archive size.
- `L-E96017CA` — Archive size in GB.
- `L-F127DF29` — Provisioned capacity units

## glue

- `L-08F3B322` — Max task DPUs per account
- `L-096DBB95` — Max spare compute capacity consumed in data processing units (DPUs) per account.
- `L-2E9FB93F` — Max concurrent observations generation runs per account
- `L-958728D1` — Maximum number of in-flight completion requests allowed per account
- `L-B78896B9` — Label file size

## grafana

- `L-0F096599` — Rate of UpdateWorkspace requests
- `L-482DE601` — Rate of DisassociateLicense requests
- `L-5420120D` — Rate of UpdatePermissions requests
- `L-6134480C` — Rate of CreateWorkspace requests
- `L-6A33FFDD` — Rate of UpdateWorkspaceAuthentication requests
- `L-A947D66C` — Rate of AssociateLicense requests
- `L-B3CBC037` — Rate of DescribeWorkspaceAuthentication requests
- `L-C1661D81` — Rate of DescribeWorkspace requests
- `L-DE04A994` — Rate of DeleteWorkspace requests
- `L-EF9C1A59` — Rate of ListPermissions requests
- `L-F61AFA49` — Rate of ListWorkspaces requests

## greengrass

- `L-1F85CE8B` — Total component artifact size
- `L-4424F8F0` — Component recipe size
- `L-7A577824` — Rate of API requests
- `L-7B8C20A0` — Rate of CreateComponentVersion requests
- `L-99B77DDC` — Thing deployment document size (without large configuration support)
- `L-B4267AEE` — Deployment document size (with large configuration support)
- `L-B905B13E` — Rate of CreateDeployment requests (V1)
- `L-EF192347` — Thing group deployment document size (without large configuration support)

## groundstation

- `L-09DEC198` — Contact Lead Time Maximum
- `L-BD84767C` — Enabled Ephemerides limit
- `L-CCFDE387` — Maximum Contact Duration
- `L-DE376FC5` — Ephemeris Validation limit
- `L-DF7B6DEC` — Scheduled Contacts Limit
- `L-FED20749` — Scheduled Minutes Limit

## guardduty

- `L-373487E5` — Finding retention period
- `L-8B0D7135` — Member accounts through AWS Organizations
- `L-F51A2830` — Member accounts by invitation
