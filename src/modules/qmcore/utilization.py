"""Read complete AWS Service Quotas utilization reports without partial results."""


class ReportPending(RuntimeError):
    """The same report must be polled again; do not start a replacement."""


def read_report(client, report_id):
    records, tokens = [], set()
    token = None
    generated_at = total = None
    while True:
        kwargs = {'ReportId': report_id, 'MaxResults': 1000}
        if token:
            kwargs['NextToken'] = token
        page = client.get_quota_utilization_report(**kwargs)
        if page.get('ReportId') != report_id:
            raise RuntimeError('AWS returned a different utilization report identity')
        status = page.get('Status')
        if status in {'PENDING', 'IN_PROGRESS'}:
            raise ReportPending(f'Report {report_id} is {status}')
        if status != 'COMPLETED' or page.get('ErrorCode') or page.get('ErrorMessage'):
            raise RuntimeError(f"Utilization report failed: {status}: {page.get('ErrorCode')}: {page.get('ErrorMessage')}")
        if not isinstance(page.get('Quotas'), list):
            raise RuntimeError('Utilization report has no quota list')
        if not isinstance(page.get('TotalCount'), int) or isinstance(page['TotalCount'], bool) or page['TotalCount'] < 0:
            raise RuntimeError('Utilization report has no valid total count')
        if page.get('GeneratedAt') is None:
            raise RuntimeError('Utilization report has no generation timestamp')
        if total is None:
            total, generated_at = page['TotalCount'], page['GeneratedAt']
        elif total != page['TotalCount'] or generated_at != page['GeneratedAt']:
            raise RuntimeError('Utilization report changed during pagination')
        records.extend(page['Quotas'])
        token = page.get('NextToken')
        if not token:
            break
        if token in tokens:
            raise RuntimeError('Repeated utilization report pagination token')
        tokens.add(token)
    if len(records) != total:
        raise RuntimeError(f'Incomplete utilization report: received {len(records)} of {total}')
    return {'ReportId': report_id, 'Status': 'COMPLETED', 'GeneratedAt': generated_at,
            'TotalCount': total, 'Quotas': records}
