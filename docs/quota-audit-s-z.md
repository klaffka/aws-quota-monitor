# S–Z Quota Audit

Generated from `data/service-quotas-20251102T133323Z.json`; unique service/quota pairs not represented by an existing check code. Snapshot date: 2026-09-10.

Direct paginated resource inventories are implemented in the collector. Rate, capacity, storage, content, runtime, and parent-detail limits remain explicitly unsupported. REVIEW rows were checked against local Botocore models; safe direct inventories were added where available.

## `s3` (13 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-1923B91D` | S3 Glacier: Retrieval request rate per second. | UNSUPPORTED: API rate/throttle quota |
| `L-1A9B467F` | Replication Destinations | UNSUPPORTED: no direct persistent resource inventory |
| `L-2431D3AF` | Multi-Region Access Point Regions | UNSUPPORTED: no direct persistent resource inventory |
| `L-2A85EAC1` | Maximum part size | UNSUPPORTED: size/throughput/content quota |
| `L-349AD9CA` | Replication transfer rate | UNSUPPORTED: API rate/throttle quota |
| `L-6AF88990` | Object tags | UNSUPPORTED: no direct persistent resource inventory |
| `L-748707F3` | Bucket policy | UNSUPPORTED: no direct persistent resource inventory |
| `L-89BABEE8` | Object size | UNSUPPORTED: size/throughput/content quota |
| `L-9CD4D118` | Object size (Console upload) | UNSUPPORTED: size/throughput/content quota |
| `L-BB883139` | S3 Glacier: Number of random restore requests. | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-CD1053C4` | Minimum part size | UNSUPPORTED: size/throughput/content quota |
| `L-DEBF781C` | Parts | UNSUPPORTED: no direct persistent resource inventory |
| `L-DEDCCF9D` | S3 Glacier: Provisioned capacity units | UNSUPPORTED: capacity or runtime quota |

## `sagemaker` (1537 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-001567EF` | ml.r8g.medium for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-001EDCEF` | ml.g5.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-005C1A21` | RSessionGateway Apps running on ml.r5.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-008FE00D` | ml.c6i.large for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-00C0E80E` | ml.m6id.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-00C91CB5` | Number of instances across all training jobs | UNSUPPORTED: capacity or runtime quota |
| `L-00DAC655` | RSessionGateway Apps running on ml.m5d.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-0100B823` | ml.g5.48xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0132CA88` | Studio KernelGateway Apps running on ml.m5.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-01341C09` | Rate of StopNotebookInstance requests | UNSUPPORTED: API rate/throttle quota |
| `L-01589929` | ml.c7i.48xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-017831D5` | ml.c6i.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-018036DB` | ml.c6gd.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-019DC79D` | Studio KernelGateway Apps running on ml.m5d.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-01E4E529` | ml.eia1.medium for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-02134873` | Studio CodeEditor Apps running on ml.m5d.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-02BF14DD` | ml.r7i.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0307F515` | ml.m5.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0309C694` | ml.m4.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-03304C28` | ml.g6.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-03767DF9` | ml.m5.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-037F309A` | Studio KernelGateway Apps running on ml.g5.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-03C8E8AF` | ml.r5.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-03E19172` | ml.g5.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-03FD2ADF` | ml.m6i.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-04421A63` | Studio JupyterLab Apps running on ml.m5d.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-047DF2B4` | Studio JupyterLab Apps running on ml.c7i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-048C491E` | ml.m5.16xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-04956A25` | ml.r8g.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0496610F` | ml.g4dn.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-04CD765C` | ml.c5n.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-04F55E28` | Studio CodeEditor Apps running on ml.c5.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-050981C0` | RSessionGateway Apps running on ml.g4dn.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-05282267` | ml.m8g.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0544E72F` | ml.r5d.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0549E35C` | ml.c6id.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-056831C6` | ml.c6i.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-05D004A9` | Studio CodeEditor Apps running on ml.g6.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-05D71277` | Longest run time for an AutoML job, from creation to termination | UNSUPPORTED: no direct persistent resource inventory |
| `L-06106111` | ml.m7i.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-064E954E` | ml.m7i.12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-065D610E` | ml.g5.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0665041B` | ml.r7i.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-06A1E8BB` | ml.r5.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-06AB0AAC` | ml.r7i.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-06DD0DBC` | ml.c6i.12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-06E121F0` | Rate of CreateStudioLifecycleConfig requests | UNSUPPORTED: API rate/throttle quota |
| `L-06EAD8FD` | Studio JupyterLab Apps running on ml.m7i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-0771FE64` | ml.r7i.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-079EEF64` | ml.m7i.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-07B51BA0` | ml.g6.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-07BEB181` | ml.g4dn.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-07D0651D` | Number of elastic inference accelerators across active endpoints | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-08553D92` | Studio CodeEditor Apps running on ml.r6id.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-08F097C3` | ml.m7i.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-08F1F3D8` | ml.m7i.48xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-08FEE190` | Studio CodeEditor Apps running on ml.r7i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-090C5671` | ml.c6i.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-09249843` | RSessionGateway Apps running on ml.m5.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-09A41608` | Studio CodeEditor Apps running on ml.p3.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-09B4A649` | ml.p4d.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-09C9B23C` | ml.c5.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-09D3DD58` | Studio KernelGateway Apps running on ml.g4dn.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-09D56C4F` | ml.p4d.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-09F79647` | ml.p4d.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0A241A0D` | Studio CodeEditor Apps running on ml.c5.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-0A29AACF` | ml.g6.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0A2EA525` | Rate of CreateWorkteam requests | UNSUPPORTED: API rate/throttle quota |
| `L-0A5EF986` | Studio CodeEditor Apps running on ml.c6i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-0A6678C9` | ml.m6i.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-0A6E4205` | ml.g5.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0A9C6950` | Studio CodeEditor Apps running on ml.m6i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-0AC766BA` | ml.m7i.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0AFBBD69` | Studio JupyterLab Apps running on ml.m6i.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-0AFC5B08` | Rate of DeleteEndpoint requests | UNSUPPORTED: API rate/throttle quota |
| `L-0B2C2B96` | Studio CodeEditor Apps running on ml.m6i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-0B434972` | ml.r7i.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0BE2F5A1` | ml.r7i.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0BEF44E8` | ml.m5.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0C0D9F82` | ml.c6i.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0C545830` | ml.m7i.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0CE343FE` | ml.t3.medium for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0D245982` | Studio CodeEditor Apps running on ml.c6id.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-0D323AED` | ml.g5.16xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0D57F08E` | ml.i3en.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0D58D77C` | ml.c5.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0DA2E7B0` | ml.g6e.48xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-0DADC663` | Studio KernelGateway Apps running on ml.p3.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-0DB30DD8` | Studio JupyterLab Apps running on ml.g4dn.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-0E2A8BBF` | Studio JupyterLab Apps running on ml.m5.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-0E846ECD` | Studio KernelGateway Apps running on ml.g4dn.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-0EA47E2A` | Studio CodeEditor Apps running on ml.g6.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-0F109211` | ml.r6i.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-0FCBFBBD` | RSessionGateway Apps running on ml.t3.large instance | UNSUPPORTED: capacity or runtime quota |
| `L-0FEC7BB1` | Studio CodeEditor Apps running on ml.g4dn.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-1122D5DF` | ml.c6i.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-11294128` | Maximum number of training jobs each hyper parameter tuning job can run in parallel at once | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-11624F40` | ml.c7i.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-11AFDCA2` | Studio JupyterLab Apps running on ml.m6id.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-11D02DB4` | Studio CodeEditor Apps running on ml.r5.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-1252146D` | ml.i3en.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-125B7142` | Studio JupyterLab Apps running on ml.g6.48xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-1271DF32` | RSessionGateway Apps running on ml.c5.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-12740493` | ml.g5.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-12798BAE` | Studio CodeEditor Apps running on ml.g5.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-127D4C65` | ml.g5.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-130E7B6B` | ml.m6i.large for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1356CD75` | Studio CodeEditor Apps running on ml.p3.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-135CF62D` | ml.g5.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-138F29A9` | Studio JupyterLab Apps running on ml.g4dn.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-14042B18` | Studio JupyterLab Apps running on ml.r6id.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-1410387A` | ml.t2.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-144A2794` | RSessionGateway Apps running on ml.g4dn.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-1474CE56` | ml.g6.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1476E09A` | Studio KernelGateway Apps running on ml.c5.large instance | UNSUPPORTED: capacity or runtime quota |
| `L-148FBB89` | ml.g6.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-150039CA` | Maximum number of Ground Truth labeling jobs | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-15047DF3` | ml.m6i.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1509B3BD` | Studio CodeEditor Apps running on ml.c6id.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-15461E7B` | Studio CodeEditor Apps running on ml.m6id.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-154D0022` | ml.r5.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-15BCD638` | ml.c5.12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-15BF0640` | Studio JupyterLab Apps running on ml.r7i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-15ECE899` | Studio JupyterLab Apps running on ml.r5.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-15F329FB` | ml.g4dn.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1619F5B7` | ml.g5.8xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1623D0BE` | ml.p3.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1630284B` | ml.m6gd.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-164A270E` | ml.c6i.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-16553FE9` | ml.c7i.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-1686EE8B` | ml.m5.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-16AF71F1` | ml.p5.48xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1743E120` | Rate of ListNotebookInstances requests | UNSUPPORTED: API rate/throttle quota |
| `L-1747114E` | Studio KernelGateway Apps running on ml.r5.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-176526F4` | ml.r6i.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-177AF1AD` | ml.g6e.48xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-177D4E91` | ml.r6gd.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-17A0905E` | ml.r5d.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-17CC37BB` | Studio CodeEditor Apps running on ml.r5.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-17CEAE74` | ml.c6i.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-180A6F2D` | ml.g4dn.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-183BFAB9` | Rate of CreateWorkforce requests | UNSUPPORTED: API rate/throttle quota |
| `L-186C8C43` | ml.inf2.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-18C64902` | Studio CodeEditor Apps running on ml.m5.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-1928E07B` | ml.g5.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-194981EA` | ml.c7i.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-195A207B` | ml.m5d.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-19734703` | Studio KernelGateway Apps running on ml.m5.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-199558F0` | ml.g4dn.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-19973BE2` | ml.g5.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-199FCA12` | Studio JupyterLab Apps running on ml.p3.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-19B6BAFC` | Studio JupyterLab Apps running on ml.g5.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-19BBECED` | ml.g6.48xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-19BC6A57` | Studio CodeEditor Apps running on ml.m6i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-19C2A697` | ml.inf2.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-19CFBA14` | ml.r6i.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-19E4BAD9` | ml.m7i.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-1A35F5CB` | ml.r8g.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1A647398` | Rate of UpdateMonitoringAlert requests | UNSUPPORTED: API rate/throttle quota |
| `L-1A8A7BA2` | Studio JupyterLab Apps running on ml.c6i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-1AE80ECF` | ml.g6e.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1AF0C909` | Rate of UpdateNotebookInstanceLifecycleConfig requests | UNSUPPORTED: API rate/throttle quota |
| `L-1B2B0D33` | ml.m6i.32xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1B353A48` | Studio CodeEditor Apps running on ml.c5.9xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-1B372F3F` | ml.r7i.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1B49FD35` | Studio JupyterLab Apps running on ml.g5.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-1B5DBA1F` | Rate of ListLabelingJobsForWorkteam requests | UNSUPPORTED: API rate/throttle quota |
| `L-1B60238B` | ml.c7i.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-1B687CD5` | ml.c5n.9xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1B7024B2` | ml.c6i.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1BF9151C` | ml.m4.10xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1C2E1B03` | ml.g4dn.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-1C84ABBF` | RSessionGateway Apps running on ml.r5.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-1CF85412` | Studio KernelGateway Apps running on ml.p3dn.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-1D84B9D2` | ml.m5.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1DA286AA` | ml.c4.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1DA9A185` | Studio KernelGateway Apps running on ml.m5.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-1DD0FB59` | ml.m5d.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-1DDB8D50` | ml.g6.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1DE24427` | ml.g6e.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1E2072C0` | ml.t3.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1E3225F6` | ml.g6e.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1E4582F6` | Studio JupyterLab Apps running on ml.m6i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-1EC048AB` | Studio CodeEditor Apps running on ml.r5.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-1EC4D7FD` | ml.c7i.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-1F122E71` | ml.r6i.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-1F4A5AAB` | ml.p3.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-1FF397C6` | ml.g6.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-203824E2` | ml.m7i.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-204097CE` | ml.m7i.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-20546400` | ml.r5.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-206CAD5E` | Rate of ListEndpointConfigs requests | UNSUPPORTED: API rate/throttle quota |
| `L-20700136` | ml.t2.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-20816B3A` | ml.r7i.16xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-20DF4E8E` | Studio CodeEditor Apps running on ml.c5.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-212B4A4E` | ml.r6i.32xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-213CD3BC` | ml.g4dn.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-214DADDD` | ml.c6i.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-21552510` | RSessionGateway Apps running on ml.c5.18xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-21962CDA` | RSessionGateway Apps running on ml.c5.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-21A1652A` | Rate of CreateTrainingJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-21A99C91` | ml.m8g.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-21DCDF63` | ml.m6id.32xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-21FC2F36` | ml.m7i.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-22BC3627` | Studio KernelGateway Apps running on ml.m5.large instance | UNSUPPORTED: capacity or runtime quota |
| `L-22E1BC00` | ml.r5d.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-23412DF7` | ml.g5.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-23426920` | ml.r7i.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-236AE59F` | ml.m5.large for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-239B242B` | ml.c5.18xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-23A89612` | Canvas Apps running on ml.m5.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-23D6147A` | Studio CodeEditor Apps running on ml.r6id.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-23E57EB1` | ml.g6e.48xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-23F5AC7E` | ml.inf1.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-23FC2F6E` | ml.m7i.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-23FF30BF` | ml.r5.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2441079A` | ml.c5.9xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2451F7E3` | ml.m7i.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-24520F3F` | ml.m5.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-246C5638` | ml.g4dn.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-24B0ADC0` | ml.m6i.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-24B12C23` | ml.m5d.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-24BF08D5` | ml.c7i.large for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-24E5A1B2` | ml.g5.12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2524EF35` | Studio KernelGateway Apps running on ml.r5.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-252AB1C1` | ml.c6i.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-254EBA2C` | Rate of ListModels requests | UNSUPPORTED: API rate/throttle quota |
| `L-2557FB75` | Studio CodeEditor Apps running on ml.p4d.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-25B13CE9` | ml.c7i.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-25EC3C78` | ml.r7i.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-260E95A6` | ml.r7i.48xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-26101D2F` | ml.r7i.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-266C4F52` | ml.c5n.18xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-26A7D02E` | Studio CodeEditor Apps running on ml.m5.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-26EB4EC7` | ml.m5d.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-2733D4D5` | Studio JupyterLab Apps running on ml.t3.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-2774E5C8` | ml.i3en.3xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-27768634` | ml.c4.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-2782D709` | ml.m6i.16xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-27CC6DE9` | Rate of UpdateWorkforce requests | UNSUPPORTED: API rate/throttle quota |
| `L-283CDA96` | ml.r5d.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-286C98BC` | ml.inf2.48xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-28CF4381` | ml.m6i.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-28F860BB` | ml.g5.24xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-28FEB563` | ml.g6.48xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2908B1E9` | ml.g4dn.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2930A179` | ml.g6e.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-29508C65` | ml.g5.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-29512C0F` | ml.g6e.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2952557B` | ml.c5n.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-29688C85` | ml.m5.large for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2972CC1F` | ml.c6i.large for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-297E9CE0` | Rate of CreateFlowDefinition requests | UNSUPPORTED: API rate/throttle quota |
| `L-299FAE98` | ml.r5.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-29B03627` | ml.m5.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-29C181D7` | ml.t2.medium for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-29FEA462` | Studio JupyterLab Apps running on ml.m6i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-2A6ACFF7` | ml.m5.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2A783E1C` | ml.r7gd.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2AD4A712` | ml.m7i.48xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-2AD5EFDD` | ml.g6e.48xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2B1E88AF` | ml.c6i.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2B2789AA` | RSessionGateway Apps running on ml.r5.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-2B2F8466` | ml.inf1.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-2B64B575` | ml.c7i.16xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2BAB231B` | ml.c4.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2BAB3767` | ml.c6i.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-2BE095E2` | ml.c5.9xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2BEDFA2E` | ml.r7i.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2BEE7665` | RSessionGateway Apps running on ml.m5.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-2BF1C629` | ml.m5d.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2C06E55A` | ml.g6.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2C080D31` | ml.m6i.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2C0E8383` | ml.g6e.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2C3AA41C` | Studio JupyterLab Apps running on ml.m7i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-2C505E76` | ml.r6id.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-2C68B58D` | Studio JupyterLab Apps running on ml.r6i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-2CA31BFA` | Studio JupyterLab Apps running on ml.m5.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-2CBC0A12` | Studio JupyterLab Apps running on ml.c6id.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-2CE978FC` | Maximum number instances allowed per SageMaker HyperPod cluster | UNSUPPORTED: capacity or runtime quota |
| `L-2D2AAC6C` | ml.m6g.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2D4C4A2D` | RSessionGateway Apps running on ml.m5d.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-2D6DEB3C` | ml.g5.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2D83F796` | ml.m6i.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-2D8CD70A` | ml.c5.18xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2DD73636` | ml.m5.large for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2E21A1FA` | ml.p3dn.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-2E243138` | ml.g6e.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2E2B5B49` | ml.g6e.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2ECAA15F` | ml.m4.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2F10D2D2` | ml.m6i.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2F1EB012` | ml.g4dn.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2F20345E` | ml.r7i.large for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2F737F8D` | ml.m5.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2F7823EE` | Studio CodeEditor Apps running on ml.c6i.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-2F9D520B` | ml.r5.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-2FA5A219` | Studio CodeEditor Apps running on ml.m6i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-2FFC6F34` | ml.r7gd.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-300538CF` | ml.r5.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-30ABD943` | RSessionGateway Apps running on ml.m5.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-30B99A16` | Studio JupyterLab Apps running on ml.m5d.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3118B7E1` | ml.g4dn.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-31522FA6` | ml.g4dn.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-31679D7C` | Studio CodeEditor Apps running on ml.c7i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-31F66640` | ml.r7i.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-320DF9E1` | ml.c7i.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3221855A` | ml.m6id.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-3245CAF1` | ml.r8g.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-326E6232` | ml.r7i.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-329751EB` | ml.m5.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-32F895F6` | Studio KernelGateway Apps running on ml.m5d.large instance | UNSUPPORTED: capacity or runtime quota |
| `L-3308CCC7` | Total number of instances allowed across SageMaker HyperPod clusters | UNSUPPORTED: capacity or runtime quota |
| `L-33471349` | Studio CodeEditor Apps running on ml.r5.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-334BD79D` | ml.m8g.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-334DC079` | ml.c4.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3358D120` | Studio JupyterLab Apps running on ml.m6id.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3360E714` | ml.r7i.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-339123BF` | ml.g5.48xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-33A961FD` | Longest run time for a training job | UNSUPPORTED: no direct persistent resource inventory |
| `L-3408A20D` | ml.g4dn.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3449BF8C` | Rate of DeleteTrainingJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-34594662` | ml.m5.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-34757F79` | Studio CodeEditor Apps running on ml.c5.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-34866D05` | ml.m7i.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-34AA6359` | Studio JupyterLab Apps running on ml.r7i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-34DBA194` | ml.m6i.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3523E641` | ml.r6i.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-3597CD5B` | ml.m6i.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-35C54F5F` | Rate of ListEndpoints requests | UNSUPPORTED: API rate/throttle quota |
| `L-35E5433E` | ml.c6g.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-363335BC` | Studio CodeEditor Apps running on ml.r6id.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-36C5FA8E` | ml.c5.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-36FB5B0A` | Studio JupyterLab Apps running on ml.r6id.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-37059D02` | ml.c5n.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3727EAE2` | ml.m4.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-379E85A3` | ml.m5.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-37CA4776` | ml.r5d.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-382C29C1` | Rate of ListLabelingJobs requests | UNSUPPORTED: API rate/throttle quota |
| `L-3870264F` | ml.r5d.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3887CBE3` | Studio JupyterLab Apps running on ml.c6id.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-391B02C7` | Studio JupyterLab Apps running on ml.r5.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3933622B` | ml.r6i.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-395315DA` | ml.c7i.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-39AB5000` | ml.t3.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-39DC8B41` | ml.m6i.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-39F5FD98` | ml.c5.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-39F81BFB` | Studio JupyterLab Apps running on ml.g4dn.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3A1C8CE1` | ml.c7i.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3A218EBD` | ml.m6i.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3A44AF4B` | Studio KernelGateway Apps running on ml.t3.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-3A549026` | ml.c7i.48xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-3A5C6756` | Studio CodeEditor Apps running on ml.m6i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3A6AD204` | ml.c5.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3A8255D8` | Studio CodeEditor Apps running on ml.r6id.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3AAF267A` | Rate of ListTransformJobs requests | UNSUPPORTED: API rate/throttle quota |
| `L-3AE4911A` | ml.g6e.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3B21AA31` | Studio CodeEditor Apps running on ml.m6id.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3B769A17` | Studio CodeEditor Apps running on ml.r6i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3B90E5BF` | ml.r7i.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-3B9CD1B7` | ml.r7i.large for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3BBC35A9` | ml.r8g.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3BDCD216` | Studio JupyterLab Apps running on ml.m5.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-3BE68F11` | ml.g6.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3C2DFC4F` | ml.r7i.48xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3C3B7CCF` | ml.c6id.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-3D0727A9` | ml.m7i.24xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3D2A1F33` | Studio CodeEditor Apps running on ml.m5.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3D52557B` | Rate of DeleteStudioLifecycleConfig requests | UNSUPPORTED: API rate/throttle quota |
| `L-3E1C9273` | ml.m5.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3E534129` | ml.r7i.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3E65B286` | ml.m5d.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3E9F0918` | ml.inf2.48xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-3ED158E9` | ml.c6i.32xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3ED20532` | Studio JupyterLab Apps running on ml.r6i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3EF45BE2` | Studio JupyterLab Apps running on ml.m5d.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-3F25BA48` | ml.r7i.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-3F3A58A2` | Rate of ListSubscribedWorkteams requests | UNSUPPORTED: API rate/throttle quota |
| `L-3F48ACC6` | ml.c7g.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3F53BF0F` | ml.g4dn.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3FD3F6D0` | ml.c7i.large for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-3FFC0D3D` | Studio CodeEditor Apps running on ml.m6id.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-402598A2` | ml.m7i.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4027057F` | ml.c6gd.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-405E5091` | ml.c7i.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4089485C` | ml.p4d.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-409A03CD` | ml.c5.18xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-40D07D7F` | ml.t3.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-40D4D8E2` | ml.m6i.12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-40E8018C` | ml.g5.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-40F00B06` | ml.c5.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-40F27D43` | ml.inf2.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-41C11899` | ml.g4dn.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-41CDD438` | ml.m7i.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-41CEEA13` | Studio JupyterLab Apps running on ml.m7i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-41D07CEF` | ml.m7i.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4209F944` | ml.m7i.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-42313123` | ml.c6i.32xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4253355C` | Studio JupyterLab Apps running on ml.r6id.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-42E4149B` | ml.g5.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-42EAE6FA` | ml.r6g.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-434233AD` | ml.inf1.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-43562353` | ml.r5.large for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-439BD1E0` | ml.r6i.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-439D1ABB` | ml.m7i.12xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-43F5FC95` | ml.g5.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4422BF16` | ml.c8g.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-448C2416` | ml.eia2.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-44A2C8FD` | ml.c6i.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4530EDEE` | ml.m6i.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4556354E` | Maximum subsampled dataset size AutoML job can be run on | UNSUPPORTED: size/throughput/content quota |
| `L-456B4C5F` | ml.p4de.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-457BA053` | Studio JupyterLab Apps running on ml.c6id.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-4581C083` | ml.c5.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-459D61D1` | ml.m6i.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-45DB9C66` | ml.r5.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-45DE7A7D` | ml.c8g.medium for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-45F58E7E` | ml.p3.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-462E7E5F` | ml.m6id.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-46345DE5` | Studio CodeEditor Apps running on ml.r6i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-4645950E` | ml.g5.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4689E606` | ml.p3.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-46E6B311` | ml.inf2.24xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-46EB709C` | ml.m6i.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-47461EBA` | ml.g4dn.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-4755F613` | RSessionGateway Apps running on ml.t3.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-479D8F33` | Total number of trial components allowed in a single trial, excluding those automatically created by SageMaker | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-47C7A96D` | ml.i3en.12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-47E0BC8F` | ml.p4d.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-47F095C9` | ml.g4dn.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-484388A9` | ml.c5d.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-484E50DA` | ml.r6i.16xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-486519E6` | ml.c5.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-48CFA376` | Studio JupyterLab Apps running on ml.r6id.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-4918D123` | Studio KernelGateway Apps running on ml.g5.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-495AAEE0` | ml.inf1.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-49679826` | ml.c5.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-496E33B0` | Studio CodeEditor Apps running on ml.r6i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-49E4D2AB` | ml.g6.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-49F254F3` | ml.c7i.12xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4A20E33E` | ml.c6i.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4A319ECB` | ml.r5.large for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4A34520C` | Studio CodeEditor Apps running on ml.c6i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-4A423436` | ml.c5n.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4A5B28AA` | ml.c7g.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4A823FAB` | ml.m5.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4A8D754D` | Studio KernelGateway Apps running on ml.m5d.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-4A9F5F15` | ml.r7i.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4ACAC7A4` | ml.g5.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-4AEBC16B` | ml.c7i.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4B55E427` | ml.g6.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4B99D021` | ml.g6.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4BAB566C` | ml.r5.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4C2FABCC` | ml.c6g.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4C5C5CA8` | ml.g4dn.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4C7F99A0` | ml.t3.large for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4CC2593C` | ml.r5d.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4CEE6BA6` | ml.m5.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4D27DFDD` | ml.c5.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4D6B5DFA` | ml.c6id.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-4E1689B6` | ml.r7i.12xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4E39DDC4` | Maximum number of running Studio apps allowed per account | UNSUPPORTED: capacity or runtime quota |
| `L-4E81EEAC` | ml.c6g.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4E89F558` | ml.m7i.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-4E8CFCC7` | Rate of ListMonitoringAlerts requests | UNSUPPORTED: API rate/throttle quota |
| `L-4E9EE949` | ml.c5d.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-4EA24ACA` | Studio CodeEditor Apps running on ml.c6id.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-4EE1482A` | ml.c7i.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4F185009` | ml.m6gd.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4F2BEC71` | Studio KernelGateway Apps running on ml.m5d.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-4F5CA161` | Studio JupyterLab Apps running on ml.c6i.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-4FA8B53C` | ml.r6i.large for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-4FC1E99C` | RSessionGateway Apps running on ml.m5.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-4FC79063` | ml.m6i.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-50222063` | ml.c6id.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-505634D0` | ml.c4.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5064185C` | ml.m6i.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-50755EC1` | ml.c5d.9xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-50AA109F` | ml.c4.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-50B5B169` | ml.g6.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-50E8FACB` | Rate of ListFlowDefinitions requests | UNSUPPORTED: API rate/throttle quota |
| `L-51467CBD` | ml.c6i.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-514B50A3` | ml.m6i.large for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-51BF3F2F` | ml.m6i.32xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-51DC12F9` | ml.g6e.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-52008469` | ml.c7g.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-52109CA8` | Studio CodeEditor Apps running on ml.c5.18xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-52150E9C` | Studio CodeEditor Apps running on ml.c6id.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-524FDA45` | ml.r5d.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-525AAB0A` | ml.c6g.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-528EF552` | ml.r5.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-529379E4` | ml.g4dn.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-529E971B` | ml.c5d.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-529F88CE` | ml.c7i.large for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-52A56414` | ml.m6i.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-52C8D816` | ml.g5.48xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-52DB9D33` | Maximum number of training jobs that each hyperparameter tuning job with Random search strategy can create | UNSUPPORTED: API rate/throttle quota |
| `L-52FB7989` | ml.c7g.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-53138E1F` | RSessionGateway Apps running on ml.m5d.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-53505EA6` | Studio JupyterLab Apps running on ml.m5.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-53570353` | ml.r5.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-536D2DD2` | ml.c6i.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5392B59D` | RSessionGateway Apps running on ml.g4dn.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-539D704C` | ml.c5.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-54106F23` | ml.c4.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-54232165` | ml.m6i.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-5498A089` | ml.m7i.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5498EAEB` | ml.r5d.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-54E3D0FA` | ml.r7i.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-551F1065` | ml.c5n.large for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-55671A7C` | Studio CodeEditor Apps running on ml.g5.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-557C20FC` | Studio CodeEditor Apps running on ml.c7i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-558B6165` | ml.r5.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-55E494BC` | ml.m6i.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-55F9C48A` | ml.r7i.8xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-56245D0D` | ml.g6e.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-566A905C` | ml.c5n.18xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-56A14E33` | Rate of CreateEndpoint requests | UNSUPPORTED: API rate/throttle quota |
| `L-56AE9D73` | ml.g6.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-56C564CA` | ml.m5.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-56D01B5B` | Studio JupyterLab Apps running on ml.m6id.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-56E181D2` | Studio CodeEditor Apps running on ml.r7i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-570B0415` | ml.c7i.large for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-574C8A05` | ml.inf1.6xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-57850F1B` | ml.c7g.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-57998C77` | ml.g4dn.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-57A53C2D` | ml.c7i.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-57AC4E19` | ml.t3.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-57D137CF` | ml.r5d.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-57E5D94E` | Studio JupyterLab Apps running on ml.c6id.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-58132C71` | Studio CodeEditor Apps running on ml.r5.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-5843585A` | ml.c6i.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-58672BCE` | ml.eia1.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5869E902` | ml.r5.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-588F9D8D` | Studio JupyterLab Apps running on ml.m5d.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-589B0DBC` | ml.c4.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-589CE341` | Studio CodeEditor Apps running on ml.c7i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-589D9467` | ml.r7i.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-58B96098` | ml.c4.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-593EF138` | ml.r6gd.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-596C3331` | ml.g5.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-59C3957D` | ml.m6i.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-59E4D2FE` | Studio CodeEditor Apps running on ml.c7i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-59F3BE31` | Studio KernelGateway Apps running on ml.r5.large instance | UNSUPPORTED: capacity or runtime quota |
| `L-5AF0D27D` | Studio KernelGateway Apps running on ml.t3.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-5B185A90` | ml.c6i.24xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5B66C272` | ml.r5d.large for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5B86ED31` | ml.m4.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5C11C23E` | Rate of UpdateTrainingJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-5C31AAE1` | ml.r5d.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5C47EA70` | ml.m5.8xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5C59A967` | ml.m6id.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-5D454ED8` | ml.c6i.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5D8382CB` | ml.g5.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-5DB40C3B` | Studio JupyterLab Apps running on ml.g4dn.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-5DF429C6` | ml.r7i.24xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5E2EB366` | ml.g6e.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5E942007` | ml.g6e.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5ECDEA91` | ml.m6i.large for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5EEB65E6` | Studio CodeEditor Apps running on ml.r7i.48xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-5F0C4D2F` | ml.g5.12xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5F238DF4` | ml.c6gn.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5F2D4124` | ml.m5.24xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5F356922` | ml.c5.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-5F5255E9` | ml.m4.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5F747AE6` | ml.t3.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5F970171` | ml.c6i.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-5FDD3816` | Rate of DescribeTransformJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-60033CF6` | ml.inf2.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-60208949` | Studio CodeEditor Apps running on ml.m7i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-60313EA3` | ml.g6e.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-60470224` | Studio KernelGateway Apps running on ml.g5.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-605A110B` | ml.c4.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6074B0D4` | ml.c6i.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6078D9A8` | Studio JupyterLab Apps running on ml.c6id.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-608EFB1F` | ml.c7i.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-60986E7E` | ml.c6g.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-60995545` | ml.m5.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-60D2A6F0` | Number of instances across all transform jobs | UNSUPPORTED: capacity or runtime quota |
| `L-61116077` | ml.m7i.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-611FA074` | ml.m5.large for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-612DD414` | Rate of InvokeEndpoint requests | UNSUPPORTED: API rate/throttle quota |
| `L-614B09FD` | ml.m5.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-614CBE09` | ml.m6i.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6198DF25` | ml.m4.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-619D6E43` | ml.p3.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-61F9C762` | Studio JupyterLab Apps running on ml.t3.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-622CFD70` | Maximum number of instances per training job | UNSUPPORTED: capacity or runtime quota |
| `L-623492E5` | Studio CodeEditor Apps running on ml.m7i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-62BEAF82` | ml.c7i.48xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-63443CBC` | ml.m4.10xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6362B48D` | Studio CodeEditor Apps running on ml.g6.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-63B78C3C` | Studio JupyterLab Apps running on ml.m7i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-63F6725D` | ml.c8g.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-64067773` | ml.g4dn.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-64211729` | ml.c7i.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-64D52F6C` | ml.r7i.48xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-650D2DBD` | Studio JupyterLab Apps running on ml.m7i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-656A17FA` | Studio CodeEditor Apps running on ml.t3.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-6572F0CF` | ml.r6i.16xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-659C9942` | ml.m7i.large for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-65C4BD00` | ml.g5.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-65D1CFE4` | Canvas Apps running on system instances | UNSUPPORTED: capacity or runtime quota |
| `L-660E0683` | ml.r6gd.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-663B74F3` | ml.m8g.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-66425F2A` | Studio JupyterLab Apps running on ml.r6i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-669A1EF3` | Studio KernelGateway Apps running on ml.m5d.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-66A9D66D` | ml.m6id.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-66EDE70E` | ml.m6i.32xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-673ED3E0` | ml.g6e.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-67A4559B` | Total number of trials a single trial component can be associated to | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-67BEA0AE` | ml.m7i.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-67E7209D` | ml.r5d.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6821867B` | ml.g5.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6829423A` | ml.m5d.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-68480206` | ml.r6i.8xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-68515813` | ml.g6e.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-68CFD09E` | ml.c6id.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-692AF693` | Studio JupyterLab Apps running on ml.m7i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-692B8304` | Studio JupyterLab Apps running on ml.g6.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-6958265E` | RSessionGateway Apps running on ml.c5.large instance | UNSUPPORTED: capacity or runtime quota |
| `L-6995701D` | ml.r6gd.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-699A2417` | ml.m6i.32xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-69AC3D57` | Studio CodeEditor Apps running on ml.t3.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-69C6935E` | ml.m6i.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-69CB6693` | Studio CodeEditor Apps running on ml.m6id.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-69F0FD66` | Studio JupyterLab Apps running on ml.c7i.48xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-69F95BD9` | ml.g6e.8xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6A3E5D65` | ml.g6.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6A6E4B44` | ml.c5d.18xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6A77BD0A` | Studio CodeEditor Apps running on ml.m6id.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-6A85BC13` | ml.p3.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6ABF7180` | ml.c6i.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-6B08BAE2` | ml.g6.48xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6B852928` | Studio CodeEditor Apps running on ml.c7i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-6BB1478A` | Rate of DescribeLabelingJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-6BC98A55` | ml.g5.48xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6BE85179` | ml.c4.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6C1DCF33` | ml.r7i.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6C44F58D` | ml.c7i.large for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6C5791AF` | Studio KernelGateway Apps running on ml.c5.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-6C6CBBDE` | ml.m7i.48xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6C73443F` | ml.c5d.18xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-6C7C4F4E` | ml.g4dn.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6C919CDA` | ml.c7i.48xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6CE24819` | ml.m7i.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6D1A7444` | Rate of DeleteFlowDefinition requests | UNSUPPORTED: API rate/throttle quota |
| `L-6D248045` | ml.r5d.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6D2BF8A8` | Studio CodeEditor Apps running on ml.c6i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-6D865216` | ml.c6g.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6DA79B36` | ml.c6i.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6DF60D19` | ml.c4.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6E02BD88` | ml.r6id.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-6F0044E7` | Studio JupyterLab Apps running on ml.c6i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-6F01766F` | ml.m6i.32xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6F0C387D` | ml.c6i.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-6F0EC0FD` | ml.g6.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6F300DAD` | ml.c7i.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6F46EF71` | ml.g5.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6F69996E` | ml.g5.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6F6C723E` | ml.c4.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6F6C8949` | ml.m5.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6F947DE5` | TensorBoard Apps running on system instances | UNSUPPORTED: capacity or runtime quota |
| `L-6FA0D387` | ml.c5.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6FA7C073` | ml.r7i.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6FCDFC95` | ml.m7i.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-6FF806F0` | Large-sized MLflow Tracking Server usage | UNSUPPORTED: size/throughput/content quota |
| `L-7036F14A` | ml.r5d.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-704CC035` | Rate of CreatePresignedNotebookInstanceUrl requests | UNSUPPORTED: API rate/throttle quota |
| `L-7064D1BA` | ml.c5n.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-70680787` | ml.m7i.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-70A53B0D` | ml.r5d.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-70FCDC93` | Studio JupyterLab Apps running on ml.r7i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-713F6743` | ml.r6g.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-718F98E5` | ml.r5d.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-719822E7` | ml.c7i.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-71EA14AB` | ml.m7i.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-71FAF417` | Studio JupyterLab Apps running on ml.t3.medium instances | UNSUPPORTED: capacity or runtime quota |
| `L-72017957` | ml.g6e.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-721FFF7B` | ml.m8g.48xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-72530F39` | ml.r6i.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-729F2471` | Maximum number of steps allowed per pipeline | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-72C89816` | Studio CodeEditor Apps running on ml.m5.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-72EF9D60` | ml.c4.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-73081A3A` | ml.c7i.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-732722E0` | ml.r7i.large for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-73887D5F` | RSessionGateway Apps running on ml.p3.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-73BEF3A2` | SageMaker Profiler Apps running on system instances | UNSUPPORTED: capacity or runtime quota |
| `L-73EC964F` | ml.g6.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-73EF2FAD` | ml.r7i.48xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-7412F8CF` | ml.m6i.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7432A529` | ml.r6gd.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-744ED636` | ml.r5d.large for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-74B46909` | ml.r5.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-74C31E8C` | ml.m7i.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-751BCA3E` | RSessionGateway Apps running on ml.r5.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-753907C7` | Rate of ListWorkforces requests | UNSUPPORTED: API rate/throttle quota |
| `L-754870FD` | ml.c6gn.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-754E1E96` | Studio JupyterLab Apps running on ml.c6i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-757BF5DF` | ml.inf2.48xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-75A970F1` | ml.g6e.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-75B2C685` | ml.c6i.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-75EB91B4` | Studio CodeEditor Apps running on ml.r6i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-76243C5D` | ml.c7i.48xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-76501DC2` | Studio CodeEditor Apps running on ml.c7i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-769E114F` | ml.g4dn.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-76A72DE0` | Studio CodeEditor Apps running on ml.m6i.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-76A7309C` | ml.m5.12xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-76AB2C05` | ml.m5.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-76AF5271` | ml.m7i.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-76D497CD` | Studio KernelGateway Apps running on ml.g5.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-77076358` | Maximum number of cluster scheduler config versions allowed per account in each region. | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-776B84D7` | Rate of UpdateWorkteam requests | UNSUPPORTED: API rate/throttle quota |
| `L-77B8159A` | Studio JupyterLab Apps running on ml.m5.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-77C35A0F` | ml.eia2.medium for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-78278E63` | Studio CodeEditor Apps running on ml.c6i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-786E9B47` | ml.c4.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-7882E313` | ml.r7i.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-78B3DA25` | ml.c6gn.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-78F18862` | Studio JupyterLab Apps running on ml.r6i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-7939E4EC` | ml.m5.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7A45086A` | RSessionGateway Apps running on ml.t3.medium instance | UNSUPPORTED: capacity or runtime quota |
| `L-7AA0FEE8` | ml.m5d.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-7AB35940` | ml.r5.large for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7ACB52C8` | Studio JupyterLab Apps running on ml.r5.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-7AD98814` | ml.m7i.16xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7B131A59` | ml.t3.large for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7B177AC5` | ml.m7i.large for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7B2FD69B` | ml.t2.medium for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-7B628106` | ml.m6i.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7B64C2AB` | ml.c6i.32xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7B7E548F` | RSessionGateway Apps running on ml.m5.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-7B952AC7` | ml.m7i.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7BD2C9FA` | ml.g4dn.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7BDD9EA3` | ml.c5.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7C5EE730` | ml.r5d.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7C9662F1` | Studio JupyterLab Apps running on ml.m5.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-7D217E5D` | ml.g5.48xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7D28AD75` | ml.g4dn.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7DC6CDE9` | ml.g6.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7E503C5F` | ml.m6i.large for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7E675D8C` | ml.m7i.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7E95878B` | Studio KernelGateway Apps running on ml.m5.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-7ECCC97B` | Rate of DeleteWorkteam requests | UNSUPPORTED: API rate/throttle quota |
| `L-7F2FEE7C` | RSessionGateway Apps running on ml.m5d.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-7FA2A64F` | Studio JupyterLab Apps running on ml.r7i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-7FADB696` | Rate of DescribeModel requests | UNSUPPORTED: API rate/throttle quota |
| `L-7FD92B01` | RSessionGateway Apps running on ml.g4dn.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-7FEDBA4C` | ml.m4.16xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-7FFAF4CB` | Studio KernelGateway Apps running on ml.r5.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-802752F2` | Studio JupyterLab Apps running on ml.m6id.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-80324B66` | ml.m7i.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-804C2AFF` | Studio JupyterLab Apps running on ml.g6.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-80BD5FD2` | ml.c7i.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8101A535` | RSessionGateway Apps running on ml.m5d.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-812CA1D8` | ml.g6e.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-813472D5` | ml.r7i.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-81482A8C` | ml.c5.18xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-814FCB98` | Studio JupyterLab Apps running on ml.m6i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-81940D85` | Studio JupyterLab Apps running on ml.g5.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-819B4B27` | ml.c5.18xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-81AF96F3` | ml.c6i.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-81CDC86A` | ml.r8g.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-81DAAA90` | ml.m6i.8xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-822C5A39` | ml.g5.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-823DAB46` | ml.t3.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-823F5794` | Studio JupyterLab Apps running on ml.m5.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-824CD705` | ml.c6i.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8276C21E` | Studio Jupyter Apps running on system instances | UNSUPPORTED: capacity or runtime quota |
| `L-82BF4638` | ml.c8g.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-82E48A74` | ml.gr6.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-82FF331C` | ml.r7i.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8345B953` | ml.g5.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-835D2208` | ml.m7i.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-83A50567` | ml.c7i.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-83AB5D73` | Studio JupyterLab Apps running on ml.g5.48xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-843BE5AB` | ml.m6i.32xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8442D925` | RSessionGateway Apps running on ml.m5.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-845DE61C` | ml.c6i.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8489026E` | Studio CodeEditor Apps running on ml.m6i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-8497E1A4` | ml.g6e.48xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8510FD88` | ml.r7i.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8536F2DB` | Studio KernelGateway Apps running on ml.r5.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-8541302D` | ml.m5.large for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8553AE9A` | Studio CodeEditor Apps running on ml.r7i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-85573624` | ml.m7i.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-85655586` | ml.c6i.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-85870296` | ml.r5.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-85D4BAF3` | ml.c4.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-85DBDADC` | ml.c7g.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-85E60595` | ml.m4.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-860ED60D` | Maximum number of concurrently running model card export jobs allowed per account. | UNSUPPORTED: capacity or runtime quota |
| `L-86177F8A` | Studio CodeEditor Apps running on ml.m5d.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-862299A2` | ml.r6g.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-862C1E14` | ml.m5.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-866A1DFA` | ml.c8g.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8679F6F3` | ml.g4dn.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-86822EDB` | ml.g5.16xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-86845C1F` | ml.r5d.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-86BF447B` | ml.c7i.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-86CB710A` | ml.m7i.large for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-86F70267` | Studio CodeEditor Apps running on ml.g6.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-86FD5133` | ml.r7i.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-87055470` | Studio JupyterLab Apps running on ml.c6id.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-8716E6AE` | ml.m6i.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8728B705` | ml.r8g.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8733EEBD` | RSessionGateway Apps running on ml.c5.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-8762A75F` | ml.p5.48xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-878E276D` | ml.c7i.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-87958880` | Studio CodeEditor Apps running on ml.m5d.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-87989AE6` | Studio JupyterLab Apps running on ml.m6i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-88193F03` | ml.c6i.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-88244E2D` | Studio JupyterLab Apps running on ml.m5d.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-882F7F72` | ml.c8g.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-88E48241` | ml.g5.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-89737A45` | Studio CodeEditor Apps running on ml.r6i.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-89855A04` | Studio CodeEditor Apps running on ml.m7i.48xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-899D2891` | ml.r5d.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-89F2FD35` | ml.m7i.48xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8A6C3F0E` | ml.g5.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8A72B806` | ml.c5n.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8A9BC23B` | Studio JupyterLab Apps running on ml.r5.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-8ACE1754` | Studio JupyterLab Apps running on ml.g6.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-8B077C42` | Studio JupyterLab Apps running on ml.r6i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-8B308035` | ml.c4.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8B9D0385` | RSessionGateway Apps running on ml.c5.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-8BACBF19` | ml.m7i.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-8BB74069` | ml.c6i.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8BD17C20` | Studio KernelGateway Apps running on ml.t3.large instance | UNSUPPORTED: capacity or runtime quota |
| `L-8BED04E5` | ml.r5.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-8BF5F502` | ml.g6.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8C2C8B44` | ml.c7i.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8C616CCB` | Studio CodeEditor Apps running on ml.g5.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-8C9D5748` | ml.m6i.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8CB23490` | ml.r5.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-8CB3A099` | ml.g6.8xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8CC2A52D` | ml.r5d.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8CCF67BD` | ml.g6.48xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8CD1FE93` | ml.t3.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8D013305` | ml.eia1.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8D196E75` | ml.g6.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8D2ED7BF` | Studio JupyterLab Apps running on ml.g5.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-8DE26E59` | Studio JupyterLab Apps running on ml.c5.9xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-8E2DEB6B` | Studio CodeEditor Apps running on ml.c6id.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-8E454C05` | ml.t3.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-8E5A292F` | Studio JupyterLab Apps running on ml.m6id.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-8E6F4665` | ml.g5.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8EE21F5A` | ml.m7i.large for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8EE25AE3` | ml.m6g.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8F13CFFD` | ml.c6i.32xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8F28AFFB` | ml.m5d.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8F6952F2` | ml.r5d.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8F818E82` | ml.m6id.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-8F92321F` | ml.g6.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-8FAD84BA` | ml.inf2.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-901586D2` | ml.r5.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9025A0D4` | Studio JupyterLab Apps running on ml.r6id.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-9055BEAC` | Studio JupyterLab Apps running on ml.c7i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-905FFCC4` | Studio JupyterLab Apps running on ml.m7i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-90765203` | ml.c4.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-909CDAD7` | ml.m8g.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-90D2ED40` | Studio CodeEditor Apps running on ml.r5.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-90ED9514` | Studio CodeEditor Apps running on ml.r5.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-913947FA` | ml.g6.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-91580987` | ml.r7i.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-919688C1` | ml.c5d.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-91CDDDD6` | Studio CodeEditor Apps running on ml.m6i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-9215A13F` | ml.c5.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-924D392D` | ml.r5.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-925D4671` | Studio JupyterLab Apps running on ml.r6id.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-9260DE8C` | ml.m8g.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-92D1521D` | Studio JupyterLab Apps running on ml.g6.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-93490D80` | ml.r6gd.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-934B4E57` | ml.c6i.16xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-93531071` | ml.g6e.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9388DC01` | ml.m8g.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-93958082` | Number of instances across all spot training jobs | UNSUPPORTED: capacity or runtime quota |
| `L-93DC53C2` | ml.m6i.12xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-940A662A` | ml.m7i.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-941884ED` | ml.c6gn.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9421DC3A` | Studio CodeEditor Apps running on ml.c6i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-944F78BB` | ml.g4dn.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-945D1F1D` | ml.c5.9xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-945D83D8` | ml.g6e.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-94C3A7A1` | ml.t2.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-94E271A3` | Studio KernelGateway Apps running on ml.g5.48xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-954CE822` | ml.g6.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-955074FD` | ml.g4dn.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-95528A90` | Studio CodeEditor Apps running on ml.m6id.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-956703D9` | ml.m5d.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-9592FA20` | Studio CodeEditor Apps running on ml.r7i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-95B12835` | ml.m6gd.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-95E39457` | ml.m5.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-9614C779` | ml.g5.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-962247BA` | Studio JupyterLab Apps running on ml.g6.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-962705EA` | ml.g5.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-96300102` | Maximum total concurrency that can be allocated across all serverless endpoints | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-9639CC81` | ml.m6i.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-964887D9` | ml.m6i.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9694914A` | Studio CodeEditor Apps running on ml.g4dn.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-96A28D02` | ml.g6e.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-96B75525` | ml.c5.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-96D8C574` | Studio JupyterLab Apps running on ml.r7i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-96E3A68C` | Rate of DescribeTrainingJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-9723DD27` | ml.c7i.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9760E62B` | Studio KernelGateway Apps running on ml.p4d.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-9772863B` | Studio KernelGateway Apps running on ml.m5.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-9778E614` | ml.m6i.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-978CD7EC` | ml.c4.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-97AC1A59` | Medium-sized MLflow Tracking Server usage | UNSUPPORTED: size/throughput/content quota |
| `L-97CF11BE` | ml.m4.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-982BF852` | ml.c6i.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9849A15E` | ml.c7i.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-98560DD6` | ml.m6i.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-98742DAD` | ml.c5.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-988CE6C5` | Studio JupyterLab Apps running on ml.g5.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-989B6391` | ml.r6i.32xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-98B8C60B` | Studio JupyterLab Apps running on ml.c5.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-98BDE811` | ml.g6.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-98BFB21C` | Studio CodeEditor Apps running on ml.g4dn.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-98D57156` | ml.r6i.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-98E77032` | ml.m7i.48xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-98F45D48` | ml.m5d.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9944ECC4` | ml.c5d.9xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-994A48B1` | Studio JupyterLab Apps running on ml.r6i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-99881E10` | ml.g6.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-99AD19BF` | Maximum number of serverless endpoints | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-99E18227` | Studio JupyterLab Apps running on ml.m6i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-9A2C5AF9` | ml.c8g.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9AB16BF2` | ml.m7i.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9AD04286` | ml.m5.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-9AD1D725` | ml.c5.9xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9AD5A106` | ml.c6i.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-9BA5373F` | ml.c4.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9BCBBE07` | ml.c7i.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9BF41C0F` | Studio JupyterLab Apps running on ml.c6id.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-9C2FFCB7` | Rate of CreateTransformJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-9C33052B` | ml.g6.48xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9C39178F` | ml.inf2.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9C72BEE2` | ml.g4dn.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9C8CF3DC` | ml.g6e.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9CD2705A` | ml.g6.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9CE6464D` | Studio JupyterLab Apps running on ml.m5d.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-9D10CA98` | ml.m6g.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9D3B2C53` | Rate of DescribeStudioLifecycleConfig requests | UNSUPPORTED: API rate/throttle quota |
| `L-9D41067A` | Studio KernelGateway Apps running on ml.p3.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-9D578B5E` | ml.m6i.large for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9D782CC7` | Maximum number of hyper parameter tuning jobs that can run at once in parallel | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-9D9F9978` | Studio KernelGateway Apps running on ml.g5.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-9E017069` | ml.eia2.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9E4D1B86` | ml.r7gd.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9EB87FF0` | Rate of StopTransformJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-9EFE4FAD` | ml.t2.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-9F2E8F67` | Studio KernelGateway Apps running on ml.c5.9xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-9F3B1F91` | Studio KernelGateway Apps running on ml.m5d.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-9F536CF3` | ml.r5.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9FAC65F7` | ml.g5.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9FB41A1C` | Studio CodeEditor Apps running on ml.m5.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-9FC178C2` | Small-sized MLflow Tracking Server usage | UNSUPPORTED: size/throughput/content quota |
| `L-9FE5CC2D` | ml.c7i.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-9FEBBCCF` | ml.r6i.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-A028E7A2` | ml.c4.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-A06D6E01` | ml.c5d.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A0B4500D` | ml.p3.16xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A0B632ED` | Studio CodeEditor Apps running on ml.m5.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-A0B6ED81` | ml.i3en.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A0C4F9CF` | ml.c6id.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-A0E4DD54` | ml.c6i.8xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A0EB0A2A` | Rate of DescribeEndpoint requests | UNSUPPORTED: API rate/throttle quota |
| `L-A0EDD8D6` | Studio CodeEditor Apps running on ml.m7i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A1025C0C` | ml.g6.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A1364089` | ml.c6i.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-A1420A06` | Studio JupyterLab Apps running on ml.m6id.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-A15DF696` | ml.g6e.12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A16FEEFE` | Studio CodeEditor Apps running on ml.r6id.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A1E21094` | ml.c5n.18xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A24D873D` | Time at which pipeline executions time out | UNSUPPORTED: no direct persistent resource inventory |
| `L-A2512F8F` | ml.c5.9xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A28AF48F` | ml.r5.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A29549DE` | Rate of UpdateNotebookInstance requests | UNSUPPORTED: API rate/throttle quota |
| `L-A2A04122` | Studio CodeEditor Apps running on ml.m7i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A2E4CEFE` | ml.r6id.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-A2EAB650` | ml.m6i.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A31DE840` | Studio CodeEditor Apps running on ml.m5d.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A32DD430` | Studio JupyterLab Apps running on ml.m6i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A373146E` | ml.m4.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A37B67B0` | Total EBS volume size in GB across all Studio Spaces | UNSUPPORTED: size/throughput/content quota |
| `L-A3AA2757` | Rate of ListNotebookInstanceLifecycleConfigs requests | UNSUPPORTED: API rate/throttle quota |
| `L-A3C7A675` | RSessionGateway Apps running on ml.m5d.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-A3CA0A7E` | Rate of ListWorkteams requests | UNSUPPORTED: API rate/throttle quota |
| `L-A40ED4BA` | ml.r5d.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A4213CB4` | ml.c7i.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A43A8354` | ml.r7i.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A4519BF1` | Studio KernelGateway Apps running on ml.c5.18xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-A4529C29` | Studio CodeEditor Apps running on ml.m5d.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A47E464A` | ml.m7i.48xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A4B610DA` | Studio JupyterLab Apps running on ml.r7i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-A4BC6738` | Studio CodeEditor Apps running on ml.c6id.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A4C3B69F` | ml.r5d.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A4C63F0B` | Studio CodeEditor Apps running on ml.m7i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-A50827DD` | ml.m4.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A56EEC3D` | Studio KernelGateway Apps running on ml.c5.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-A5D63399` | Maximum number of instances per processing job | UNSUPPORTED: capacity or runtime quota |
| `L-A62BA7D5` | ml.m6i.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A6338E51` | Studio JupyterLab Apps running on ml.m6id.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A63CA0EB` | Studio CodeEditor Apps running on ml.g4dn.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A6419EF6` | Studio JupyterLab Apps running on ml.c5.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-A663541C` | Maximum dataset size AutoML job can be run on | UNSUPPORTED: size/throughput/content quota |
| `L-A68C3C9C` | ml.r6i.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A72DDE21` | Studio JupyterLab Apps running on ml.r6id.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A7B1AACC` | RSessionGateway Apps running on ml.g4dn.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-A7E8B111` | ml.c7g.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A810B462` | ml.r5.large for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A82A7A66` | Studio JupyterLab Apps running on ml.c7i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-A82B1FAA` | Studio JupyterLab Apps running on ml.r6i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-A82FD95C` | ml.r6i.12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A8827666` | ml.p4d.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A886A53A` | ml.g6.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A8A29A23` | ml.r5d.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A8D5B4AA` | ml.c7i.48xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A9165189` | RSessionGateway Apps running on ml.g4dn.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-A9527A17` | ml.g6.16xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A97F0519` | ml.g6e.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-A9CD2FA4` | ml.m7i.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-A9F2A8B3` | ml.m5.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AA088DA9` | ml.c6i.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-AA5E2462` | ml.r5.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AA7135D4` | Studio CodeEditor Apps running on ml.g5.48xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-AA8CF8C4` | ml.r7i.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AA91CB2D` | ml.g6e.16xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AABA5942` | Studio JupyterLab Apps running on ml.g6.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-AB53E0CA` | ml.m6gd.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-ABAC207F` | Studio JupyterLab Apps running on ml.c5.18xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-ABB537FE` | Studio JupyterLab Apps running on ml.r6id.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-ABFCF5A2` | ml.c5.9xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AC014CFB` | ml.g5.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AC802292` | ml.c6i.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AC9EC023` | ml.m6i.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-ACC42312` | Studio CodeEditor Apps running on ml.r6id.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-ACD9A4A4` | ml.r7i.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-AD0A282D` | ml.m5.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AD2BA317` | Rate of DescribeFlowDefinition requests | UNSUPPORTED: API rate/throttle quota |
| `L-AD3B35FF` | ml.c5.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AD4C1352` | ml.g4dn.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AD63F1D2` | Studio JupyterLab Apps running on ml.p4d.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-AD9316E0` | Rate of UpdateEndpointWeightsAndCapacities requests | UNSUPPORTED: API rate/throttle quota |
| `L-ADBE66E5` | RSessionGateway Apps running on ml.p3.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-AE0B3C3D` | Studio CodeEditor Apps running on ml.c6i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-AE2F2D88` | ml.r6gd.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AE3447AD` | ml.m6i.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AE407E8B` | ml.g6e.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AE93C70E` | ml.m6i.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AE9844E7` | Studio CodeEditor Apps running on ml.r7i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-AEB45880` | ml.m5d.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-AED8308D` | ml.r6i.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-AF1BC9E1` | ml.m6g.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AFB011B4` | ml.m5.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-AFEEB9EB` | ml.m4.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B013C051` | ml.g5.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B039EA8F` | Studio JupyterLab Apps running on ml.t3.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-B03C553E` | ml.r5.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B06EA6BA` | ml.m6id.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-B0729CB4` | ml.g6e.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B0A4992C` | ml.m6i.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B0E221DE` | ml.g6.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B0F91871` | ml.g6.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B1369D96` | ml.r6i.32xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B156D5EC` | ml.r5.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B1845A48` | Studio CodeEditor Apps running on ml.r6i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-B1C4D018` | ml.g4dn.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B1CE7499` | Rate of DescribeNotebookInstanceLifecycleConfig requests | UNSUPPORTED: API rate/throttle quota |
| `L-B21D8B36` | ml.m5.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B232DF69` | ml.m5.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B257AB01` | ml.g6e.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B25B9B93` | ml.m6gd.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B271A5D9` | ml.c7i.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B2B3BA64` | ml.inf1.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B2D8E643` | ml.r5.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B307949A` | ml.r5.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B3737E03` | Studio CodeEditor Apps running on ml.r6id.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-B38DFB56` | ml.r7i.16xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B3FC00CD` | ml.m4.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B46EE84C` | ml.m6gd.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B49B1A1D` | ml.c7i.24xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B4C54251` | ml.r5d.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B50E4FC3` | Rate of DescribeEndpointConfig requests | UNSUPPORTED: API rate/throttle quota |
| `L-B5124877` | Studio JupyterLab Apps running on ml.m6id.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-B51E8A99` | Rate of DeleteTransformJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-B538D5DB` | ml.c5.18xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B54F7F84` | ml.r5d.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B57580F5` | Rate of StopTrainingJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-B581F102` | Studio JupyterLab Apps running on ml.c7i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-B5D1E461` | ml.r6i.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-B5F303BE` | ml.c5.9xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-B644CD97` | ml.c5.large for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B6744048` | RSessionGateway Apps running on ml.m5d.large instance | UNSUPPORTED: capacity or runtime quota |
| `L-B67CFA0C` | ml.g4dn.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B68C8DD7` | Studio JupyterLab Apps running on ml.m7i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-B6A274A9` | ml.c7i.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B6A6325E` | ml.r7i.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B6BF3EB3` | ml.m8g.medium for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B6D80D9C` | ml.g5.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B6DC27DA` | ml.r7i.large for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B71FA538` | Rate of ListHumanTaskUis requests | UNSUPPORTED: API rate/throttle quota |
| `L-B74ED3C1` | ml.r5.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-B7A07BB4` | ml.t3.large for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B7AC53F5` | ml.m5d.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B7AE5453` | ml.r5.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B7E8699C` | ml.r7i.large for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B7EB1FFD` | RSessionGateway Apps running on ml.m5.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-B82FDF78` | ml.t2.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B8378206` | ml.m6id.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-B83BF0BE` | ml.c7i.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B87A968D` | ml.c6g.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B89C4B79` | RStudioServerPro Apps running on system instances | UNSUPPORTED: capacity or runtime quota |
| `L-B8A3B4CE` | ml.r6g.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B8C1F9B8` | Studio CodeEditor Apps running on ml.g6.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-B9080C32` | ml.g5.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B95AAE44` | ml.t3.large for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B984C7D5` | Studio JupyterLab Apps running on ml.g6.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-B98A08AE` | Studio CodeEditor Apps running on ml.m7i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-B99D4EA0` | ml.c6i.32xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-B9D177E1` | ml.c6i.32xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-B9F1A904` | Rate of CreateNotebookInstanceLifecycleConfig requests | UNSUPPORTED: API rate/throttle quota |
| `L-BA5B2FC5` | ml.g6.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BA5C7A54` | ml.g4dn.12xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BA5EF415` | Rate of CreateModel requests | UNSUPPORTED: API rate/throttle quota |
| `L-BA8ED5F7` | Studio CodeEditor Apps running on ml.m5d.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-BAC087B0` | Studio CodeEditor Apps running on ml.m6i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-BB72E7FA` | ml.m4.10xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BB73F76A` | ml.r6g.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BC1C7D38` | ml.m5.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BC684567` | ml.g6.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BC6B3288` | ml.g5.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BCA2C892` | ml.r5.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BCA7D0DE` | ml.m4.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BCBB517D` | ml.r7i.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BCBC84AA` | ml.m6g.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BCDEC7B7` | Studio KernelGateway Apps running on ml.m5d.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-BD05AE89` | ml.r5d.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BD09952F` | Studio JupyterLab Apps running on ml.c5.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-BD97DD7F` | ml.m5.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-BDDC56AF` | RSessionGateway Apps running on ml.m5.large instance | UNSUPPORTED: capacity or runtime quota |
| `L-BE30C13D` | ml.r7i.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BE44390B` | ml.t2.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-BE78F29C` | ml.m4.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-BE792A7A` | ml.g5.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BE9444D9` | ml.g6e.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BEAEADC8` | ml.g6e.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BEF3120E` | ml.p4de.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-BF4FD612` | ml.r6i.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-BF6C9DF0` | Studio JupyterLab Apps running on ml.c5.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-BF717A6B` | Studio JupyterLab Apps running on ml.c6i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-BFB30A8F` | Studio CodeEditor Apps running on ml.r7i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-C056993F` | Studio CodeEditor Apps running on ml.r6i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-C0592240` | Studio JupyterLab Apps running on ml.c5.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-C076FA77` | ml.t3.large for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C087612A` | ml.c4.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C1031CE4` | ml.g6e.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C104F114` | Studio CodeEditor Apps running on ml.r6i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-C10DAD58` | ml.c6gd.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C15ACFF4` | ml.c5.9xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C177D66D` | ml.r6id.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-C17B05C4` | ml.m4.10xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C1971434` | ml.c6i.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C1A208ED` | Rate of CreateNotebookInstance requests | UNSUPPORTED: API rate/throttle quota |
| `L-C1AE5754` | Studio JupyterLab Apps running on ml.c5.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-C1AEC017` | ml.g6e.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C1B9A48D` | ml.g5.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C1E62DF0` | ml.m6g.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C1E6B202` | ml.c5n.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C1E99663` | ml.r8g.48xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C1EBA9C5` | ml.c5.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C22BC883` | ml.r6id.32xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-C2495BC4` | ml.g4dn.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C24CB777` | Studio JupyterLab Apps running on ml.c6id.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-C2EE0881` | ml.gr6.8xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C2F8103D` | ml.g4dn.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-C35F807B` | ml.g4dn.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C3E706F6` | Maximum number of Ground Truth Streaming labeling jobs | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-C4008A6B` | ml.m4.10xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C4557679` | Studio CodeEditor Apps running on ml.p3.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-C4717561` | Rate of DeleteEndpointConfig requests | UNSUPPORTED: API rate/throttle quota |
| `L-C47C8B74` | Studio KernelGateway Apps running on ml.c5.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-C48C555A` | Rate of CreateEndpointConfig requests | UNSUPPORTED: API rate/throttle quota |
| `L-C491AA4E` | ml.m7i.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C4B5BAD2` | ml.c6gd.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C4DFBAA1` | ml.r5d.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C51A0845` | ml.r7i.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C56471C1` | Studio CodeEditor Apps running on ml.m7i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-C5747110` | ml.m7i.large for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C57B8181` | ml.r5.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C5A266EB` | Size of EBS volume for a training job instance | UNSUPPORTED: capacity or runtime quota |
| `L-C5A57F3A` | RSessionGateway Apps running on ml.p3.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-C5B2C408` | ml.c4.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C5B4EE09` | ml.c4.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C6079701` | ml.r7i.48xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C623FF97` | Studio CodeEditor Apps running on ml.c5.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-C6383286` | ml.g5.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C691FBAD` | ml.r6id.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-C720D775` | RSessionGateway Apps running on ml.r5.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-C7494E04` | ml.c6i.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C7B212A3` | ml.c7i.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-C7DCB657` | ml.g6e.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C8044861` | ml.c5.18xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C80F4352` | Studio CodeEditor Apps running on ml.c6id.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-C83A0F84` | Rate of DescribeSubscribedWorkteam requests | UNSUPPORTED: API rate/throttle quota |
| `L-C87FF004` | ml.g5.48xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C88C8F13` | ml.m5.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C899B716` | Rate of ListMonitoringAlertHistory requests | UNSUPPORTED: API rate/throttle quota |
| `L-C8AB7CDA` | ml.inf2.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C8B8462D` | ml.g6.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C960C80D` | ml.g4dn.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-C98EE842` | Rate of DeleteNotebookInstanceLifecycleConfig requests | UNSUPPORTED: API rate/throttle quota |
| `L-CAEE7DB7` | ml.g5.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CB4A3655` | ml.g4dn.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CB4B91F3` | ml.m7i.48xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CB985DC5` | ml.p3.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CBBEA301` | ml.c8g.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CBCD290E` | Studio KernelGateway Apps running on ml.c5.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-CC73B658` | Studio KernelGateway Apps running on ml.r5.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-CCA2CA42` | ml.m6gd.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CCE2AFA6` | ml.m5.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CCE6D1FE` | ml.c6gd.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CCEE4B8C` | ml.g6e.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CD017EBE` | Studio KernelGateway Apps running on ml.m5.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-CD3B6B80` | ml.m6i.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CDC3B509` | ml.g6.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CDFDF9FD` | ml.m7i.large for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CE130130` | ml.g6e.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CE2C0A43` | ml.m6i.24xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CE3F2C41` | Studio CodeEditor Apps running on ml.r6id.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-CE6894AA` | ml.m4.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-CE772A48` | ml.c6i.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CED6A634` | Maximum number of parameters allowed per pipeline | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-CEED8B6B` | ml.c7i.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-CEEF9A6E` | ml.m4.10xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-CF4A1BAE` | ml.m6i.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CF4F44AD` | ml.c6i.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CF81ED81` | ml.m4.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-CFC2D5B6` | Maximum number of concurrent AutoML Jobs | UNSUPPORTED: capacity or runtime quota |
| `L-CFF1A7E1` | ml.r6id.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-D01EC2F3` | Rate of CreateLabelingJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-D0327E29` | ml.c5n.9xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D04B88E2` | ml.c5n.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D0B132AA` | ml.c4.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-D0EA3DC8` | ml.m5.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D12B1AA4` | Studio KernelGateway Apps running on ml.p3.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-D144443B` | ml.c5n.9xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D152CACC` | ml.r5d.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D1AFBF6F` | ml.g6e.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D1BB9472` | ml.m6i.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D1E4F16E` | Studio CodeEditor Apps running on ml.m5d.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D1F7791E` | Studio CodeEditor Apps running on ml.c7i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D205D3F0` | RSessionGateway Apps running on ml.c5.9xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-D216E27D` | ml.i3en.6xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D21B7162` | ml.r5d.large for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D24A5F8F` | ml.i3en.16xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D25FCBA1` | ml.c7i.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D266139B` | ml.g5.48xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-D267F635` | Studio KernelGateway Apps running on ml.g4dn.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-D2CAE1E9` | RSessionGateway Apps running on ml.r5.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-D33B72B9` | ml.c7i.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D35E48B2` | ml.m4.10xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D39ED03D` | ml.c7i.12xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D3CC7B01` | Studio CodeEditor Apps running on ml.m6id.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-D460D348` | ml.m6i.16xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D463F25C` | ml.c7i.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D470D954` | ml.g6.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D4D7435A` | Studio KernelGateway Apps running on ml.m5.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-D4EE434E` | ml.r5.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D5106C9A` | ml.m7i.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D526E050` | ml.c6i.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D531C9E1` | Studio JupyterLab Apps running on ml.p3.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D53933F5` | Studio JupyterLab Apps running on ml.c7i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D589112D` | ml.m4.2xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D5D3B1E5` | Studio KernelGateway Apps running on ml.r5.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-D62610A9` | Total number of trial components allowed from a SageMaker context, excluding those automatically created by SageMaker | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-D6B1EB0D` | ml.r6id.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-D6EBD1A9` | Studio JupyterLab Apps running on ml.m5.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D6EC8840` | ml.m7i.8xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D7137944` | Maximum number of compute quota versions allowed per account in each region. | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-D71E726A` | ml.r5d.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D7932DDD` | RSessionGateway Apps running on ml.t3.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-D79647DB` | ml.g4dn.16xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D7BEE2A3` | Size of EBS volume for a processing job instance | UNSUPPORTED: capacity or runtime quota |
| `L-D7CE983F` | ml.m4.16xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D7D166A0` | ml.m4.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D7D29FB6` | Studio JupyterLab Apps running on ml.p3.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D7D95295` | ml.g5.48xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D7ED8DED` | Studio CodeEditor Apps running on ml.m5d.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D7FE33BF` | ml.r6g.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D7FF3362` | ml.r5.24xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-D8830406` | ml.g6.12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D88B02E6` | Studio JupyterLab Apps running on ml.m7i.48xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D88DB51B` | Studio CodeEditor Apps running on ml.m7i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D8A40472` | ml.c5n.18xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D8B97089` | ml.g4dn.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-D8CDAD21` | Studio CodeEditor Apps running on ml.c5.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D8FA228C` | ml.c6i.32xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D91735C4` | ml.i3en.large for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-D9B45548` | Studio KernelGateway Apps running on ml.g4dn.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-D9B5C786` | ml.r7i.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-D9E59670` | RStudioServerPro Apps running on ml.c5.9xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-D9F69758` | ml.m6i.large for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DA37C575` | ml.c6gn.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DA5A09B2` | Studio CodeEditor Apps running on ml.c6id.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-DA7C9B9C` | Studio CodeEditor Apps running on ml.g5.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-DA9E8BF2` | Studio JupyterLab Apps running on ml.r7i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-DAB12A9F` | ml.r6i.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DAB6AA41` | ml.m4.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DABA7ED5` | ml.t3.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DACE30FC` | ml.r6g.12xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DAE78A2A` | ml.r5.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-DB00E0E3` | ml.m7i.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DB4D51CF` | ml.g5.4xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DB5B82A8` | ml.c6gn.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DB62C864` | Maximum number of instances per spot training job | UNSUPPORTED: capacity or runtime quota |
| `L-DBF210E3` | ml.g6.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DC90E824` | ml.r8g.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DC93118C` | ml.c5n.4xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DCCEDB7D` | RSessionGateway Apps running on ml.p4d.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-DCD9DBD1` | RSessionGateway Apps running on ml.m5d.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-DCE2AE7E` | Studio KernelGateway Apps running on ml.g5.4xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-DD18D5D6` | ml.g5.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DD1D4232` | ml.m6i.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-DD362E80` | ml.r5.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DD42D93D` | ml.c6i.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DD508305` | ml.c5n.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DDA1AAD8` | Size of EBS volume for a transform job instance | UNSUPPORTED: capacity or runtime quota |
| `L-DE02D088` | Studio CodeEditor Apps running on ml.c6id.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-DE07CBDF` | ml.g5.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DE22CE7F` | ml.c6i.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DE40B39E` | ml.r7i.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DE587792` | Rate of ListTrainingJobs requests | UNSUPPORTED: API rate/throttle quota |
| `L-DE5F2160` | Studio JupyterLab Apps running on ml.m6i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-DE7D3776` | ml.g6e.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DE8FE3FA` | ml.r7gd.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DE9841A6` | ml.m6g.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DEE7535D` | Rate of CreateHumanTaskUi requests | UNSUPPORTED: API rate/throttle quota |
| `L-DF052B7B` | ml.c4.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DF3F3E67` | ml.r7gd.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DF589F40` | Studio CodeEditor Apps running on ml.g5.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-DF759A63` | Studio JupyterLab Apps running on ml.c7i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-DFB10FDE` | ml.g6.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-DFF9A17E` | ml.c6id.8xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-E0299BF7` | ml.r5d.large for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E0385488` | ml.r7gd.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E05B041E` | Studio JupyterLab Apps running on ml.r6id.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E091038E` | ml.c5.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E0A39AB4` | ml.r6i.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E0C458EA` | ml.g6e.48xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E1249695` | ml.m4.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-E13DF72A` | Maximum size of EBS volume in GB for a SageMaker HyperPod cluster instance | UNSUPPORTED: capacity or runtime quota |
| `L-E157C95B` | Studio JupyterLab Apps running on ml.r5.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E17566B7` | ml.t3.medium for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-E1ACD1F8` | ml.r5.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E20CA2A9` | Rate of DeleteNotebookInstance requests | UNSUPPORTED: API rate/throttle quota |
| `L-E215EF33` | ml.c5n.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E2274DDA` | Rate of DeleteModel requests | UNSUPPORTED: API rate/throttle quota |
| `L-E2649D46` | ml.m5.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E28416C6` | ml.r7gd.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E2A0AC0F` | ml.m5.12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E2BB44FE` | ml.c5.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E2BDBB46` | ml.r5.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E2E710C5` | Studio JupyterLab Apps running on ml.r6i.32xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E2E903C6` | ml.m5.24xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E312D77E` | ml.m4.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E31E799C` | ml.r7i.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E3362D50` | Studio CodeEditor Apps running on ml.c6i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E3646D22` | Studio CodeEditor Apps running on ml.g5.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E3970643` | ml.m7i.2xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E3C0D615` | ml.c4.xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E3DCB664` | ml.g5.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E3DFC4E9` | Studio JupyterLab Apps running on ml.g4dn.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E4156D7D` | ml.r7i.large for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E4348ACD` | ml.r6id.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-E4515972` | Studio CodeEditor Apps running on ml.g6.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E45AD561` | Studio JupyterLab Apps running on ml.r6i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E4B12EA2` | Total EBS volume size in GB across all notebook instances | UNSUPPORTED: capacity or runtime quota |
| `L-E4B23F6B` | ml.c7i.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-E4F6EF77` | ml.r5.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E5144DC4` | Studio JupyterLab Apps running on ml.m6id.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E5775070` | Studio KernelGateway Apps running on ml.g4dn.2xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-E5884D25` | ml.t3.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-E5A7A988` | ml.t3.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E5FD58AB` | Studio CodeEditor Apps running on ml.t3.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E60A61DF` | ml.m4.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E64F3C7F` | ml.m5.large for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E6623D00` | Rate of UpdateEndpoint requests | UNSUPPORTED: API rate/throttle quota |
| `L-E66E2C21` | Studio KernelGateway Apps running on ml.g5.16xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-E6D074A3` | Studio CodeEditor Apps running on ml.r6id.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-E7898792` | ml.c5.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E84ADEB3` | ml.m7i.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E854D418` | ml.r5.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E863DCD3` | ml.m6i.32xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E8917BB7` | ml.g5.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-E8EAF30E` | Studio CodeEditor Apps running on ml.r5.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-E9136106` | Studio CodeEditor Apps running on ml.m6id.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-E9225B85` | ml.m5.xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E9BB87E2` | ml.c6gn.16xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-E9EE5599` | ml.c5.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EA346344` | ml.g4dn.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EA47BDD3` | Longest run time for a processing job | UNSUPPORTED: no direct persistent resource inventory |
| `L-EAA40023` | ml.r5d.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EAB0CBAB` | ml.g4dn.4xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EAC49F53` | Maximum number of training jobs that each hyperparameter tuning job can create | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-EAC6F82B` | Studio KernelGateway Apps running on ml.t3.medium instance | UNSUPPORTED: capacity or runtime quota |
| `L-EB03CD8A` | ml.m7i.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EB77DBD3` | Studio CodeEditor Apps running on ml.c7i.48xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-EB92BE12` | cluster-ml-r7i-12xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EB93283A` | Studio JupyterLab Apps running on ml.c6i.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-EBB53C25` | ml.c8g.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EBE79C48` | Rate of DescribeHumanTaskUi requests | UNSUPPORTED: API rate/throttle quota |
| `L-EC104295` | ml.t3.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EC351EF7` | ml.c6id.large for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-EC374A06` | ml.g5.12xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-EC686150` | Studio JupyterLab Apps running on ml.m5d.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-ED698555` | ml.c8g.48xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-ED7BD217` | ml.g5.24xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-ED8DEE9B` | Maximum number of instances per endpoint | UNSUPPORTED: capacity or runtime quota |
| `L-ED93A43F` | ml.m4.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EDE09F63` | ml.m5d.4xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-EDFF07E7` | ml.c6gd.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EE5A3114` | Studio CodeEditor Apps running on ml.g6.48xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-EE718475` | Studio JupyterLab Apps running on ml.m5d.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-EE75DBCF` | Studio CodeEditor Apps running on ml.g4dn.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-EEA21C8A` | Studio CodeEditor Apps running on ml.m5.xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-EEA45187` | Studio CodeEditor Apps running on ml.c6i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-EEC4CFAE` | Studio JupyterLab Apps running on ml.c6i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-EEC7404F` | ml.m8g.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EED7F51C` | ml.g5.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EF089D40` | ml.m6i.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EF24FBDB` | Maximum number of model card versions allowed per account. | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-EF2BF7DC` | Studio KernelGateway Apps running on ml.r5.12xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-EF33F9B9` | Studio JupyterLab Apps running on ml.r5.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-EF62EAFA` | Maximum number of dataset objects per labeling job | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-EF662387` | ml.c5.18xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-EFB2F063` | ml.c5.4xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EFBC980A` | ml.m6i.24xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-EFCA02A2` | ml.m7i.8xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F003DF95` | Studio CodeEditor Apps running on ml.m6id.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F0067944` | Maximum number of parallel compilation jobs | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-F0132B48` | ml.r5.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F0365EA9` | ml.r7gd.medium for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F087CCFC` | Studio JupyterLab Apps running on ml.g5.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F0C6E97A` | ml.r6i.12xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F0D9539F` | ml.r7i.24xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F11AF030` | Studio JupyterLab Apps running on ml.c6i.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F18C373F` | Studio JupyterLab Apps running on ml.r7i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F1AB2AEA` | ml.r7i.48xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F1ABFE8A` | ml.r5.8xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F1B1085A` | ml.m6i.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F23B5C47` | Studio JupyterLab Apps running on ml.c7i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F2CC767C` | ml.c6id.32xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-F2F8BB60` | Studio KernelGateway Apps running on ml.c5.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-F30D287E` | ml.c5d.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F311B08F` | Number of instances across all processing jobs | UNSUPPORTED: capacity or runtime quota |
| `L-F314A0DD` | ml.r7i.xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-F330D906` | ml.c6i.2xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F361CE98` | ml.c6i.8xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F3C955A3` | Studio KernelGateway Apps running on ml.g4dn.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-F3F4F82A` | RSessionGateway Apps running on ml.c5.xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-F4145962` | Studio JupyterLab Apps running on ml.m6i.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F41659C8` | ml.r5d.large for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F42DA4C1` | Rate of DescribeWorkteam requests | UNSUPPORTED: API rate/throttle quota |
| `L-F43A1825` | Studio KernelGateway Apps running on ml.m5d.24xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-F49350C0` | RSessionGateway Apps running on ml.r5.8xlarge instance | UNSUPPORTED: capacity or runtime quota |
| `L-F4F08D88` | ml.m4.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F5012757` | ml.r7i.48xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F502E62D` | Studio JupyterLab Apps running on ml.c6i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F526E899` | ml.r7i.16xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F556799F` | Rate of DeleteWorkforce requests | UNSUPPORTED: API rate/throttle quota |
| `L-F5689004` | ml.m5.2xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F59A72DA` | Studio JupyterLab Apps running on ml.g4dn.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F5A8815D` | Studio CodeEditor Apps running on ml.r7i.24xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F62D1B89` | ml.r7i.16xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F63839BF` | ml.g6.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F63BAB3A` | Studio CodeEditor Apps running on ml.g6.12xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F64ABEAB` | Studio JupyterLab Apps running on ml.r7i.48xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F6B8A3A3` | ml.g5.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F6E868D7` | Studio JupyterLab Apps running on ml.c6id.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F70A2467` | ml.g6e.12xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F73C7DB9` | Studio JupyterLab Apps running on ml.g5.2xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F761337C` | ml.inf2.8xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F7D04A63` | ml.r7i.xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F81A365E` | ml.r5d.12xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F88734E1` | ml.g6e.12xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F88776CD` | Maximum number of concurrent pipeline executions allowed per account | UNSUPPORTED: capacity or runtime quota |
| `L-F8AE8304` | Studio CodeEditor Apps running on ml.g5.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-F8B56976` | Rate of DescribeWorkforce requests | UNSUPPORTED: API rate/throttle quota |
| `L-F8C60E1D` | ml.c4.xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F8D7F460` | ml.g6e.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F9042956` | ml.r5.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F93088C1` | ml.p3.8xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F971E784` | ml.inf1.24xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F975D5F5` | Studio CodeEditor Apps running on ml.c7i.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-F978BE20` | ml.c5.xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F97C6864` | ml.m4.xlarge for processing job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F9989D2B` | ml.c7i.16xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-F9EC727B` | Rate of StopLabelingJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-FA13E20B` | ml.r5d.xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FA6957DB` | Studio JupyterLab Apps running on ml.c7i.16xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-FB715320` | ml.t3.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-FB830EC3` | ml.g6.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FBA9FB4A` | ml.m7i.16xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FBB495B2` | ml.r6i.large for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FBB7E9CB` | ml.c4.4xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FC157D3E` | ml.m7i.2xlarge for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FC2BE3FC` | Studio JupyterLab Apps running on ml.r5.large instances | UNSUPPORTED: capacity or runtime quota |
| `L-FC4D7F52` | Maximum total FSx Lustre capacity in TiB across SageMaker HyperPod restricted instance groups | UNSUPPORTED: capacity or runtime quota |
| `L-FC6B95EF` | ml.m7i.24xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FC8415AB` | ml.r6i.24xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FCEDEAC6` | Studio CodeEditor Apps running on ml.t3.medium instances | UNSUPPORTED: capacity or runtime quota |
| `L-FCF4DD1A` | Rate of StartNotebookInstance requests | UNSUPPORTED: API rate/throttle quota |
| `L-FD3B4A6C` | Rate of DeleteHumanTaskUi requests | UNSUPPORTED: API rate/throttle quota |
| `L-FD4AD312` | ml.t3.medium for cluster usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FD4BCA24` | ml.c7i.16xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-FD6F8A4D` | ml.c6i.12xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FD73C65F` | ml.g6.48xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FD9E9507` | ml.c6gd.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FDB47EBF` | Studio CodeEditor Apps running on ml.m5.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-FDD19E2A` | ml.c5n.9xlarge for training warm pool usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FDD27A76` | ml.r8g.2xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FE159C34` | ml.m4.2xlarge for spot training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FE7F1F85` | Studio CodeEditor Apps running on ml.g4dn.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-FE869B40` | ml.g5.4xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FE9C120B` | Studio CodeEditor Apps running on ml.r6i.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-FEC35D99` | RStudioServerPro Apps running on ml.c5.4xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-FEEC5811` | RSessionGateway Apps running on ml.r5.large instance | UNSUPPORTED: capacity or runtime quota |
| `L-FEF755D6` | ml.c5.4xlarge for endpoint usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FF0345A7` | Rate of ListStudioLifecycleConfigs requests | UNSUPPORTED: API rate/throttle quota |
| `L-FF2BFCDC` | ml.inf1.6xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-FF40225D` | Studio JupyterLab Apps running on ml.r5.8xlarge instances | UNSUPPORTED: capacity or runtime quota |
| `L-FF5C9E31` | ml.c6i.16xlarge for transform job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FF78806F` | ml.c5d.2xlarge for notebook instance usage | UNSUPPORTED: capacity or runtime quota |
| `L-FFABC174` | ml.r7i.8xlarge for training job usage | UNSUPPORTED: no direct persistent resource inventory |
| `L-FFBD1638` | Studio CodeEditor Apps running on ml.r7i.12xlarge instances | UNSUPPORTED: capacity or runtime quota |

## `scheduler` (13 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-03C881B9` | ListScheduleGroups request rate | UNSUPPORTED: API rate/throttle quota |
| `L-1DC60392` | ListTagsForResource request rate | UNSUPPORTED: API rate/throttle quota |
| `L-21ED5C4A` | CreateScheduleGroup request rate | UNSUPPORTED: API rate/throttle quota |
| `L-44A0C1A0` | UntagResource request rate | UNSUPPORTED: API rate/throttle quota |
| `L-4F80D7BE` | DeleteScheduleGroup request rate | UNSUPPORTED: API rate/throttle quota |
| `L-53944E21` | DeleteSchedule request rate | UNSUPPORTED: API rate/throttle quota |
| `L-66629D52` | ListSchedules request rate | UNSUPPORTED: API rate/throttle quota |
| `L-6F4B17DE` | CreateSchedule request rate | UNSUPPORTED: API rate/throttle quota |
| `L-754C8BBA` | GetScheduleGroup request rate | UNSUPPORTED: API rate/throttle quota |
| `L-B7845AAE` | UpdateSchedule request rate | UNSUPPORTED: API rate/throttle quota |
| `L-E7A3E659` | TagResource request rate | UNSUPPORTED: API rate/throttle quota |
| `L-F6D2596E` | Invocations throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-FB03E819` | GetSchedule request rate | UNSUPPORTED: API rate/throttle quota |

## `scn` (10 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-0FAA04BA` | Maximum active questions per conversation  | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-1DE0B7F6` | Active and pending invitations | UNSUPPORTED: no direct persistent resource inventory |
| `L-24B8CC9C` | Insights watchlists per instance | UNSUPPORTED: capacity or runtime quota |
| `L-3F81EE7B` | Maximum message history retention | UNSUPPORTED: size/throughput/content quota |
| `L-5420252D` | Active AWS Supply Chain connections per instance | UNSUPPORTED: capacity or runtime quota |
| `L-7C5DB5F6` | Insights LineItems per watchlist | UNSUPPORTED: size/throughput/content quota |
| `L-B582E7FC` | Maximum number of conversations per user | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-D6076B6C` | Data requests | UNSUPPORTED: no direct persistent resource inventory |
| `L-D7FA6849` | Insights watchlists per user | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-F1600C71` | AWS Supply Chain data integration flows per instance | UNSUPPORTED: capacity or runtime quota |

## `secretsmanager` (16 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-06876EE2` | Staging labels attached across all versions of a secret | UNSUPPORTED: no direct persistent resource inventory |
| `L-2D877201` | Rate of GetSecretValue API requests | UNSUPPORTED: API rate/throttle quota |
| `L-2F24C883` | Secret value size | UNSUPPORTED: size/throughput/content quota |
| `L-385CE7B7` | Rate of DescribeSecret API requests | UNSUPPORTED: API rate/throttle quota |
| `L-6A9CA93A` | Rate of GetRandomPassword API requests | UNSUPPORTED: API rate/throttle quota |
| `L-7AA14F8F` | Resource-based policy length | UNSUPPORTED: size/throughput/content quota |
| `L-7DA53705` | Rate of ListSecretVersionIds API requests | UNSUPPORTED: API rate/throttle quota |
| `L-7E29BE3F` | Combined rate of RestoreSecret API requests | UNSUPPORTED: API rate/throttle quota |
| `L-8679C9D9` | Combined rate of RotateSecret and CancelRotateSecret API requests | UNSUPPORTED: API rate/throttle quota |
| `L-8D63BBB6` | Combined rate of PutSecretValue, RemoveRegionsFromReplication, ReplicateSecretToRegion, StopReplicationToReplica, UpdateSecret, and UpdateSecretVersionStage API requests | UNSUPPORTED: API rate/throttle quota |
| `L-8D82A813` | Combined rate of DeleteResourcePolicy, GetResourcePolicy, PutResourcePolicy, and ValidateResourcePolicy API requests | UNSUPPORTED: API rate/throttle quota |
| `L-BC8DD7C4` | Combined rate of TagResource and UntagResource API requests | UNSUPPORTED: API rate/throttle quota |
| `L-BF57D437` | Rate of DeleteSecret API requests | UNSUPPORTED: API rate/throttle quota |
| `L-CBA4CAC4` | Rate of CreateSecret API requests | UNSUPPORTED: API rate/throttle quota |
| `L-F452D4B5` | Rate of BatchGetSecretValue API requests | UNSUPPORTED: API rate/throttle quota |
| `L-FC17872E` | Rate of ListSecrets API requests | UNSUPPORTED: API rate/throttle quota |

