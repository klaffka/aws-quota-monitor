#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# AWS Service Quotas Exporter
# - Exportiert Default- und Applied-Quotas für alle (oder angegebene) Regionen
# - Erzeugt: service-quotas-<timestamp>.json  und  service-quotas-<timestamp>.csv
#
# Usage:
#   ./export-aws-quotas.sh [--profile <name>] [--regions "eu-central-1,eu-west-1"]
#
# Beispiele:
#   ./export-aws-quotas.sh
#   ./export-aws-quotas.sh --profile prod
#   ./export-aws-quotas.sh --profile prod --regions "eu-central-1,eu-west-1"
# -----------------------------------------------------------------------------

PROFILE_OPT=""
REGIONS_CSV=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE_OPT="--profile $2"
      shift 2
      ;;
    --regions)
      REGIONS_CSV="$2"
      shift 2
      ;;
    *)
      echo "Unbekannte Option: $1" >&2
      exit 1
      ;;
  esac
done

# Mehr Robustheit gegen API-Limits
export AWS_RETRY_MODE=adaptive
export AWS_MAX_ATTEMPTS=10

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
out_json="service-quotas-${timestamp}.json"
out_csv="service-quotas-${timestamp}.csv"
tmp_jsonl="$(mktemp)"
trap 'rm -f "$tmp_jsonl"' EXIT

echo "→ Ermittele Regionen..."
if [[ -z "$REGIONS_CSV" ]]; then
  # Standard: nur eu-central-1, damit das Skript nicht ewig läuft.
  echo "  Keine Regionen angegeben — verwende Standardregion: eu-central-1"
  REGIONS=("eu-central-1")
else
  IFS=',' read -r -a REGIONS <<< "$REGIONS_CSV"
fi

