#!/usr/bin/env bash
# Restore to a new, explicitly named drill table. This intentionally writes AWS resources.
set -euo pipefail
source_table=''
target_table=''
region=''
restore_time=''
execute=false
while (($#)); do
  case "$1" in
    --source) source_table=${2:?}; shift 2 ;;
    --target) target_table=${2:?}; shift 2 ;;
    --region) region=${2:?}; shift 2 ;;
    --restore-time) restore_time=${2:?}; shift 2 ;;
    --execute) execute=true; shift ;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
[[ -n "$source_table" && -n "$target_table" && -n "$region" && -n "$restore_time" ]] || {
  printf 'Required: --source TABLE --target qm-restore-drill-NAME --region REGION --restore-time ISO [--execute]\n' >&2
  exit 2
}
[[ "$target_table" == qm-restore-drill-* && "$source_table" != "$target_table" ]] || {
  printf 'Target must be distinct and start with qm-restore-drill-\n' >&2
  exit 2
}
if [[ "$execute" != true ]]; then
  printf 'Plan: restore %s in %s to %s at %s. Add --execute to create this table.\n' \
    "$source_table" "$region" "$target_table" "$restore_time"
  exit 0
fi
if aws dynamodb describe-table --table-name "$target_table" --region "$region" \
    --query 'Table.TableStatus' --output text >/dev/null 2>&1; then
  printf 'Target table already exists; choose a new drill table name.\n' >&2
  exit 1
fi
aws dynamodb restore-table-to-point-in-time --source-table-name "$source_table" \
  --target-table-name "$target_table" --restore-date-time "$restore_time" \
  --region "$region" --no-cli-pager
aws dynamodb wait table-exists --table-name "$target_table" --region "$region"
aws dynamodb describe-table --table-name "$target_table" --region "$region" \
  --query 'Table.{Name:TableName,Status:TableStatus,Items:ItemCount,ARN:TableArn}'
printf 'Drill table retained. Inspect it, then remove only this exact qm-restore-drill-* table after review.\n'