## `security-ir` (22 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-004260A3` | Throttle rate limit for BatchGetMemberAccountDetails | UNSUPPORTED: API rate/throttle quota |
| `L-07DD2157` | Throttle rate limit for UpdateMembership | UNSUPPORTED: API rate/throttle quota |
| `L-0C6FEDDC` | Throttle rate limit for ListMemberships | UNSUPPORTED: API rate/throttle quota |
| `L-14F545A0` | Throttle rate limit for ListCases | UNSUPPORTED: API rate/throttle quota |
| `L-2BD26108` | Throttle rate limit for GetCase | UNSUPPORTED: API rate/throttle quota |
| `L-3C89FDA8` | Throttle rate limit for CancelMembership | UNSUPPORTED: API rate/throttle quota |
| `L-418370BE` | Throttle rate limit for ListCaseEdits | UNSUPPORTED: API rate/throttle quota |
| `L-470201CA` | Throttle rate limit for CreateMembership | UNSUPPORTED: API rate/throttle quota |
| `L-5052B1EE` | Service managed cases created in the last day | UNSUPPORTED: no direct persistent resource inventory |
| `L-8228E2A3` | Throttle rate limit for GetCaseAttachmentDownloadUrl | UNSUPPORTED: API rate/throttle quota |
| `L-87F7FF63` | Active self managed cases | UNSUPPORTED: no direct persistent resource inventory |
| `L-90AC1990` | Throttle rate limit for UpdateCase | UNSUPPORTED: API rate/throttle quota |
| `L-9183A0FA` | Throttle rate limit for GetCaseAttachmentUploadUrl | UNSUPPORTED: API rate/throttle quota |
| `L-955499E1` | Throttle rate limit for CloseCase | UNSUPPORTED: API rate/throttle quota |
| `L-9D937963` | Throttle rate limit for ListComments | UNSUPPORTED: API rate/throttle quota |
| `L-A44E2290` | Active service managed cases | UNSUPPORTED: no direct persistent resource inventory |
| `L-A73F66BB` | Throttle rate limit for UpdateCaseStatus | UNSUPPORTED: API rate/throttle quota |
| `L-C342A5D3` | Throttle rate limit for UpdateCaseComment | UNSUPPORTED: API rate/throttle quota |
| `L-CD70E27A` | Throttle rate limit for UpdateResolverType | UNSUPPORTED: API rate/throttle quota |
| `L-CF723868` | Throttle rate limit for CreateCaseComment | UNSUPPORTED: API rate/throttle quota |
| `L-D9B684A4` | Throttle rate limit for CreateCase | UNSUPPORTED: API rate/throttle quota |
| `L-DE41D667` | Throttle rate limit for GetMembership | UNSUPPORTED: API rate/throttle quota |