# Hilfsfunktion: paginierte Abfrage (liefert .[] JSON-Objekte der gewünschten Liste)
# Args: region, serviceCode, scope(default|applied)
fetch_quotas() {
  local region="$1"
  local svc="$2"
  local scope="$3"

  local cmd="aws $PROFILE_OPT service-quotas"
  local subcmd=""
  local key=""
  if [[ "$scope" == "default" ]]; then
    subcmd="list-aws-default-service-quotas"
    key="Quotas"
  else
    subcmd="list-service-quotas"
    key="Quotas"
  fi

  local next=""
  while :; do
    if [[ -n "$next" ]]; then
      resp=$($cmd "$subcmd" --service-code "$svc" --region "$region" --page-size 100 --starting-token "$next" --output json || true)
    else
      resp=$($cmd "$subcmd" --service-code "$svc" --region "$region" --page-size 100 --output json || true)
    fi

    # Falls Service kein Ergebnis liefert (oder nicht unterstützt wird), abbrechen
    if [[ -z "${resp:-}" || "${resp}" == "null" ]]; then
      break
    fi

    # Quotas extrahieren (einzeln parsen, usage-Metric prüfen und erweitern)
    echo "$resp" | jq -c --arg key "$key" '(.[ $key ] // [])[]' | while IFS= read -r quota; do
      quotaCode=$(echo "$quota" | jq -r '.QuotaCode // empty')
      quotaName=$(echo "$quota" | jq -r '.QuotaName // empty')
      # Prüfe asynchron/sequentiell auf vorhandenes Usage-Metric (robust gegenüber Fehlern)
      hasMetric=$(check_usage_metric "$region" "$svc" "$quotaCode" "$quotaName" || echo false)

      # Baue das erweiterte Objekt und schreibe es in die temporäre Datei
      echo "$quota" | jq -c --arg region "$region" --arg scope "$scope" --arg svc "$svc" --arg hasMetric "$hasMetric" '
        {
          region: $region,
          scope: $scope,
          serviceCode: $svc,
          serviceName: (.ServiceName // null),
          quotaCode: (.QuotaCode // null),
          quotaName: (.QuotaName // null),
          quotaArn: (.QuotaArn // null),
          unit: (.Unit // null),
          adjustable: (.Adjustable // false),
          globalQuota: (.GlobalQuota // false),
          value: (.Value // null),
          hasUsageMetric: ( $hasMetric == "true" )
        }' >> "$tmp_jsonl"
    done

    # Pagination
    next=$(echo "$resp" | jq -r '.NextToken // empty')
    [[ -z "$next" ]] && break
  done
}

# Prüft, ob für eine gegebene Quota ein CloudWatch-Metric existiert (versucht einige Namensräume/namen)
check_usage_metric() {
  local region="$1"
  local svc="$2"
  local quotaCode="$3"
  local quotaName="$4"

  # Kandidaten für Metric-Namen / -Namespaces (anpassbar)
  local candidates=("$quotaCode" "$quotaName" "$svc")
  local namespaces=("AWS/ServiceQuotas" "AWS/Usage" "")

  for ns in "${namespaces[@]}"; do
    for m in "${candidates[@]}"; do
      [[ -z "$m" || "$m" == "null" ]] && continue
      # Versuche list-metrics; leere/nicht vorhandene Antworten werden ignoriert
      if [[ -n "$ns" ]]; then
        resp=$(aws $PROFILE_OPT cloudwatch list-metrics --region "$region" --namespace "$ns" --metric-name "$m" --output json 2>/dev/null || echo '{}')
      else
        resp=$(aws $PROFILE_OPT cloudwatch list-metrics --region "$region" --metric-name "$m" --output json 2>/dev/null || echo '{}')
      fi
      if echo "$resp" | jq -e '.Metrics | length > 0' >/dev/null 2>&1; then
        echo "true"
        return
      fi
    done
  done
  echo "false"
}

echo "→ Sammle Services je Region & lese Default/Applied Quotas..."
for region in "${REGIONS[@]}"; do
  echo "  - Region: $region"
  # Services der Region
  services_json=$(aws $PROFILE_OPT service-quotas list-services --region "$region" --output json || echo '{}')
  # Robust gegen leere/fehlerhafte Antworten
  # mapfile ist auf macOS nicht verfügbar; benutze while-read, um das Array zu befüllen.
  SVCS=()
  while IFS= read -r svc; do
    [[ -n "$svc" ]] && SVCS+=("$svc")
  done < <(echo "$services_json" | jq -r '.Services[]?.ServiceCode' 2>/dev/null || true)

  # Falls leer, weiter
  if [[ ${#SVCS[@]} -eq 0 ]]; then
    echo "    (Keine Services gefunden oder Service-Quotas in dieser Region nicht verfügbar.)"
    continue
  fi

  for svc in "${SVCS[@]}"; do
    # Default-Quotas
    fetch_quotas "$region" "$svc" "default"
    # Applied-Quotas
    fetch_quotas "$region" "$svc" "applied"
  done
done

echo "→ Schreibe JSON-Gesamtausgabe: $out_json"
jq -s '.' "$tmp_jsonl" > "$out_json"

echo "→ Erzeuge kombinierte CSV (Default + Applied in einer Zeile): $out_csv"
# Wir mappen je Region/ServiceCode/QuotaCode und fügen default/applied zusammen
jq -r '
  # Lade alle Datensätze
  . as $all
  | $all
  | group_by({region, serviceCode, quotaCode})
  | map({
      region:      (.[0].region),
      serviceCode: (.[0].serviceCode),
      serviceName: (.[0].serviceName),
      quotaCode:   (.[0].quotaCode),
      quotaName:   (.[0].quotaName),
      unit:        (.[0].unit),
      adjustable:  (.[0].adjustable),
      globalQuota: (.[0].globalQuota),
      defaultValue: ( (.[]
        | select(.scope=="default")
        | .value) // null ),
      appliedValue: ( (.[]
        | select(.scope=="applied")
        | .value) // null )
    })
  # Header + Zeilen ausgeben
  | (["region","serviceCode","serviceName","quotaCode","quotaName","unit","adjustable","globalQuota","defaultValue","appliedValue","hasUsageMetric"]
     , (.[] | [
        .region,
        .serviceCode,
        (.serviceName // ""),
        .quotaCode,
        (.quotaName // ""),
        (.unit // ""),
        (if .adjustable then "true" else "false" end),
        (if .globalQuota then "true" else "false" end),
        (if .defaultValue==null then "" else (.defaultValue|tostring) end),
        (if .appliedValue==null then "" else (.appliedValue|tostring) end),
        (if .hasUsageMetric then "true" else "false" end)
      ]))
  | @csv
' "$out_json" > "$out_csv"

echo "Fertig ✅"
echo "JSON: $out_json"
echo "CSV : $out_csv"
