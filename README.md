# AWS Quota Monitor

AWS Service Quotas Monitoring und Alerting System mit Lambda, DynamoDB und SNS.

## Übersicht

Das System erfasst AWS Service Quotas (EC2 und allgemeine Quotas) mit ihren aktuellen Nutzungswerten, speichert diese in DynamoDB und sendet Alerts über SNS, wenn Schwellwerte überschritten werden.

### Architektur

```
┌─────────────┐
│   Lambda    │ (qm-quotacontroller)
│  Function   │
└──────┬──────┘
       │
       ├─→ Service Quotas API
       ├─→ EC2 API (für spezifische Checks)
       ├─→ DynamoDB (Speicherung)
       └─→ SNS Topic (Alerts)
```

## Struktur

### `/src` — Python-Code

- **`main.py`**: Lambda Handler, orchestriert Quotas-Erfassung, Speicherung und Alerting
- **`qmchecks/`**: Quota-Check-Module
  - `general/utilization_report.py`: Allgemeine Quotas via Service Quotas API
  - `ec2/ec2.py`: EC2-spezifische Checks (AMI Sharing, Client VPN, etc.)
- **`qmalerting/`**: Alert-System
  - `alerting.py`: `QuotaAlert` Klasse für SNS-Benachrichtigungen
- **`qmdb/`**: Datenbankzugriff
  - `db.py`: DynamoDB-Operationen

### `/deployment` — Terraform IaC

Vollständige AWS-Infrastruktur als Code:

- **`main.tf`**: Lambda, IAM-Rollen, Policies, SNS Topic, DynamoDB Tabelle
- **`data.tf`**: Archive für Lambda Funktion und Dependencies Layer
- **`variables.tf`**: Konfigurierbare Parameter
- **`version.tf`**: Provider und Terraform-Versionen
- **`terraform.tfvars`**: Deployment-spezifische Werte

## Setup

### Voraussetzungen

- AWS CLI konfiguriert mit Credentials/Profil (z.B. `BA`)
- Terraform >= 1.0
- Python 3.11+ lokal (für Tests)

### Installation lokal

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# AWS-Profil testen
export AWS_PROFILE=BA
python3 src/main.py
```

### Deployment zu AWS

```bash
cd deployment

# Variablen in terraform.tfvars setzen
cat > terraform.tfvars <<EOF
tags = {
  scope = "BA"
  env   = "prod"
}

alert_threshold_pct = 80
alert_email         = "alerts@example.com"
EOF

# Deployen
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars" -auto-approve
```

## Konfiguration

### Lambda Umgebungsvariablen (automatisch via Terraform)

| Variable | Beschreibung | Standard |
|----------|-------------|----------|
| `QM_QUOTA_TABLE` | DynamoDB Tabellennamen | `qm-quotalog` |
| `QM_ALERT_TOPIC_ARN` | SNS Topic für Alerts | (automatisch) |
| `QM_ALERT_THRESHOLD` | Utilization % für Alerts | 80 |

### Terraform Variablen

| Variable | Beschreibung | Standard |
|----------|-------------|----------|
| `tags` | Tags für alle Ressourcen | `{}` |
| `alert_threshold_pct` | Schwellwert für Alerts | 80 |
| `alert_email` | E-Mail für SNS Subscription | `` |

## Nutzung

### Lokal testen mit BA-Profil

```bash
export AWS_PROFILE=BA
export QM_ALERT_THRESHOLD=75  # Optional
python3 src/main.py
```

### Lambda manuell triggern

```bash
aws lambda invoke \
  --function-name qm-quotacontroller \
  --profile BA \
  response.json

cat response.json
```

### CloudWatch Logs anschauen

```bash
aws logs tail /aws/lambda/qm-quotacontroller \
  --follow \
  --profile BA
```

## Datenmodell

### DynamoDB Tabelle: `qm-quotalog`

Partition Key: `PK` (String)  
Sort Key: `SK` (String)

**Beispiel:**
- PK: `QUOTA#123456789012#eu-central-1#quota#L-70015FFA`
- SK: `TS#2026-02-14T12:34:56Z`

**Attribute:**
- accountId, region, serviceCode, quotaCode, quotaName
- limitValue, usageValue, utilizationPct
- collectorType, dataSource, calculationMethod
- maxResourceType, maxResourceId, maxResourceMeta
- collectedAt, ttl (für automatisches Löschen)

## Erweiterungen

### Neue Service-Checks hinzufügen

1. Neues Modul in `src/qmchecks/<service>/` erstellen
2. Funktionen analog zu `ec2.py` implementieren
3. In `src/main.py` importieren und aufrufen

### Alert-Logik anpassen

Die `QuotaAlert` Klasse in `src/qmalerting/alerting.py` kann erweitert werden:
- Andere Notification-Kanäle (E-Mail, Slack, etc.)
- Unterschiedliche Schwellwerte pro Quota
- Historische Datenanalyse

## Troubleshooting

### Lambda Timeout
Erhöhen Sie `timeout` und `memory_size` in `deployment/main.tf`.

### IAM Berechtigungen
Prüfen Sie die Inline-Policies in `deployment/main.tf`:
- `lambda_service_quotas`: Service Quotas API Zugriff
- `lambda_ec2`: EC2 API Zugriff
- `lambda_dynamodb`: DynamoDB Zugriff
- `lambda_sns`: SNS Publish Zugriff

### Layer-Abhängigkeiten
Der Layer wird automatisch gebaut mit `pip install -r requirements.txt`. Falls Fehler auftreten:

```bash
cd deployment
terraform apply -var-file="terraform.tfvars" -auto-approve
```

## Requirements

Siehe `requirements.txt`:
- boto3 >= 1.42.0 (für Service Quotas API)
- reportlab >= 3.2.4

## Lizenz

Internal Project

Pro Quota werden (falls vorhanden) auch die vollständigen Usage-Metric-Details (`Namespace`, `MetricName`, Dimensionen, Statistik-Empfehlung) ausgegeben und in die CSV übernommen. Die AWS-Credentials werden – wie bei der AWS CLI – per Umgebung bzw. Profil geladen. Das Skript respektiert außerdem `AWS_MAX_ATTEMPTS`/`AWS_RETRY_MODE`.

## Lizenz

- Frei verwendbar (keine Garantie).