## `securityhub` (2 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-11E34C3D` | Number of insight results | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-F717136E` | Security Hub finding retention time | UNSUPPORTED: size/throughput/content quota |

## `serverlessrepo` (2 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-3EEA1272` | Free Amazon S3 storage for code packages | UNSUPPORTED: size/throughput/content quota |
| `L-41ACBE3C` | Application policy length | UNSUPPORTED: size/throughput/content quota |

## `servicecatalog` (3 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-223F4C54` | Applications per attribute group | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-2B360974` | Tags per provisioned product | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-3BC91705` | Users, groups, and roles per product | REVIEW: parent-scoped or resource count; no unambiguous API mapping |

## `servicequotas` (12 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-027D2B0A` | Throttle rate for GetRequestedServiceQuotaChange | UNSUPPORTED: API rate/throttle quota |
| `L-09C84CC6` | Throttle rate for GetServiceQuota | UNSUPPORTED: API rate/throttle quota |
| `L-0E18483E` | Throttle rate for ListRequestedServiceQuotaChangeHistoryByQuota | UNSUPPORTED: API rate/throttle quota |
| `L-61010047` | Throttle rate for RequestServiceQuotaIncrease | UNSUPPORTED: API rate/throttle quota |
| `L-6120A68B` | Throttle rate for ListTagsForResource | UNSUPPORTED: API rate/throttle quota |
| `L-65470577` | Throttle rate for ListServiceQuotas | UNSUPPORTED: API rate/throttle quota |
| `L-71DCD22A` | Throttle rate for ListAWSDefaultServiceQuotas | UNSUPPORTED: API rate/throttle quota |
| `L-86127B31` | Throttle rate for TagResource | UNSUPPORTED: API rate/throttle quota |
| `L-A53F603E` | Throttle rate for GetAWSDefaultServiceQuota | UNSUPPORTED: API rate/throttle quota |
| `L-BF40C7E2` | Throttle rate for UntagResource | UNSUPPORTED: API rate/throttle quota |
| `L-C7624166` | Throttle rate for ListRequestedServiceQuotaChangeHistory | UNSUPPORTED: API rate/throttle quota |
| `L-E3924FE5` | Throttle rate for ListServices | UNSUPPORTED: API rate/throttle quota |

