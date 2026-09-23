#!/usr/bin/env python3
"""Fail when a package's line coverage falls below its recorded baseline.

The baseline is the measured figure rounded down, not a target. It protects
what the suite already reaches and is raised deliberately, the same way
`quota_coverage.py --baseline` protects the quota figures.

One number over `src` would say nothing: `src/modules/qmchecks` holds 12,240 of
the 13,447 statements, so `qmcore` could fall from 92% to 60% and move the total
by a point and a half. Each package therefore carries its own floor.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

PACKAGES = ('src/modules/qmcore', 'src/modules/qmchecks', 'src/modules/qmdb',
            'src/modules/qmalerting', 'src/functions')


def measure(report: str) -> dict[str, float]:
    """Percent of statements covered, per package, from a coverage JSON report."""
    files = json.loads(Path(report).read_text(encoding='utf-8'))['files']
    totals: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
    for name, entry in files.items():
        name = name.replace('\\', '/')
        package = next((p for p in PACKAGES if name.startswith(p)), None)
        if package is None:
            continue
        totals[package][0] += entry['summary']['covered_lines']
        totals[package][1] += entry['summary']['num_statements']
    return {package: round(100 * covered / statements, 2)
            for package, (covered, statements) in totals.items() if statements}


def compare_baseline(current: dict[str, float], path: str) -> list[str]:
    """Return one message per package that fell below its baseline."""
    baseline = json.loads(Path(path).read_text(encoding='utf-8'))
    failures = []
    for package, floor in sorted(baseline.items()):
        measured = current.get(package)
        if measured is None:
            failures.append(f'{package} is in the baseline but was not measured')
        elif measured < floor:
            failures.append(f'{package} fell from {floor}% to {measured}%')
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Zeilenabdeckung je Paket gegen eine Baseline prüfen')
    parser.add_argument('report', help='coverage-JSON aus pytest --cov-report=json')
    parser.add_argument('--baseline', help='Baseline-JSON; Exit 1 bei Rückschritt')
    parser.add_argument('--update-baseline', metavar='PATH',
                        help='Gemessene Werte abgerundet als Baseline schreiben')
    arguments = parser.parse_args()

    current = measure(arguments.report)
    for package in PACKAGES:
        if package in current:
            print(f'{package:26s} {current[package]:6.2f}%')

    if arguments.update_baseline:
        floors = {package: int(value) for package, value in sorted(current.items())}
        Path(arguments.update_baseline).write_text(
            json.dumps(floors, indent=2) + '\n', encoding='utf-8')
        print(f'baseline written to {arguments.update_baseline}')

    if arguments.baseline:
        failures = compare_baseline(current, arguments.baseline)
        for failure in failures:
            print(f'coverage regression: {failure}')
        return 1 if failures else 0
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
