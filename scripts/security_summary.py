"""Fail closed on scanner findings without printing potential secret material."""
import json
import sys


def summarize(report):
    findings = []
    for result in report.get('Results', []):
        for category in ('Vulnerabilities', 'Secrets', 'Misconfigurations'):
            for finding in result.get(category, []):
                if category == 'Misconfigurations' and finding.get('Status') != 'FAIL':
                    continue
                findings.append({'path': result['Target'], 'kind': category,
                                 'id': finding.get('VulnerabilityID') or finding.get('ID') or finding.get('RuleID'),
                                 'severity': finding.get('Severity'),
                                 'title': finding.get('Title')})
    return findings


if __name__ == '__main__':
    results = summarize(json.load(sys.stdin))
    print(json.dumps({'findings': results, 'count': len(results)}, indent=2))
    raise SystemExit(bool(results))