## `ses` (2 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-804C8AE8` | Sending quota | UNSUPPORTED: no direct persistent resource inventory |
| `L-CDEF9B6B` | Sending rate | UNSUPPORTED: API rate/throttle quota |

## `signer` (19 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-107F88F0` | Rate of RevokeSignature requests | UNSUPPORTED: API rate/throttle quota |
| `L-34D2D11C` | Rate of ListProfilePermissions requests | UNSUPPORTED: API rate/throttle quota |
| `L-47E1077B` | Rate of UntagResource requests | UNSUPPORTED: API rate/throttle quota |
| `L-4E20C20E` | Rate of CancelSigningProfile requests | UNSUPPORTED: API rate/throttle quota |
| `L-4F2A443B` | Rate of ListTagsForResource requests | UNSUPPORTED: API rate/throttle quota |
| `L-5DB503D1` | Rate of ListSigningJobs requests | UNSUPPORTED: API rate/throttle quota |
| `L-6291E160` | Rate of StartSigningJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-7068EEE0` | Rate of GetRevocationStatus requests | UNSUPPORTED: API rate/throttle quota |
| `L-7E38DDAF` | Rate of TagResource requests | UNSUPPORTED: API rate/throttle quota |
| `L-9A9396FB` | Rate of AddProfilePermission requests | UNSUPPORTED: API rate/throttle quota |
| `L-A99B6F73` | Rate of ListSigningProfiles requests | UNSUPPORTED: API rate/throttle quota |
| `L-C2AF6AB8` | Rate of GetSigningProfile requests | UNSUPPORTED: API rate/throttle quota |
| `L-C934DC82` | Rate of SignPayload requests | UNSUPPORTED: API rate/throttle quota |
| `L-E1BE245B` | Rate of ListSigningPlatforms requests | UNSUPPORTED: API rate/throttle quota |
| `L-E9957E95` | Rate of GetSigningPlatform requests | UNSUPPORTED: API rate/throttle quota |
| `L-EBC45F16` | Rate of RevokeSigningProfile requests | UNSUPPORTED: API rate/throttle quota |
| `L-F86FBF89` | Rate of DescribeSigningJob requests | UNSUPPORTED: API rate/throttle quota |
| `L-FE97337F` | Rate of PutSigningProfile requests | UNSUPPORTED: API rate/throttle quota |
| `L-FEE4A855` | Rate of RemoveProfilePermission requests | UNSUPPORTED: API rate/throttle quota |

## `simspaceweaver` (14 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-0D5EA22A` | Index fields for each entity | UNSUPPORTED: no direct persistent resource inventory |
| `L-196DBE75` | Memory for each compute resource unit | UNSUPPORTED: no direct persistent resource inventory |
| `L-1C081C76` | Data fields for each entity | UNSUPPORTED: no direct persistent resource inventory |
| `L-28D50DBD` | Entity data field size | UNSUPPORTED: size/throughput/content quota |
| `L-5A09ACA0` | Entity transfers between workers | UNSUPPORTED: no direct persistent resource inventory |
| `L-5EB93DDB` | Remote subscriptions for each worker | UNSUPPORTED: no direct persistent resource inventory |
| `L-7688C21B` | Simulation count | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-76C7419E` | Compute resource units for each worker | UNSUPPORTED: no direct persistent resource inventory |
| `L-A8C6832C` | Workers for a simulation | UNSUPPORTED: no direct persistent resource inventory |
| `L-B5A348F7` | Entity transfers on the same worker | UNSUPPORTED: no direct persistent resource inventory |
| `L-C1A95297` | Largest maximum duration (in days) for a simulation | UNSUPPORTED: no direct persistent resource inventory |
| `L-C7078EE6` | vCPUs for each compute resource unit | UNSUPPORTED: capacity or runtime quota |
| `L-D450D3E6` | Compute resource units for each app | UNSUPPORTED: no direct persistent resource inventory |
| `L-F2C1E197` | Entities in a partition | UNSUPPORTED: no direct persistent resource inventory |

## `sms` (2 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-3290AB9E` | Duration of service usage per VM in days | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-AFABDADD` | Concurrent VM migrations | UNSUPPORTED: capacity or runtime quota |

## `sms-voice` (12 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-1306C1EF` | OptOutLists | UNSUPPORTED: no direct persistent resource inventory |
| `L-1A498A50` | Pools | UNSUPPORTED: no direct persistent resource inventory |
| `L-2325465C` | TextMessageMonthlySpend | UNSUPPORTED: no direct persistent resource inventory |
| `L-7988B946` | RegistrationAttachments | UNSUPPORTED: no direct persistent resource inventory |
| `L-95ACE848` | ProtectConfigurations | UNSUPPORTED: no direct persistent resource inventory |
| `L-9A0E302E` | ConfigurationSets | UNSUPPORTED: no direct persistent resource inventory |
| `L-AD1C675F` | VerifiedDestinationPhoneNumbers | UNSUPPORTED: no direct persistent resource inventory |
| `L-BE964C91` | Registrations | UNSUPPORTED: no direct persistent resource inventory |
| `L-C62B0C80` | PhoneNumbers | UNSUPPORTED: no direct persistent resource inventory |
| `L-D6967A02` | SenderIds | UNSUPPORTED: no direct persistent resource inventory |
| `L-DEA21975` | MediaMessageMonthlySpend | UNSUPPORTED: no direct persistent resource inventory |
| `L-FDAE1CE0` | VoiceMessageMonthlySpend | UNSUPPORTED: no direct persistent resource inventory |

## `snow-device-management` (10 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-0C95862B` | ListDeviceResources throttle limit | UNSUPPORTED: API rate/throttle quota |
| `L-209341BC` | DescribeTask throttle limit | UNSUPPORTED: API rate/throttle quota |
| `L-396E856A` | ListTasks throttle limit | UNSUPPORTED: API rate/throttle quota |
| `L-4B75C131` | DescribeDeviceEc2Instances throttle limit | UNSUPPORTED: API rate/throttle quota |
| `L-8A2E571D` | ListExecutions throttle limit | UNSUPPORTED: API rate/throttle quota |
| `L-8BC3C224` | DescribeDevice throttle limit | UNSUPPORTED: API rate/throttle quota |
| `L-8CEBA534` | CancelTask throttle limit | UNSUPPORTED: API rate/throttle quota |
| `L-C90DA346` | CreateTask throttle limit | UNSUPPORTED: API rate/throttle quota |
| `L-CA980D98` | DescribeExecution throttle limit | UNSUPPORTED: API rate/throttle quota |
| `L-CCEAB4FA` | ListDevices throttle limit | UNSUPPORTED: API rate/throttle quota |

## `sns` (43 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-01EACE54` | CheckIfPhoneNumberIsOptedOut Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-038DA0E0` | GetEndpointAttributes Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-039289D5` | ListTopics Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-154ECCA7` | SetSMSAttributes Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-19F66BE5` | ListPhoneNumbersOptedOut Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-21C7FFA6` | ListSubscriptions Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-2EE2434F` | GetSMSSandboxAccountStatus Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-2FE42A3E` | DeleteEndpoint Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-390AADBE` | ListSubscriptionsByTopic Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-41B81227` | ListPlatformApplications Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-4659BFC2` | ListEndpointsByPlatformApplication Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-4738DDCE` | CreatePlatformApplication Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-4EE37BC0` | SetEndpointAttributes Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-6521CF3A` | ListOriginationNumbers Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-6635B4C9` | Promotional SMS Message Delivery Rate per Second | UNSUPPORTED: API rate/throttle quota |
| `L-6A04D1EB` | RemovePermission Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-7B7E3FB8` | CreateSMSSandboxPhoneNumber Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-7E62C088` | Email Delivery Rate per Second | UNSUPPORTED: API rate/throttle quota |
| `L-820458B0` | GetTopicAttributes Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-856966E8` | OptInPhoneNumber Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-876E1222` | GetSubscriptionAttributes Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-93308085` | Unsubscribe Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-93CEC191` | ListTagsForResource Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-9A72FF33` | GetSMSAttributes Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-9D5EC8F7` | DeletePlatformApplication Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-A05852B7` | AddPermission Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-A228E0EB` | SetPlatformApplicationAttributes Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-A30AD1BE` | UntagResource Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-AB928142` | CreateTopic Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-B3509C67` | VerifySMSSandboxPhoneNumber Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-B6107771` | SetSubscriptionAttributes Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-B98ECD3E` | DeleteTopic Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-BBD4D2FF` | Subscribe Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-BCD4AAF3` | SMS Message Spending in USD | UNSUPPORTED: no direct persistent resource inventory |
| `L-BF824DE9` | TagResource Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-C1E19420` | ListSMSSandboxPhoneNumbers Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-CC5551AD` | Transactional SMS Message Delivery Rate per Second | UNSUPPORTED: API rate/throttle quota |
| `L-E1E48E53` | CreatePlatformEndpoint Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-F35E8445` | GetPlatformApplicationAttributes Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-F514C636` | SetTopicAttributes Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-F6A3071A` | DeleteSMSSandboxPhoneNumber Transactions per Second | UNSUPPORTED: API rate/throttle quota |
| `L-F8E2BA85` | Messages Published per Second | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-FF07E5EA` | ConfirmSubscription Transactions per Second | UNSUPPORTED: API rate/throttle quota |

## `social-messaging` (9 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-07DABF82` | Rate of TagResource API requests | UNSUPPORTED: API rate/throttle quota |
| `L-0942AEB8` | Rate of ListTagsForResource API requests | UNSUPPORTED: API rate/throttle quota |
| `L-24D3430B` | Rate of GetWhatsAppMessageMedia API requests | UNSUPPORTED: API rate/throttle quota |
| `L-52675531` | Rate of SendWhatsAppMessage API requests | UNSUPPORTED: API rate/throttle quota |
| `L-67364A44` | Rate of PostWhatsAppMessageMedia API requests | UNSUPPORTED: API rate/throttle quota |
| `L-68B6D81D` | Rate of DeleteWhatsAppMessageMedia API requests | UNSUPPORTED: API rate/throttle quota |
| `L-B752DEC4` | Rate of ListLinkedWhatsAppBusinessAccounts API requests | UNSUPPORTED: API rate/throttle quota |
| `L-D06A8815` | Rate of DisassociateWhatsAppBusinessAccount API requests | UNSUPPORTED: API rate/throttle quota |
| `L-D468F93A` | Rate of UntagResource API requests | UNSUPPORTED: API rate/throttle quota |

## `sqs` (4 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-4FF3DAAF` | Batched Message ID Length | UNSUPPORTED: size/throughput/content quota |
| `L-81970B52` | Message Size in S3 Bucket | UNSUPPORTED: size/throughput/content quota |
| `L-98134C75` | Attributes per Message | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-F115E65A` | Messages per Batch | REVIEW: parent-scoped or resource count; no unambiguous API mapping |

## `ssm` (150 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-00E4B877` | Transactions per second (TPS) for the DeleteActivation API | UNSUPPORTED: API rate/throttle quota |
| `L-0189FAA2` | Transactions per second (TPS) for the DescribeAutomationStepExecutions API | UNSUPPORTED: API rate/throttle quota |
| `L-03C7B7FA` | Monthly action items | UNSUPPORTED: size/throughput/content quota |
| `L-0769EAD5` | Transactions per second (TPS) for the DescribeEffectivePatchesForPatchBaseline API | UNSUPPORTED: API rate/throttle quota |
| `L-09101E66` | Concurrently executing Automations | UNSUPPORTED: capacity or runtime quota |
| `L-0BB2D2EE` | Parameter versions | UNSUPPORTED: no direct persistent resource inventory |
| `L-0EA3E58F` | Transactions per second (TPS) for the StartExecutionPreview API | UNSUPPORTED: API rate/throttle quota |
| `L-115AA42B` | Transactions per second (TPS) for the UpdatePatchBaseline API | UNSUPPORTED: API rate/throttle quota |
| `L-13FAEF3E` | Transactions per second (TPS) for the GetPatchBaseline API | UNSUPPORTED: API rate/throttle quota |
| `L-14B74893` | Start Session Rate | UNSUPPORTED: API rate/throttle quota |
| `L-192186BE` | Transactions per second (TPS) for the UpdateMaintenanceWindowTarget API | UNSUPPORTED: API rate/throttle quota |
| `L-1EB1BE93` | Rate of DeleteParameters requests | UNSUPPORTED: API rate/throttle quota |
| `L-1F60EE8D` | Rate of GetParameters requests | UNSUPPORTED: API rate/throttle quota |
| `L-204D72EE` | Transactions per second (TPS) for the GetMaintenanceWindow API | UNSUPPORTED: API rate/throttle quota |
| `L-2081159F` | Transactions per second (TPS) for the DescribeMaintenanceWindowExecutionTasks API | UNSUPPORTED: API rate/throttle quota |
| `L-2105138B` | Transactions per second (TPS) for the ListAssociationVersions API | UNSUPPORTED: API rate/throttle quota |
| `L-22F7AD98` | Transactions per second (TPS) for the ListResourceComplianceSummaries API | UNSUPPORTED: API rate/throttle quota |
| `L-246F6E92` | Transactions per second (TPS) for the RegisterTargetWithMaintenanceWindow API | UNSUPPORTED: API rate/throttle quota |
| `L-24F2158E` | Transactions per second (TPS) for the RegisterPatchBaselineForPatchGroup API | UNSUPPORTED: API rate/throttle quota |
| `L-26BF3FE6` | Maintenance Window concurrent executions | UNSUPPORTED: capacity or runtime quota |
| `L-2912F481` | Rate of GetParametersByPath requests | UNSUPPORTED: API rate/throttle quota |
| `L-2A90B152` | Total OpsInsights | UNSUPPORTED: no direct persistent resource inventory |
| `L-2AB7CEAA` | Transactions per second (TPS) for the StartAccessRequest API | UNSUPPORTED: API rate/throttle quota |
| `L-2D95D5B2` | Total OpsItems | UNSUPPORTED: size/throughput/content quota |
| `L-2E373755` | Inventory item data size per day | UNSUPPORTED: size/throughput/content quota |
| `L-301DF0C6` | Rate of DescribeParameters requests | UNSUPPORTED: API rate/throttle quota |
| `L-32A72023` | Transactions per second (TPS) for the CreateAssociationBatch API | UNSUPPORTED: API rate/throttle quota |
| `L-32EDF4F0` | ListOpsItemEvents requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-33411F6D` | Transactions per second (TPS) for the RegisterDefaultPatchBaseline API | UNSUPPORTED: API rate/throttle quota |
| `L-34ABAFFC` | CreateOpsItem requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-36B79513` | Transactions per second (TPS) for the DeleteMaintenanceWindow API | UNSUPPORTED: API rate/throttle quota |
| `L-38D3219A` | Queued change request executions | UNSUPPORTED: no direct persistent resource inventory |
| `L-38E2D141` | Systems Manager document size | UNSUPPORTED: size/throughput/content quota |
| `L-39F3DBE3` | AssociateOpsItemRelatedItem requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-3CC7248E` | Transactions per second (TPS) for the StartAssociationsOnce API | UNSUPPORTED: API rate/throttle quota |
| `L-419D965E` | Monthly access requests | UNSUPPORTED: no direct persistent resource inventory |
| `L-42F8EE53` | Transactions per second (TPS) for the DeregisterManagedInstance API | UNSUPPORTED: API rate/throttle quota |
| `L-4312E68C` | DisassociateOpsItemRelatedItem requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-44746CFE` | Concurrently executing rate control automation | UNSUPPORTED: API rate/throttle quota |
| `L-44AFEB8F` | Systems Manager "Conformance pack template" SSM document favorites | UNSUPPORTED: no direct persistent resource inventory |
| `L-4713A935` | CreateActivation TPS burst quota | UNSUPPORTED: API rate/throttle quota |
| `L-48EFCC69` | Transactions per second (TPS) for the GetMaintenanceWindowExecution API | UNSUPPORTED: API rate/throttle quota |
| `L-48F865D9` | Transactions per second (TPS) for the GetAutomationExecution API | UNSUPPORTED: API rate/throttle quota |
| `L-491563A5` | Instance Association Limit | UNSUPPORTED: capacity or runtime quota |
| `L-4B199A0E` | Transactions per second (TPS) for the DescribeAssociationExecutionTargets API | UNSUPPORTED: API rate/throttle quota |
| `L-501C43B7` | Transactions per second (TPS) for the DeleteAssociation API | UNSUPPORTED: API rate/throttle quota |
| `L-5084F2AE` | Transactions per second (TPS) for the DescribePatchGroupState API | UNSUPPORTED: API rate/throttle quota |
| `L-55FA9157` | Describe Sessions Rate | UNSUPPORTED: API rate/throttle quota |
| `L-569762F5` | Rate of LabelParameterVersion requests | UNSUPPORTED: API rate/throttle quota |
| `L-570CBE12` | DeleteOpsItem requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-59F2EC49` | Transactions per second (TPS) for the DescribeMaintenanceWindowTasks API | UNSUPPORTED: API rate/throttle quota |
| `L-624DC2C1` | Total access requests | UNSUPPORTED: no direct persistent resource inventory |
| `L-633DA7F9` | Transactions per second (TPS) for the DescribeAutomationExecutions API | UNSUPPORTED: API rate/throttle quota |
| `L-63DB636A` | Describe instance (node) information rate | UNSUPPORTED: API rate/throttle quota |
| `L-655FE23B` | Transactions per second (TPS) for the CreatePatchBaseline API | UNSUPPORTED: API rate/throttle quota |
| `L-66C0A468` | Transactions per second (TPS) for the CreateAssociation API | UNSUPPORTED: API rate/throttle quota |
| `L-66C13439` | OpsItems per month | UNSUPPORTED: size/throughput/content quota |
| `L-67A346B6` | Transactions per second (TPS) for the UpdateAssociationStatus API | UNSUPPORTED: API rate/throttle quota |
| `L-67CAB5B9` | Describe instance (node) properties rate | UNSUPPORTED: API rate/throttle quota |
| `L-67DAE0B3` | Additional Automation executions that can be queued | UNSUPPORTED: no direct persistent resource inventory |
| `L-68B7146F` | Transactions per second (TPS) for the GetCalendar API | UNSUPPORTED: API rate/throttle quota |
| `L-6954D1E3` | Transactions per second (TPS) for the DescribeAssociationExecutions API | UNSUPPORTED: API rate/throttle quota |
| `L-6ED8928A` | UpdateManagedInstanceRole TPS burst quota | UNSUPPORTED: API rate/throttle quota |
| `L-6FC7BAAA` | Transactions per second (TPS) for the GetAccessToken API | UNSUPPORTED: API rate/throttle quota |
| `L-74DA5678` | Transactions per second (TPS) for the DescribeInstancePatchStates API | UNSUPPORTED: API rate/throttle quota |
| `L-74F38A1D` | Transactions per second (TPS) for the DescribeAvailablePatches API | UNSUPPORTED: API rate/throttle quota |
| `L-7555A2F3` | Monthly change requests | UNSUPPORTED: no direct persistent resource inventory |
| `L-761CA7BD` | Concurrent rate-controlled change request executions | UNSUPPORTED: API rate/throttle quota |
| `L-766FCB89` | Transactions per second (TPS) for the DescribePatchProperties API | UNSUPPORTED: API rate/throttle quota |
| `L-77351679` | Transactions per second (TPS) for the UpdateMaintenanceWindowTask API | UNSUPPORTED: API rate/throttle quota |
| `L-7799FEAA` | Add tags to resource rate | UNSUPPORTED: API rate/throttle quota |
| `L-77BC7794` | Transactions per second (TPS) for the PutCalendar API | UNSUPPORTED: API rate/throttle quota |
| `L-7A67410C` | Transactions per second (TPS) for the DescribeMaintenanceWindowExecutionTaskInvocations API | UNSUPPORTED: API rate/throttle quota |
| `L-7AADEF99` | Transactions per second (TPS) for the PutComplianceItems API | UNSUPPORTED: API rate/throttle quota |
| `L-7ABECCD3` | Transactions per second (TPS) for the GetExecutionPreview API | UNSUPPORTED: API rate/throttle quota |
| `L-7ACB503F` | Terminate Session Rate | UNSUPPORTED: API rate/throttle quota |
| `L-7CE06C40` | Systems Manager SSM "Command" document favorites | UNSUPPORTED: no direct persistent resource inventory |
| `L-7D1B5207` | DeregisterManagedInstance TPS burst quota | UNSUPPORTED: API rate/throttle quota |
| `L-7E6F78DE` | Transactions per second (TPS) for the ListComplianceSummaries API | UNSUPPORTED: API rate/throttle quota |
| `L-7FC1ECAB` | Custom inventory types | UNSUPPORTED: no direct persistent resource inventory |
| `L-86D29B06` | Transactions per second (TPS) for the ListCalendarEvents API | UNSUPPORTED: API rate/throttle quota |
| `L-8760F72A` | Transactions per second (TPS) for the CancelMaintenanceWindowExecution API | UNSUPPORTED: API rate/throttle quota |
| `L-9252FCD2` | Concurrently running automations with blocking actions | UNSUPPORTED: capacity or runtime quota |
| `L-9310AE1F` | Transactions per second (TPS) for the DeregisterPatchBaselineForPatchGroup API | UNSUPPORTED: API rate/throttle quota |
| `L-95DD7585` | Rate of DeleteParameter requests | UNSUPPORTED: API rate/throttle quota |
| `L-99469188` | Transactions per second (TPS) for the StartAutomationExecution API | UNSUPPORTED: API rate/throttle quota |
| `L-995701F3` | Transactions per second (TPS) for the CreateMaintenanceWindow API | UNSUPPORTED: API rate/throttle quota |
| `L-9A3BDF81` | DescribeActivations TPS burst quota | UNSUPPORTED: API rate/throttle quota |
| `L-9AADF3D6` | Transactions per second (TPS) for the DeletePatchBaseline API | UNSUPPORTED: API rate/throttle quota |
| `L-9AEB3A5B` | ListOpsItemRelatedItems requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-9C9BA455` | Transactions per second (TPS) for the GetDefaultPatchBaseline API | UNSUPPORTED: API rate/throttle quota |
| `L-9CEEE184` | Transactions per second (TPS) for the StopAutomationExecution API | UNSUPPORTED: API rate/throttle quota |
| `L-9CFC10D4` | Transactions per second (TPS) for the DeregisterTargetFromMaintenanceWindow API | UNSUPPORTED: API rate/throttle quota |
| `L-9DBA655D` | Transactions per second (TPS) for the DescribeMaintenanceWindowsForTarget API | UNSUPPORTED: API rate/throttle quota |
| `L-A3642506` | Transactions per second (TPS) for the SendAutomationSignal API | UNSUPPORTED: API rate/throttle quota |
| `L-A786999D` | UpdateOpsItem requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-AD2B7BF4` | Advanced tier on-premises managed instances | UNSUPPORTED: capacity or runtime quota |
| `L-ADCC853D` | Transactions per second (TPS) for the ListAssociations API | UNSUPPORTED: API rate/throttle quota |
| `L-B031931C` | Transactions per second (TPS) for the DescribeMaintenanceWindowSchedule API | UNSUPPORTED: API rate/throttle quota |
| `L-B28EAB71` | Systems Manager CloudFormation document size | UNSUPPORTED: size/throughput/content quota |
| `L-B2FDB012` | DeleteActivation TPS burst quota | UNSUPPORTED: API rate/throttle quota |
| `L-B50130F5` | Total change requests | UNSUPPORTED: no direct persistent resource inventory |
| `L-B57320C4` | Standard tier on-premises managed instances | UNSUPPORTED: capacity or runtime quota |
| `L-B856FC41` | Resume Session Rate | UNSUPPORTED: API rate/throttle quota |
| `L-BCC99751` | Standard parameter value | UNSUPPORTED: no direct persistent resource inventory |
| `L-C6126953` | List tags for resource rate | UNSUPPORTED: API rate/throttle quota |
| `L-C666B4B8` | Inventory data size per request | UNSUPPORTED: size/throughput/content quota |
| `L-C98FD403` | Transactions per second (TPS) for the ListComplianceItems API | UNSUPPORTED: API rate/throttle quota |
| `L-CA06CE12` | Additional access requests that can be queued | UNSUPPORTED: no direct persistent resource inventory |
| `L-CB14E78C` | Total action items | UNSUPPORTED: size/throughput/content quota |
| `L-CC88F5D2` | Transactions per second (TPS) for the GetMaintenanceWindowTask API | UNSUPPORTED: API rate/throttle quota |
| `L-CE4D78FF` | Additional rate control automation executions that can be queued | UNSUPPORTED: API rate/throttle quota |
| `L-CE541349` | Transactions per second (TPS) for the UpdateMaintenanceWindow API | UNSUPPORTED: API rate/throttle quota |
| `L-CECCEB04` | Advanced parameter value | UNSUPPORTED: no direct persistent resource inventory |
| `L-CFDD7DBC` | Transactions per second (TPS) for the UpdateManagedInstanceRole API | UNSUPPORTED: API rate/throttle quota |
| `L-D00F3769` | Transactions per second (TPS) for the DescribePatchGroups API | UNSUPPORTED: API rate/throttle quota |
| `L-D0D811A0` | Custom inventory type attributes | UNSUPPORTED: no direct persistent resource inventory |
| `L-D3EE0E92` | Transactions per second (TPS) for the DescribeActivations API | UNSUPPORTED: API rate/throttle quota |
| `L-D500163B` | Rate of PutParameter requests | UNSUPPORTED: API rate/throttle quota |
| `L-D6F0ECB2` | Transactions per second (TPS) for the DescribeAssociation API | UNSUPPORTED: API rate/throttle quota |
| `L-D9013A56` | Monthly OpsInsights | UNSUPPORTED: no direct persistent resource inventory |
| `L-D92E3D5B` | Concurrently executing access requests | UNSUPPORTED: capacity or runtime quota |
| `L-DF93A10D` | Systems Manager managed node fleet size | UNSUPPORTED: size/throughput/content quota |
| `L-DFDF118D` | Systems Manager "Policy" SSM document favorites | UNSUPPORTED: no direct persistent resource inventory |
| `L-E1EFC734` | Transactions per second (TPS) for the DescribeMaintenanceWindows API | UNSUPPORTED: API rate/throttle quota |
| `L-E2609C16` | Transactions per second (TPS) for the UpdateAssociation API | UNSUPPORTED: API rate/throttle quota |
| `L-E265D3AF` | Transactions per second (TPS) for the DescribeInstancePatches API | UNSUPPORTED: API rate/throttle quota |
| `L-E33D9B0D` | GetOpsItem requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-E72257B6` | Rate of GetParameter requests | UNSUPPORTED: API rate/throttle quota |
| `L-E899D51B` | Transactions per second (TPS) for the GetMaintenanceWindowExecutionTask API | UNSUPPORTED: API rate/throttle quota |
| `L-EB5F275D` | Transactions per second (TPS) for the RegisterTaskWithMaintenanceWindow API | UNSUPPORTED: API rate/throttle quota |
| `L-ECD4A92E` | Transactions per second (TPS) for the GetMaintenanceWindowExecutionTaskInvocation API | UNSUPPORTED: API rate/throttle quota |
| `L-ED39BA30` | Transactions per second (TPS) for the CreateActivation API | UNSUPPORTED: API rate/throttle quota |
| `L-EDAA5204` | Rate of UnlabelParameterVersion requests | UNSUPPORTED: API rate/throttle quota |
| `L-EF027D0A` | Transactions per second (TPS) for the GetDeployablePatchSnapshotForInstance API | UNSUPPORTED: API rate/throttle quota |
| `L-EF1E03CE` | Transactions per second (TPS) for the DescribeInstanceAssociationsStatus API | UNSUPPORTED: API rate/throttle quota |
| `L-EF50046D` | Systems Manager "Session" SSM document favorites | UNSUPPORTED: no direct persistent resource inventory |
| `L-F07C1865` | Get Connection Status Rate | UNSUPPORTED: API rate/throttle quota |
| `L-F19BE923` | Transactions per second (TPS) for the DeregisterTaskFromMaintenanceWindow API | UNSUPPORTED: API rate/throttle quota |
| `L-F25281C0` | Transactions per second (TPS) for the DescribeEffectiveInstanceAssociations API | UNSUPPORTED: API rate/throttle quota |
| `L-F457BDEB` | Remove tags from resource rate | UNSUPPORTED: API rate/throttle quota |
| `L-F5EE8B1B` | Inventory data retention period | UNSUPPORTED: size/throughput/content quota |
| `L-F716D492` | Transactions per second (TPS) for the DescribePatchBaselines API | UNSUPPORTED: API rate/throttle quota |
| `L-F7BECA7A` | Transactions per second (TPS) for the GetCalendarState API | UNSUPPORTED: API rate/throttle quota |
| `L-F93F4DF6` | Transactions per second (TPS) for the GetPatchBaselineForPatchGroup API | UNSUPPORTED: API rate/throttle quota |
| `L-F96BC21C` | Transactions per second (TPS) for the DescribeMaintenanceWindowExecutions API | UNSUPPORTED: API rate/throttle quota |
| `L-F9BD0C82` | Rate of GetParameterHistory requests | UNSUPPORTED: API rate/throttle quota |
| `L-FA4D3C50` | Transactions per second (TPS) for the DescribeInstancePatchStatesForPatchGroup API | UNSUPPORTED: API rate/throttle quota |
| `L-FBC53ED0` | Transactions per second (TPS) for the DescribeMaintenanceWindowTargets API | UNSUPPORTED: API rate/throttle quota |
| `L-FD7BBF54` | Systems Manager Automation runbook favorites | UNSUPPORTED: no direct persistent resource inventory |

## `ssm-contacts` (17 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-05EEDCEB` | ListPagesByContact API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-0C2999E2` | DescribeEngagement API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-0ECD1CFA` | Non-mutating rotation-related API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-1B8F788C` | Rotations per schedule | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-254D300C` | StartEngagement API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-28BF1B5E` | Voice engagement throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-53EDA07E` | All other operations API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-70D46058` | ListPagesByEngagement API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-73C3F2C3` | SMS engagement throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-8F6873DD` | ListEngagements API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-977ABCD7` | DescribePage API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-D35B01ED` | AcceptPage API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-DBEB7593` | Non-mutating SSMContacts-related API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-E25E885A` | ListPageReceipts API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-E86843F5` | GetContact API throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-F3345603` | Email engagement throttle quota | UNSUPPORTED: API rate/throttle quota |
| `L-F890E288` | StopEngagement API throttle quota | UNSUPPORTED: API rate/throttle quota |

## `ssm-guiconnect` (5 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-0D9340F5` | Throttle rate for GetConnection | UNSUPPORTED: API rate/throttle quota |
| `L-64419857` | Concurrent Remote Desktop connections | UNSUPPORTED: capacity or runtime quota |
| `L-6C572BE6` | Throttle rate for StartConnection | UNSUPPORTED: API rate/throttle quota |
| `L-71687733` | Throttle rate for CancelConnection | UNSUPPORTED: API rate/throttle quota |
| `L-FC9CFAED` | Throttle rate for ListConnections | UNSUPPORTED: API rate/throttle quota |

## `ssm-incidents` (35 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-01CCB66A` | ListTagsForResource requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-02FD30E2` | UpdateRelatedItems requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-0476E0C6` | UpdateTimelineEvent requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-12007467` | GetResourcePolicies requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-1494E1F0` | ListIncidentRecords requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-32C59404` | TagResource requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-51B6B2CA` | ListTimelineEvents requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-55AB8DFA` | GetResponsePlan requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-5964C1A6` | StartIncident requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-60218A2B` | ListReplicationSets requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-65614EA3` | Incidents per response plan per month | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-79F7FE3F` | GetIncidentRecord requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-7A88AF26` | BatchGetIncidentFindings requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-81058D72` | DeleteTimelineEvent requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-8635B488` | CreateResponsePlan requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-86E2D041` | Timeline events per incident | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-8BD82D65` | PutResourcePolicy requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-8E3A5BBF` | ListResponsePlans requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-A08553F0` | ListIncidentFindings requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-A23D539A` | CreateReplicationSet requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-A2627BB9` | Related items per incident | UNSUPPORTED: size/throughput/content quota |
| `L-A320D7D7` | UpdateResponsePlan requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-A7E87765` | UpdateIncidentRecord requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-AB732CD0` | DeleteIncidentRecord requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-AFFE651C` | ListRelatedItems requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-B8B5C4FA` | GetReplicationSet requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-B94A3EEA` | UntagResource requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-B9CCDEDA` | DeleteResponsePlan requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-BD3B3682` | CreateTimelineEvent requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-CA5201AF` | GetTimelineEvent requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-D6FEF05F` | UpdateReplicationSet requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-D9F668D1` | UpdateDeletionProtection requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-E7843AED` | DeleteResourcePolicy requests per second | UNSUPPORTED: API rate/throttle quota |
| `L-EA89B72F` | Regions per replication set | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-F7EACE1C` | DeleteReplicationSet requests per second | UNSUPPORTED: API rate/throttle quota |

## `ssm-quicksetup` (14 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-08FD86E5` | Rate of CreateConfigurationManager API requests | UNSUPPORTED: API rate/throttle quota |
| `L-15691887` | Rate of UpdateConfigurationManager API requests | UNSUPPORTED: API rate/throttle quota |
| `L-32A1E232` | Rate of GetServiceSettings API requests | UNSUPPORTED: API rate/throttle quota |
| `L-49A1F5AE` | Rate of TagResource API requests | UNSUPPORTED: API rate/throttle quota |
| `L-4BC9630F` | Rate of GetConfiguration API requests | UNSUPPORTED: API rate/throttle quota |
| `L-4C0D0E01` | Rate of UntagResource API requests | UNSUPPORTED: API rate/throttle quota |
| `L-51697648` | Rate of UpdateConfigurationDefinition API requests | UNSUPPORTED: API rate/throttle quota |
| `L-530440CD` | Rate of ListQuickSetupTypes API requests | UNSUPPORTED: API rate/throttle quota |
| `L-55C09481` | Rate of ListConfigurationManagers API requests | UNSUPPORTED: API rate/throttle quota |
| `L-7939C9BD` | Rate of GetConfigurationManager API requests | UNSUPPORTED: API rate/throttle quota |
| `L-8FDB112B` | Rate of ListTagsForResource API requests | UNSUPPORTED: API rate/throttle quota |
| `L-D4A46C91` | Rate of DeleteConfigurationManager API requests | UNSUPPORTED: API rate/throttle quota |
| `L-F5453BBF` | Rate of UpdateServiceSettings API requests | UNSUPPORTED: API rate/throttle quota |
| `L-FECD5D9F` | Rate of ListConfigurations API requests | UNSUPPORTED: API rate/throttle quota |

## `ssm-sap` (2 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-458E2EE3` | Components per SAP application | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-5B34AA09` | Databases per component | REVIEW: parent-scoped or resource count; no unambiguous API mapping |

## `sso` (3 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-0299121C` | Total number of AWS accounts or applications that can be configured | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-6985B686` | Number of unique groups that can be used to evaluate the permissions for a user | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-C4FCA052` | File size of service provider SAML 2.0 certificates (in PEM format) | UNSUPPORTED: size/throughput/content quota |

## `states` (95 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-0169882E` | DeleteStateMachine throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-06F91E3A` | CreateStateMachineAlias throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-0A0C3368` | PublishStateMachineVersion throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-0AA8035B` | DeleteStateMachineVersion throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-0B6A3253` | DescribeStateMachineAlias throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-0DC55683` | DescribeStateMachineForExecution throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-0DD5CC77` | ValidateStateMachineDefinition throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-0EE9C880` | ListActivities throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-11731986` | CreateStateMachine throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-1342F2DA` | ListExecutions throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-137B3F65` | StateTransition throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-144D81B0` | GetExecutionHistory throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-15419B47` | ListStateMachineVersions throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-15D902EC` |  Open Map Runs | UNSUPPORTED: no direct persistent resource inventory |
| `L-17571B08` | ListMapRuns throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-191B5A6B` | UntagResource throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-198B5406` | ListMapRuns throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-1B55A735` | StartExecution throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-1D8665FF` | RedriveExecution throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-20F3BB5B` | DescribeActivity throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-2225B7C3` | SendTaskHeartbeat throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-233C6A78` | DescribeStateMachine throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-25C72657` | UpdateStateMachine throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-2786AC1A` | SendTaskHeartbeat throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-29AE5D31` | ListStateMachines throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-2C798E2E` | UntagResource throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-2CDE2B0A` | Input file data size for a Map Run | UNSUPPORTED: size/throughput/content quota |
| `L-31300AD4` | StopExecution throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-345D7ED2` | DescribeStateMachineAlias throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-3586FBF7` | Maximum Concurrency | UNSUPPORTED: no direct persistent resource inventory |
| `L-3D708175` | UpdateMapRun throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-3F41C9CA` | Execution time | UNSUPPORTED: no direct persistent resource inventory |
| `L-47716EBC` | Maximum Number of Items Read per Map Run | UNSUPPORTED: size/throughput/content quota |
| `L-4A5FADE3` | DescribeExecution throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-53EFA4BD` | UpdateStateMachineAlias throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-5AD63623` | Execution history retention time | UNSUPPORTED: size/throughput/content quota |
| `L-5D565FF6` | CreateActivity throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-60E71163` | Task execution time | UNSUPPORTED: no direct persistent resource inventory |
| `L-623044A2` | DeleteActivity throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-630CF084` | SendTaskSuccess throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-631A2A16` | GetActivityTask throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-656FC223` | UpdateStateMachineAlias throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-6B5F0D66` | DeleteStateMachineVersion throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-6F348EF6` | ListTagsForResource throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-718BBE49` | DescribeStateMachine throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-752E372A` | Maximum size of CSV headers | UNSUPPORTED: size/throughput/content quota |
| `L-75A8B871` | TestState throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-75EF6064` | Activity pollers per ARN | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-77AA0D13` | StartMapRun throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-7A4BEE15` | ListExecutions throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-7B25D42D` | UpdateStateMachine throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-7B8A8E4B` | StartExpressExecution throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-7DC9CADD` | GetActivityTask throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-809F4173` | DeleteActivity throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-81549E4C` | ListTagsForResource throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-818B33FC` | ListActivities throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-824BD7F8` | Execution idle time | UNSUPPORTED: no direct persistent resource inventory |
| `L-881C30D9` | Resource name length | UNSUPPORTED: size/throughput/content quota |
| `L-88A8339B` | DescribeStateMachineForExecution throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-898DDD72` | StopExecution throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-8FEC45E4` | Input or result data size in task state or execution | UNSUPPORTED: size/throughput/content quota |
| `L-91DFCA1B` | SendTaskFailure throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-94D27F5A` | Maximum redrives of a Map Run | UNSUPPORTED: no direct persistent resource inventory |
| `L-9BACC576` | DescribeMapRun throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-9E82C0BD` | ListStateMachines throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-A0B4DA4A` | DescribeExecution throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-AD9B4E93` | StateTransition throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-B581C5F3` | DescribeActivity throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-B590C09A` | PublishStateMachineVersion throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-B82BF66D` | DescribeMapRun throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-B8A5B662` | Open executions | UNSUPPORTED: no direct persistent resource inventory |
| `L-BE784273` | ValidateStateMachineDefinition throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-BE9DC071` | StartMapRun throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-BF6A8A21` | ListStateMachineAliases throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-C04F0C78` | CreateStateMachineAlias throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-C314E25C` | TagResource throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-C841B85F` | Task retention time in queue | UNSUPPORTED: size/throughput/content quota |
| `L-C96E1D3D` | DeleteStateMachineAlias throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-CDF2E38B` | SendTaskFailure throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-CE44C76B` | Execution history size | UNSUPPORTED: size/throughput/content quota |
| `L-CE9F8059` | StartExecution throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-CFF7B006` | StartExpressExecution throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-D282C59F` | CreateActivity throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-DAFB74D5` | Request size | UNSUPPORTED: size/throughput/content quota |
| `L-DB101538` | RedriveExecution throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-DEAF517C` | UpdateMapRun throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-E58E8A9B` | ListStateMachineAliases throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-E6D39AA7` | CreateStateMachine throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-EACE83FA` | SendTaskSuccess throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-F8B59CB5` | ListStateMachineVersions throttle token refill rate per second | UNSUPPORTED: API rate/throttle quota |
| `L-F965A8DF` | TagResource throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-F9699A68` | GetExecutionHistory throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-FA23558C` | DeleteStateMachine throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-FAA4E8CB` | DeleteStateMachineAlias throttle token bucket size | UNSUPPORTED: API rate/throttle quota |
| `L-FB14794C` | TestState throttle token bucket size | UNSUPPORTED: API rate/throttle quota |

## `storagegateway` (9 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-6D83F84B` | Cached volume gateway Upload Buffer Minimum in GiB | UNSUPPORTED: no direct persistent resource inventory |
| `L-803470D8` | Cached volume gateway Cache Minimum in GiB | UNSUPPORTED: no direct persistent resource inventory |
| `L-87640A7E` | Tape gateway Upload Buffer Minimum in GiB | UNSUPPORTED: no direct persistent resource inventory |
| `L-96D17DE9` | Minimum size of a virtual tape in GiB | UNSUPPORTED: size/throughput/content quota |
| `L-98F44425` | File size | UNSUPPORTED: size/throughput/content quota |
| `L-BD85E1A6` | File gateway Cache Minimum in GiB | UNSUPPORTED: no direct persistent resource inventory |
| `L-C86341FE` | Path length | UNSUPPORTED: size/throughput/content quota |
| `L-E0AEEBAC` | Stored volume gateway Upload Buffer Minimum in GiB | UNSUPPORTED: no direct persistent resource inventory |
| `L-F3EDDF8C` | Tape gateway Cache Minimum in GiB | UNSUPPORTED: no direct persistent resource inventory |

## `swf` (98 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-07B00041` | DescribeDomain throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-0F51A38F` | StartWorkflowExecution throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-10B07C15` | RespondDecisionTaskCompleted throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-10FD2791` | CountOpenWorkflowExecutions throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-11796F0D` | RegisterWorkflowType throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-1188DD51` | RespondDecisionTaskCompleted throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-11BEBC6E` | CountClosedWorkflowExecutions throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-125E0653` | SignalWorkflowExecution throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-158C01C8` | RespondActivityTaskCanceled throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-1B6B2394` | ListClosedWorkflowExecutions throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-1EB8BFAC` | DescribeWorkflowExecution throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-22059A3A` | DeprecateDomain throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-23555C14` | UndeprecateWorkflowType throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-23ED90FD` | PollForDecisionTask throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-28C5E3D9` | TerminateWorkflowExecution throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-3E1AC395` | UndeprecateWorkflowType throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-3E87B554` | RequestCancelWorkflowExecution throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-418A961F` | StartTimer throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-420027E2` | TerminateWorkflowExecution throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-45E4DED8` | UndeprecateDomain throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-4B5905DC` | Open timers per workflow execution | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-521D4B0C` | DeleteWorkflowType throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-522BE746` | UndeprecateActivityType throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-52452CEB` | DeprecateWorkflowType throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-541D480C` | ListTagsForResource throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-542E1377` | UndeprecateActivityType throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-54F7FCCE` | ListOpenWorkflowExecutions throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-58183C51` | GetWorkflowExecutionHistory throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-585C29D3` | Input or output result data size | UNSUPPORTED: size/throughput/content quota |
| `L-60ABAF6D` | DeleteActivityType throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-613386B0` | CountOpenWorkflowExecutions throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-664871FC` | ListTagsForResource throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-67FCAFB0` | DescribeWorkflowType throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-6ACC4529` | RespondActivityTaskFailed throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-6B93B990` | CountClosedWorkflowExecutions throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-6E67C23B` | ListDomains throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-708CA9CD` | ListActivityTypes throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-72A8322C` | RegisterDomain throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-7379A78A` | CountPendingDecisionTasks throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-740FECBB` | TagResource throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-778DA924` | UntagResource throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-78ABDAF0` | CountPendingActivityTasks throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-7B042585` | ListOpenWorkflowExecutions throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-7CE7ADCD` | DeprecateWorkflowType throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-82178AAF` | ListClosedWorkflowExecutions throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-85FB1745` | RegisterActivityType throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-8746B166` | ListActivityTypes throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-889726A2` | RequestCancelWorkflowExecution throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-90E73253` | SignalExternalWorkflowExecution throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-90F927AE` | ScheduleActivityTask throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-91FA29FA` | DeprecateDomain throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-967C6C00` | RequestCancelExternalWorkflowExecution throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-9889E41A` | ScheduleActivityTask throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-9B56EA20` | Request size | UNSUPPORTED: size/throughput/content quota |
| `L-9EB7B9D6` | RespondActivityTaskFailed throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-9F857AB4` | RegisterDomain throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-A32357D7` | Workflow execution time | UNSUPPORTED: no direct persistent resource inventory |
| `L-A4249261` | DeleteWorkflowType throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-A94186CB` | StartTimer throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-B016F208` | Task execution time in year | UNSUPPORTED: no direct persistent resource inventory |
| `L-B03232CC` | SWF task retention time in queue | UNSUPPORTED: size/throughput/content quota |
| `L-B0C289A4` | Open child workflow executions | UNSUPPORTED: no direct persistent resource inventory |
| `L-B1B7886E` | RespondActivityTaskCompleted throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-B59DD71F` | UndeprecateDomain throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-B61DF1D5` | GetWorkflowExecutionHistory throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-B6B07F5F` | DescribeWorkflowExecution throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-B80CE8BF` | CountPendingActivityTasks throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-BC8E42D6` | RequestCancelExternalWorkflowExecution throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-BE04F134` | StartChildWorkflowExecution throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-BEE48758` | StartChildWorkflowExecution throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-C0C38A8F` | ListWorkflowTypes throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-C0F4576E` | UntagResource throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-C2741471` | StartWorkflowExecution throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-C5FCA8F5` | CountPendingDecisionTasks throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-C6E6D788` | DescribeActivityType throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-C943B086` | RegisterActivityType throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-C96251D8` | RespondActivityTaskCompleted throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-CBE45CF4` | RecordActivityTaskHeartbeat throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-CEE29E14` | TagResource throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-D441B742` | RecordActivityTaskHeartbeat throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-D4B08332` | DeprecateActivityType throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-D699363F` | DescribeWorkflowType throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-DE1A2EBB` | DescribeActivityType throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-DF1BC840` | Events in Workflow execution history | UNSUPPORTED: no direct persistent resource inventory |
| `L-DFCD38D8` | PollForDecisionTask throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-E2260636` | DescribeDomain throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-E3E6B073` | RespondActivityTaskCanceled throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-E5906E57` | Pollers per task list | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-E6133E10` | Open activity tasks per workflow execution | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-E73B63BD` | RegisterWorkflowType throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-E74A6FC5` | SignalExternalWorkflowExecution throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-E75077A8` | DeprecateActivityType throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-EABBD6AB` | PollForActivityTask throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-F5350037` | PollForActivityTask throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-F649FC18` | SignalWorkflowExecution throttle refill limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-FBF3CE2F` | ListWorkflowTypes throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-FD69F8F8` | DeleteActivityType throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-FFE46A4B` | ListDomains throttle burst limit in transactions per second | UNSUPPORTED: API rate/throttle quota |

## `textract` (30 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-16E39BCB` | TagResource throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-1E329480` | DeleteAdapter throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-25DA5AF6` | ListAdapterVersions throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-25F2C897` | Async ExpenseAnalysis throttle limit for max number of concurrent jobs | UNSUPPORTED: API rate/throttle quota |
| `L-29FC1640` | CreateAdapter throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-3667A958` | ListTagsForResource throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-3AFF0430` | GetAdapter throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-4CDADAE4` | GetLendingAnalysisSummary throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-5B33D1C3` | Async DocumentTextDetection throttle limit for max number of concurrent jobs | UNSUPPORTED: API rate/throttle quota |
| `L-5CF3B0DF` | Async DocumentAnalysis throttle limit for max number of concurrent jobs | UNSUPPORTED: API rate/throttle quota |
| `L-5E3A5D59` | StartDocumentAnalysis throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-75788A8B` | DetectDocumentText throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-78993479` | GetLendingAnalysis throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-7C2E8C8C` | AnalyzeID throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-7FCF1C0F` | UpdateAdapter throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-80A81B07` | AnalyzeExpense throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-8A021B00` | ListAdapters throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-90151521` | CreateAdapterVersion throttle limit for max number of new successful adapter versions per month | UNSUPPORTED: API rate/throttle quota |
| `L-94C8FE3F` | GetDocumentTextDetection throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-9ACAE5E4` | GetDocumentAnalysis throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-A35C1798` | GetAdapterVersion throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-AE9E2453` | StartDocumentTextDetection throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-B83AD6FF` | AnalyzeDocument throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-C3BB1AF3` | UntagResource throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-CFEC0789` | Async LendingAnalysis throttle limit for max number of concurrent jobs | UNSUPPORTED: API rate/throttle quota |
| `L-E31D91C2` | StartExpenseAnalysis throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-F69F2A31` | DeleteAdapterVersion throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-F94EF855` | CreateAdapterVersion throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-FA2C35B5` | GetExpenseAnalysis throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |
| `L-FF9CE2BA` | StartLendingAnalysis throttle limit in transactions per second | UNSUPPORTED: API rate/throttle quota |

## `timestream` (28 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-00158752` | ListScheduledQueries request rate | UNSUPPORTED: API rate/throttle quota |
| `L-05CF2F29` | Measures per table | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-0C6E4BCB` | ListDatabases request rate | UNSUPPORTED: API rate/throttle quota |
| `L-16B72159` | PrepareQuery request rate | UNSUPPORTED: API rate/throttle quota |
| `L-279D7B08` | DeleteDatabase request rate | UNSUPPORTED: API rate/throttle quota |
| `L-3F031494` | Dimensions per table | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-6044E01C` | DescribeBatchLoadTask request rate | UNSUPPORTED: API rate/throttle quota |
| `L-6B1915C6` | UpdateDatabase request rate | UNSUPPORTED: API rate/throttle quota |
| `L-6C25862A` | DescribeScheduledQuery request rate | UNSUPPORTED: API rate/throttle quota |
| `L-71D80F70` | Unique measures across multi-measure records per table | UNSUPPORTED: size/throughput/content quota |
| `L-7565C2A8` | CreateTable request rate | UNSUPPORTED: API rate/throttle quota |
| `L-798CB19D` | CreateScheduledQuery request rate | UNSUPPORTED: API rate/throttle quota |
| `L-7C9FE50E` | DeleteTable request rate | UNSUPPORTED: API rate/throttle quota |
| `L-8892F7F6` | CreateDatabase request rate | UNSUPPORTED: API rate/throttle quota |
| `L-89E3B36D` | DescribeTable request rate | UNSUPPORTED: API rate/throttle quota |
| `L-8BF444C0` | UpdateScheduledQuery request rate | UNSUPPORTED: API rate/throttle quota |
| `L-8DFD99E7` | UpdateAccountSettings request rate | UNSUPPORTED: API rate/throttle quota |
| `L-8FD9593E` | UpdateTable request rate | UNSUPPORTED: API rate/throttle quota |
| `L-9F20DF3A` | ResumeBatchLoadTask request rate | UNSUPPORTED: API rate/throttle quota |
| `L-A83B13DB` | DescribeAccountSettings request rate | UNSUPPORTED: API rate/throttle quota |
| `L-AE604CE2` | ListTables request rate | UNSUPPORTED: API rate/throttle quota |
| `L-BFCD0C9E` | Maximum count of active magnetic store partitions per database | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-C0E9F2ED` | ExecuteScheduledQuery request rate | UNSUPPORTED: API rate/throttle quota |
| `L-C49D398A` | CreateBatchLoadTask request rate | UNSUPPORTED: API rate/throttle quota |
| `L-F07A9AB4` | ListBatchLoadTasks request rate | UNSUPPORTED: API rate/throttle quota |
| `L-F98EACE7` | DescribeDatabase request rate | UNSUPPORTED: API rate/throttle quota |
| `L-FA296006` | DeleteScheduledQuery request rate | UNSUPPORTED: API rate/throttle quota |
| `L-FEB34FC6` | Max allowed MaxQueryTCU | UNSUPPORTED: no direct persistent resource inventory |

## `transcribe` (55 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-00A7F8C0` | Transactions per second, StartStreamTranscriptionWebSocket | UNSUPPORTED: API rate/throttle quota |
| `L-0599F82B` | Number of concurrent streams (HTTP/2 + Websocket) | UNSUPPORTED: capacity or runtime quota |
| `L-23CCF526` | Transactions per second, CreateVocabulary operation | UNSUPPORTED: API rate/throttle quota |
| `L-27AD4F82` | Number of days that job records are retained | UNSUPPORTED: size/throughput/content quota |
| `L-29C417EC` | Transactions per second, GetCallAnalyticsCategory operation | UNSUPPORTED: API rate/throttle quota |
| `L-2B06FDCC` | Transactions per second, StartStreamTranscription | UNSUPPORTED: API rate/throttle quota |
| `L-2B8713A4` | Maximum audio file size (Medical) | UNSUPPORTED: size/throughput/content quota |
| `L-2C7580BC` | Maximum size of a custom vocabulary | UNSUPPORTED: size/throughput/content quota |
| `L-2D4ED180` | Transactions per second, ListMedicalTranscriptionJobs operation | UNSUPPORTED: API rate/throttle quota |
| `L-2F86860B` | Transactions per second, GetCallAnalyticsJob operation | UNSUPPORTED: API rate/throttle quota |
| `L-30829B86` | Maximum size of a vocabulary filter | UNSUPPORTED: size/throughput/content quota |
| `L-3445E3CD` | Maximum number of targets allowed per category for Call Analytics batch jobs | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-34DCCAED` | Number of days that job records are retained (Medical) | UNSUPPORTED: size/throughput/content quota |
| `L-467D3ED0` | Transactions per second, GetMedicalVocabulary operation | UNSUPPORTED: API rate/throttle quota |
| `L-49DA58C9` | Transactions per second, StartCallAnalyticsStreamTranscriptionWebsocket | UNSUPPORTED: API rate/throttle quota |
| `L-49FE4216` | Maximum length of a custom vocabulary phrase | UNSUPPORTED: size/throughput/content quota |
| `L-4B321684` | Transactions per second, StartCallAnalyticsJob operation | UNSUPPORTED: API rate/throttle quota |
| `L-4D4F1AC4` | Maximum audio file length for Call Analytics batch jobs | UNSUPPORTED: size/throughput/content quota |
| `L-4E017343` | Number of channels for channel identification (Medical) | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-5B9152AD` | Maximum audio file length (Medical) | UNSUPPORTED: size/throughput/content quota |
| `L-612AD79E` | Transactions per second, ListTranscriptionJobs operation | UNSUPPORTED: API rate/throttle quota |
| `L-67DA1F8F` | Number of channels for channel identification | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-6F37B9E3` | Transactions per second, StartTranscriptionJob operation | UNSUPPORTED: API rate/throttle quota |
| `L-765784F2` | Transactions per second, UpdateMedicalVocabulary operation | UNSUPPORTED: API rate/throttle quota |
| `L-79130216` | Transactions per second, GetTranscriptionJob operation | UNSUPPORTED: API rate/throttle quota |
| `L-8043D35A` | Maximum audio file size for Call Analytics batch jobs | UNSUPPORTED: size/throughput/content quota |
| `L-825D9BA6` | Transactions per second, StartMedicalTranscriptionJob operation | UNSUPPORTED: API rate/throttle quota |
| `L-8E9A98C3` | Minimum audio file duration for Call Analytics batch jobs | UNSUPPORTED: no direct persistent resource inventory |
| `L-93564E36` | Transactions per second, ListCallAnalyticsJobs operation | UNSUPPORTED: API rate/throttle quota |
| `L-949A4206` | Job queue bandwidth ratio | UNSUPPORTED: size/throughput/content quota |
| `L-A34A9084` | Number of concurrent Call Analytics streams (HTTP/2 + Websocket) | UNSUPPORTED: capacity or runtime quota |
| `L-A4098D0D` | Transactions per second, StartMedicalStreamTranscription | UNSUPPORTED: API rate/throttle quota |
| `L-A99534C1` | Transactions per second, GetMedicalTranscriptionJob operation | UNSUPPORTED: API rate/throttle quota |
| `L-AAFCE0A3` | Transactions per second, DeleteMedicalTranscriptionJob operation | UNSUPPORTED: API rate/throttle quota |
| `L-AED2C08C` | Transactions per second, ListCallAnalyticsCategories operation | UNSUPPORTED: API rate/throttle quota |
| `L-AEECB49A` | Transactions per second, DeleteCallAnalyticsCategory operation | UNSUPPORTED: API rate/throttle quota |
| `L-B282140E` | Number of days that job records are retained for Call Analytics batch jobs | UNSUPPORTED: size/throughput/content quota |
| `L-B32D80CD` | Transactions per second, CreateCallAnalyticsCategory operation | UNSUPPORTED: API rate/throttle quota |
| `L-B46C0D84` | Transactions per second, ListVocabularies operation | UNSUPPORTED: API rate/throttle quota |
| `L-B7245D62` | Transactions per second, StartMedicalStreamTranscriptionWebsocket | UNSUPPORTED: API rate/throttle quota |
| `L-B8E3E4A0` | Transactions per second, GetVocabulary operation | UNSUPPORTED: API rate/throttle quota |
| `L-C12E2B65` | Maximum audio file length | UNSUPPORTED: size/throughput/content quota |
| `L-C1F432D2` | Number of channels for channel identification for Call Analytics batch jobs | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-C20201ED` | Transactions per second, UpdateVocabulary operation | UNSUPPORTED: API rate/throttle quota |
| `L-CECDF303` | Transactions per second, DeleteTranscriptionJob operation | UNSUPPORTED: API rate/throttle quota |
| `L-D0C82002` | Number of concurrent Medical streams (HTTP/2 + Websocket) | UNSUPPORTED: capacity or runtime quota |
| `L-D2C499F9` | Transactions per second, ListMedicalVocabularies operation | UNSUPPORTED: API rate/throttle quota |
| `L-D6EC4EAD` | Minimum audio file duration | UNSUPPORTED: no direct persistent resource inventory |
| `L-E9D8884B` | Transactions per second, DeleteCallAnalyticsJob operation | UNSUPPORTED: API rate/throttle quota |
| `L-EC6090B0` | Minimum audio file duration (Medical) | UNSUPPORTED: no direct persistent resource inventory |
| `L-ED89E5C0` | Transactions per second, DeleteMedicalVocabulary operation | UNSUPPORTED: API rate/throttle quota |
| `L-F0847210` | Transactions per second, DeleteVocabulary operation | UNSUPPORTED: API rate/throttle quota |
| `L-F4971247` | Transactions per second, UpdateCallAnalyticsCategory operation | UNSUPPORTED: API rate/throttle quota |
| `L-F6E06B47` | Transactions per second, StartCallAnalyticsStreamTranscription | UNSUPPORTED: API rate/throttle quota |
| `L-FE4C37F7` | Maximum audio file size | UNSUPPORTED: size/throughput/content quota |

## `transfer` (20 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-05D4EADD` | Maximum number of new executions per workflow | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-1A59C433` | Rate of StartDirectoryListing per SFTP connector | UNSUPPORTED: API rate/throttle quota |
| `L-1B36ED13` | Maximum inbound AS2 message size | UNSUPPORTED: size/throughput/content quota |
| `L-1B7183EB` | Concurrent AS2 messages per server | UNSUPPORTED: capacity or runtime quota |
| `L-2259D421` | File size | UNSUPPORTED: size/throughput/content quota |
| `L-2B1BC0C3` | Number of files per StartFileTransfer request | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-396F6E73` | Concurrent multiplexed SFTP sessions per connection | UNSUPPORTED: capacity or runtime quota |
| `L-3B829EB0` | Number of authentication requests per user per second | UNSUPPORTED: API rate/throttle quota |
| `L-4963D6B7` | Rate of StartRemoteMove files per SFTP connector | UNSUPPORTED: API rate/throttle quota |
| `L-4978356A` | Rate of AS2 messages per server | UNSUPPORTED: API rate/throttle quota |
| `L-4BAB8288` | Concurrent sessions per server | UNSUPPORTED: capacity or runtime quota |
| `L-57D537DE` | Rate of StartFileTransfer files per SFTP connector | UNSUPPORTED: API rate/throttle quota |
| `L-83F728FB` | Concurrent AS2 messages per connector | UNSUPPORTED: capacity or runtime quota |
| `L-9A414140` | Maximum outbound AS2 message size | UNSUPPORTED: size/throughput/content quota |
| `L-ACBBA5DF` | Maximum logical directory mappings characters | UNSUPPORTED: size/throughput/content quota |
| `L-B6C4BD5F` | Idle connection timeout | UNSUPPORTED: no direct persistent resource inventory |
| `L-CD3E054C` | New executions refill rate per workflow per second | UNSUPPORTED: API rate/throttle quota |
| `L-CFAB221D` | Rate of StartRemoteDelete files per SFTP connector | UNSUPPORTED: API rate/throttle quota |
| `L-E5F10FFD` | Rate of StartFileTransfer files per AS2 connector | UNSUPPORTED: API rate/throttle quota |

## `verifiedpermissions` (27 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-19773BA0` | DeletePolicyStore requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-1FC83DB7` | BatchIsAuthorizedWithToken requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-271BE7E8` | ListPolicyStores requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-2AFF096D` | UpdatePolicy requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-38A7DE67` | DeleteIdentitySource requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-3F1C6115` | CreatePolicyStore requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-3F9287FA` | UpdatePolicyStore requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-4E0E8AFD` | ListPolicies requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-5A76F227` | GetIdentitySource requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-5CA93A13` | DeletePolicyTemplate requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-645D3857` | IsAuthorizedWithToken requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-6DD21905` | CreateIdentitySource requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-70239429` | ListPolicyTemplates requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-771544C7` | IsAuthorized requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-886D79EB` | PutSchema requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-8D5CB09F` | CreatePolicyTemplate requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-8E2326FF` | ListIdentitySources requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-9647C866` | CreatePolicy requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-9DB5CAA4` | BatchIsAuthorized requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-B49B9779` | GetSchema requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-C9736881` | GetPolicy requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-D2870CD3` | UpdateIdentitySource requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-D82415D2` | GetPolicyTemplate requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-DC54B663` | UpdatePolicyTemplate requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-DE99D97D` | BatchGetPolicy requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-E1924570` | GetPolicyStore requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |
| `L-F81CF58F` | DeletePolicy requests per second per Region per account | UNSUPPORTED: API rate/throttle quota |

## `voiceid` (4 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-429DC46D` | Fraudster registration requests per fraudster registration job | UNSUPPORTED: API rate/throttle quota |
| `L-6DD2993B` | Fraudsters per watchlist | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-9EB99B73` | Speaker enrollment requests per speaker enrollment job | UNSUPPORTED: API rate/throttle quota |
| `L-F4849009` | Active streaming sessions per domain | UNSUPPORTED: capacity or runtime quota |

## `vpc` (2 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-3248932A` | Characters per VPC endpoint policy | UNSUPPORTED: size/throughput/content quota |
| `L-8312C5BB` | VPC peering connection request expiry hours | UNSUPPORTED: no direct persistent resource inventory |

## `vpc-lattice` (1 open quota)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-87FCA9B2` | Auth policy size | UNSUPPORTED: size/throughput/content quota |

## `waf-regional` (6 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-02647DC9` | Search length | UNSUPPORTED: size/throughput/content quota |
| `L-28FAE46F` | Rate of requests | UNSUPPORTED: API rate/throttle quota |
| `L-343F131E` | IP addresses blocked per rate-based rule | UNSUPPORTED: API rate/throttle quota |
| `L-797E08C8` | Regex pattern length | UNSUPPORTED: size/throughput/content quota |
| `L-7EF6FB27` | Rate-based rule rate | UNSUPPORTED: API rate/throttle quota |
| `L-AEEA10B9` | HTTP header name length | UNSUPPORTED: size/throughput/content quota |

## `wafv2` (6 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-030B54CC` | Maximum number of referenced statements per rule group or web ACL in WAF for regional | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-74EBD1DD` | Maximum number of unique IP addresses that can be blocked per rate-based rule for regional | UNSUPPORTED: API rate/throttle quota |
| `L-8B48556D` | Maximum size in kilobytes of a web request body that can be inspected for Application Load Balancer and AWS AppSync protections | UNSUPPORTED: size/throughput/content quota |
| `L-A85235F6` | Maximum number of requests per second per web ACL for regional | UNSUPPORTED: API rate/throttle quota |
| `L-C928281E` | Minimum request rate that can be defined for a rate-based rule for regional | UNSUPPORTED: API rate/throttle quota |
| `L-D95DED7E` | Maximum size in kilobytes of a web request body that can be inspected for CloudFront, API Gateway, Amazon Cognito, App Runner, and Verified Access protections | UNSUPPORTED: size/throughput/content quota |

## `wellarchitected` (5 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-0979631D` | Versions per lens | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-0AA67FCF` | Pillars per lens | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-84104561` | Choices per question | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-D5439D2C` | Lens size | UNSUPPORTED: size/throughput/content quota |
| `L-FCB0C16C` | Questions per pillar | REVIEW: parent-scoped or resource count; no unambiguous API mapping |

## `wisdom` (59 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-0090B50A` | Rate of API requests for RenderMessageTemplate | UNSUPPORTED: API rate/throttle quota |
| `L-06FFDC6F` | Rate of API requests for CreateAssistantAssociation | UNSUPPORTED: API rate/throttle quota |
| `L-077B0F42` | Rate of API requests for ListQuickResponses | UNSUPPORTED: API rate/throttle quota |
| `L-08F1AA01` | Rate of API requests for DeleteMessageTemplateAttachment | UNSUPPORTED: API rate/throttle quota |
| `L-10CA616F` | Rate of API requests for GetContentSummary | UNSUPPORTED: API rate/throttle quota |
| `L-12665571` | Rate of API requests for CreateSession | UNSUPPORTED: API rate/throttle quota |
| `L-16823F6A` | Rate of API requests for UpdateKnowledgeBaseTemplateUri | UNSUPPORTED: API rate/throttle quota |
| `L-1C046530` | Maximum size per attachment in an email message template | UNSUPPORTED: size/throughput/content quota |
| `L-20924856` | Rate of API requests for DeleteImportJob | UNSUPPORTED: API rate/throttle quota |
| `L-225955BF` | Rate of API requests for UpdateMessageTemplateMetadata | UNSUPPORTED: API rate/throttle quota |
| `L-2836100B` | Maximum number of characters in an email message template | UNSUPPORTED: size/throughput/content quota |
| `L-286BB24D` | Content size | UNSUPPORTED: size/throughput/content quota |
| `L-30D12FFF` | Rate of API requests for DeleteMessageTemplate | UNSUPPORTED: API rate/throttle quota |
| `L-33825569` | Rate of API requests for GetAssistant | UNSUPPORTED: API rate/throttle quota |
| `L-349001D1` | Rate of API requests for CreateMessageTemplate | UNSUPPORTED: API rate/throttle quota |
| `L-357A675E` | Rate of API requests for GetSession | UNSUPPORTED: API rate/throttle quota |
| `L-3988218B` | Rate of API requests for ListMessageTemplates | UNSUPPORTED: API rate/throttle quota |
| `L-3BBE199E` | Rate of API requests for GetImportJob | UNSUPPORTED: API rate/throttle quota |
| `L-3F7B6949` | Rate of API requests for GetKnowledgeBase | UNSUPPORTED: API rate/throttle quota |
| `L-4159FA2D` | Rate of API requests for GetMessageTemplate | UNSUPPORTED: API rate/throttle quota |
| `L-45879046` | Rate of API requests for DeactivateMessageTemplate | UNSUPPORTED: API rate/throttle quota |
| `L-597AFFD4` | Rate of API requests for SearchQuickResponses | UNSUPPORTED: API rate/throttle quota |
| `L-64F4F8A4` | Rate of API requests for StartImportJob | UNSUPPORTED: API rate/throttle quota |
| `L-67C0E663` | Rate of API requests for UpdateQuickResponse | UNSUPPORTED: API rate/throttle quota |
| `L-6B774E73` | Rate of API requests for UntagResource | UNSUPPORTED: API rate/throttle quota |
| `L-6EAC2850` | Rate of API requests for ListKnowledgeBases | UNSUPPORTED: API rate/throttle quota |
| `L-7183A9AA` | Rate of API requests for NotifyRecommendationsReceived | UNSUPPORTED: API rate/throttle quota |
| `L-748F3E94` | Maximum number of characters in an SMS message template | UNSUPPORTED: size/throughput/content quota |
| `L-75E8D220` | Rate of API requests for DeleteKnowledgeBase | UNSUPPORTED: API rate/throttle quota |
| `L-7A8F45D9` | Rate of API requests for ListAssistantAssociations | UNSUPPORTED: API rate/throttle quota |
| `L-7AA24867` | Rate of API requests for ListTagsForResource | UNSUPPORTED: API rate/throttle quota |
| `L-7BCD6D97` | Rate of API requests for SearchMessageTemplates | UNSUPPORTED: API rate/throttle quota |
| `L-7C77FB1A` | Rate of API requests for CreateKnowledgeBase | UNSUPPORTED: API rate/throttle quota |
| `L-7E7C477E` | Rate of API requests for CreateContent | UNSUPPORTED: API rate/throttle quota |
| `L-84036F17` | Rate of API requests for CreateAssistant | UNSUPPORTED: API rate/throttle quota |
| `L-869A5CB8` | Rate of API requests for DeleteAssistantAssociation | UNSUPPORTED: API rate/throttle quota |
| `L-8B3876B5` | Rate of API requests for ListAssistants | UNSUPPORTED: API rate/throttle quota |
| `L-8B41D6E7` | Maximum number of attachments per email message template | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-9B912B0C` | Rate of API requests for SearchContent | UNSUPPORTED: API rate/throttle quota |
| `L-9F242C3F` | Rate of API requests for UpdateMessageTemplate | UNSUPPORTED: API rate/throttle quota |
| `L-A00E39EA` | Rate of API requests for DeleteAssistant | UNSUPPORTED: API rate/throttle quota |
| `L-A0CF4A4D` | Rate of API requests for CreateMessageTemplateVersion | UNSUPPORTED: API rate/throttle quota |
| `L-A21C97E2` | Rate of API requests for CreateMessageTemplateAttachment | UNSUPPORTED: API rate/throttle quota |
| `L-A5E16775` | Rate of API requests for TagResource | UNSUPPORTED: API rate/throttle quota |
| `L-A67B1533` | Rate of API requests for DeleteContent | UNSUPPORTED: API rate/throttle quota |
| `L-B2D7D043` | Rate of API requests for ListImportJobs | UNSUPPORTED: API rate/throttle quota |
| `L-B5D9B610` | Rate of API requests for GetContent | UNSUPPORTED: API rate/throttle quota |
| `L-BD020A5F` | Rate of API requests for CreateQuickResponse | UNSUPPORTED: API rate/throttle quota |
| `L-BDA36AE2` | Rate of API requests for GetAssistantAssociation | UNSUPPORTED: API rate/throttle quota |
| `L-BE34124B` | Rate of API requests for ActivateMessageTemplate | UNSUPPORTED: API rate/throttle quota |
| `L-C9B885FB` | Rate of API requests for GetQuickResponse | UNSUPPORTED: API rate/throttle quota |
| `L-CA23568A` | Rate of API requests for QueryAssistant | UNSUPPORTED: API rate/throttle quota |
| `L-CA2E4BF7` | Rate of API requests for GetRecommendations | UNSUPPORTED: API rate/throttle quota |
| `L-CBEEAAE4` | Rate of API requests for SearchSessions | UNSUPPORTED: API rate/throttle quota |
| `L-E85308FD` | Rate of API requests for UpdateContent | UNSUPPORTED: API rate/throttle quota |
| `L-E9948A8B` | Rate of API requests for RemoveKnowledgeBaseTemplateUri | UNSUPPORTED: API rate/throttle quota |
| `L-EB422E2D` | Rate of API requests for DeleteQuickResponse | UNSUPPORTED: API rate/throttle quota |
| `L-FBCC7857` | Rate of API requests for ListMessageTemplateVersions | UNSUPPORTED: API rate/throttle quota |
| `L-FE0F5908` | Rate of API requests for StartContentUpload | UNSUPPORTED: API rate/throttle quota |

## `workspaces` (14 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-011B3C20` | General Purpose Standard streaming instances for WorkSpaces Pools | UNSUPPORTED: capacity or runtime quota |
| `L-07C6D3A5` | General Purpose Power streaming instances for WorkSpaces Pools | UNSUPPORTED: capacity or runtime quota |
| `L-0B7D5CA2` | Graphics.g4dn 4xlarge streaming instances for WorkSpaces Pools | UNSUPPORTED: capacity or runtime quota |
| `L-254B485B` | GraphicsPro WorkSpaces | UNSUPPORTED: no direct persistent resource inventory |
| `L-2F7BEDD3` | General Purpose Performance streaming instances for WorkSpaces Pools | UNSUPPORTED: capacity or runtime quota |
| `L-465DA8AF` | GeneralPurpose 4xlarge streaming instances for WorkSpaces | UNSUPPORTED: capacity or runtime quota |
| `L-8C70C791` | General Purpose Value streaming instances for WorkSpaces Pools | UNSUPPORTED: capacity or runtime quota |
| `L-9A67B5CB` | Standby WorkSpaces | UNSUPPORTED: no direct persistent resource inventory |
| `L-BCACAEBC` | Graphics.g4dn WorkSpaces | UNSUPPORTED: no direct persistent resource inventory |
| `L-BE9A8466` | GraphicsPro.g4dn WorkSpaces | UNSUPPORTED: no direct persistent resource inventory |
| `L-C266A5F4` | GeneralPurpose 8xlarge streaming instances for WorkSpaces | UNSUPPORTED: capacity or runtime quota |
| `L-D34D6523` | Graphics.g4dn xlarge streaming instances for WorkSpaces Pools | UNSUPPORTED: capacity or runtime quota |
| `L-D6CFBE96` | WorkSpaces Pools | UNSUPPORTED: no direct persistent resource inventory |
| `L-F7854FE2` | General Purpose PowerPro streaming instances for WorkSpaces Pools | UNSUPPORTED: capacity or runtime quota |

## `workspaces-instances` (1 open quota)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-4842BC54` | Concurrent WorkSpaces Managed Instances in allocating state | UNSUPPORTED: capacity or runtime quota |

## `workspaces-web` (58 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-00C34477` | Rate of GetBrowserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-02CFB9A1` | Rate of ListBrowserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-079D6D1A` | Rate of CreateUserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-095DE697` | Rate of ListPortals requests | UNSUPPORTED: API rate/throttle quota |
| `L-0BC76D3C` | Rate of AssociateTrustStore requests | UNSUPPORTED: API rate/throttle quota |
| `L-0F222D02` | Rate of GetUserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-133AFA92` | Rate of UpdateUserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-14261565` | Rate of CreateIpAccessSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-184EBD82` | Rate of DeleteNetworkSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-1A51C3EA` | Rate of ListTagsForResource requests | UNSUPPORTED: API rate/throttle quota |
| `L-1B5A496A` | Maximum concurrent sessions for the standard.regular instance type in the specified region | UNSUPPORTED: capacity or runtime quota |
| `L-1DB47EFF` | Rate of DisassociateBrowserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-1E9BCE97` | Rate of UpdateIdentityProvider requests | UNSUPPORTED: API rate/throttle quota |
| `L-1F25669B` | Rate of UpdateNetworkSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-28AF32D3` | Maximum concurrent sessions for the standard.large instance type in the specified region | UNSUPPORTED: capacity or runtime quota |
| `L-2C7C0AF1` | Rate of DeleteUserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-322B0066` | Rate of GetPortal requests | UNSUPPORTED: API rate/throttle quota |
| `L-362C3C84` | Rate of DeleteBrowserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-3B5144ED` | Rate of DeleteIpAccessSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-438EBE87` | Rate of DeleteTrustStore requests | UNSUPPORTED: API rate/throttle quota |
| `L-43C1B6E6` | Rate of AssociateNetworkSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-467E6EFD` | Maximum concurrent sessions for the standard.xlarge instance type in the specified region | UNSUPPORTED: capacity or runtime quota |
| `L-48CA0EC9` | Rate of UpdateBrowserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-49DD0E62` | Rate of DisassociateTrustStore requests | UNSUPPORTED: API rate/throttle quota |
| `L-5046A0A4` | Rate of DeleteIdentityProvider requests | UNSUPPORTED: API rate/throttle quota |
| `L-57EB3A5C` | Rate of CreateUserAccessLoggingSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-58202D8F` | Rate of DeleteUserAccessLoggingSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-6D75560B` | Rate of UpdateUserAccessLoggingSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-6E3C18D8` | Rate of CreateIdentityProvider requests | UNSUPPORTED: API rate/throttle quota |
| `L-6F4DA997` | Rate of AssociateUserAccessLoggingSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-75BD2FF5` | Rate of ListTrustStores requests | UNSUPPORTED: API rate/throttle quota |
| `L-77E95BD0` | Rate of DisassociateNetworkSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-79EC01E1` | Rate of ListNetworkSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-86380CED` | Rate of TagResource requests | UNSUPPORTED: API rate/throttle quota |
| `L-885A84B6` | Rate of UpdatePortal requests | UNSUPPORTED: API rate/throttle quota |
| `L-8BF44F8E` | Rate of DeletePortal requests | UNSUPPORTED: API rate/throttle quota |
| `L-8E8025D8` | Rate of DisassociateUserAccessLoggingSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-90048709` | Rate of ListUserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-91742F30` | Rate of ListIdentityProviders requests | UNSUPPORTED: API rate/throttle quota |
| `L-94E642D1` | Rate of UntagResource requests | UNSUPPORTED: API rate/throttle quota |
| `L-955BBE3B` | Rate of UpdateTrustStore requests | UNSUPPORTED: API rate/throttle quota |
| `L-A3E92E82` | Rate of AssociateBrowserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-A7E91E5C` | Rate of GetIpAccessSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-AE820403` | Rate of ListTrustStoreCertificates requests | UNSUPPORTED: API rate/throttle quota |
| `L-BB21B00F` | Rate of CreateNetworkSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-C8E73DC8` | Rate of CreateBrowserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-D5EA059F` | Rate of CreatePortal requests | UNSUPPORTED: API rate/throttle quota |
| `L-D9ADFC33` | Rate of GetIdentityProvider requests | UNSUPPORTED: API rate/throttle quota |
| `L-DCB5C13E` | Rate of ListUserAccessLoggingSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-E1E0B653` | Rate of AssociateIpAccessSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-E207534D` | Rate of GetUserAccessLoggingSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-E81A7683` | Rate of GetNetworkSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-E91D6E7E` | Rate of ListIpAccessSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-EC36A4C6` | Rate of DisassociateIpAccessSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-ED73BCDC` | Rate of UpdateIpAccessSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-ED7C8CD0` | Rate of AssociateUserSettings requests | UNSUPPORTED: API rate/throttle quota |
| `L-F31E6456` | Rate of CreateTrustStore requests | UNSUPPORTED: API rate/throttle quota |
| `L-F64575FC` | Rate of DisassociateUserSettings requests | UNSUPPORTED: API rate/throttle quota |

## `xray` (9 open quotas)

| Quota code | Quota name | Classification |
|---|---|---|
| `L-3B8EFF88` | Trace document size (lower limit) | UNSUPPORTED: size/throughput/content quota |
| `L-428FB8E0` | Trace document size (dynamic upper limit) | UNSUPPORTED: size/throughput/content quota |
| `L-5DB17969` | Trace data modification period in days | UNSUPPORTED: no direct persistent resource inventory |
| `L-998BFF16` | Trace and service graph retention in days | UNSUPPORTED: size/throughput/content quota |
| `L-C6B6F05D` | Indexed annotations per trace | REVIEW: parent-scoped or resource count; no unambiguous API mapping |
| `L-D781C0FD` | Segment document size | UNSUPPORTED: size/throughput/content quota |
| `L-E75A2BBF` | Segments per second | REVIEW: parent-scoped or resource count; no unambiguous API mapping |


## `servicediscovery` (3 offene Quotas)

- `L-0BA10AAE` — **DiscoverInstancesRevision operation per account rate** — `USAGE_METRIC`: Request rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-514A639A` — **DiscoverInstances operation per account steady rate** — `USAGE_METRIC`: Request rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.
- `L-76CF203B` — **DiscoverInstances operation per account burst rate** — `USAGE_METRIC`: Request burst rate; a persistent resource inventory cannot measure current consumption. Requires a compatible official UsageMetric.

