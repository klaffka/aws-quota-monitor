import boto3
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure src/ is on sys.path before local imports when executed directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from qmdb.db import QuotaLogDb


class QuotaReport:
    def __init__(self, session):
        self.session = session
        self.client = session.client('service-quotas')

    def get_quota_report_ec2(self):
        quotas = []
        paginator = self.client.get_paginator('list_service_quotas')
        for page in paginator.paginate(ServiceCode='ec2'):
            for quota in page['Quotas']:
                quotas.append(quota)
        return quotas

    def ddb_get(self, item, key, default=None):
        """Extract DynamoDB attribute to python, supports resource-returned dicts."""
        if key not in item:
            return default
        v = item[key]
        if isinstance(v, dict) and any(k in v for k in ("S", "N", "NULL")):
            if "S" in v:
                return v["S"]
            if "N" in v:
                n = v["N"]
                return int(n) if n.isdigit() else float(n)
            if "NULL" in v and v["NULL"] is True:
                return default
            return default
        return v

    def severity(self, util_pct):
        if util_pct is None:
            return "UNKNOWN"
        if util_pct >= 90:
            return "CRITICAL"
        if util_pct >= 75:
            return "WARNING"
        return "OK"

    def build_quota_report(self, items, outfile="quota-report.pdf"):
        styles = getSampleStyleSheet()
        small = styles["BodyText"].clone("Small")
        small.fontSize = 7
        small.leading = 9
        doc = SimpleDocTemplate(
            outfile,
            pagesize=landscape(A4),
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        # Flatten items into rows
        rows = []
        for it in items:
            util = self.ddb_get(it, "utilizationPct", 0) or 0
            row = {
                "service": self.ddb_get(it, "serviceCode", ""),
                "quota": self.ddb_get(it, "quotaName", ""),
                "code": self.ddb_get(it, "quotaCode", ""),
                "scope": self.ddb_get(it, "scopeType", ""),
                "account": self.ddb_get(it, "accountId", ""),
                "region": self.ddb_get(it, "region", ""),
                "usage": self.ddb_get(it, "usageValue", 0),
                "limit": self.ddb_get(it, "limitValue", 0),
                "util": util,
                "sev": self.severity(util),
                "collectedAt": self.ddb_get(it, "collectedAt", ""),
                "source": self.ddb_get(it, "dataSource", ""),
                "calc": self.ddb_get(it, "calculationMethod", ""),
                "maxRes": self.ddb_get(it, "maxResourceId", "—") or "—",
            }
            rows.append(row)

        # Summary
        counts = {"CRITICAL": 0, "WARNING": 0, "OK": 0, "UNKNOWN": 0}
        for r in rows:
            counts[r["sev"]] = counts.get(r["sev"], 0) + 1

        # Sort by utilization desc for Top list
        top = sorted(rows, key=lambda r: (r["util"] if r["util"] is not None else -1), reverse=True)[:10]

        story = []
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        story.append(Paragraph("Cloud Quotas Report", styles["Title"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"GeneratedAt (UTC): {now}", styles["Normal"]))
        story.append(Spacer(1, 16))

        story.append(Paragraph("Executive Summary", styles["Heading1"]))
        summary_table = Table(
            [["Severity", "Count"],
            ["CRITICAL (>= 90%)", str(counts["CRITICAL"])],
            ["WARNING (>= 75%)", str(counts["WARNING"])],
            ["OK (< 75%)", str(counts["OK"])],
            ["UNKNOWN", str(counts["UNKNOWN"])],],
            colWidths=[180, 80]
        )
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN", (1,1), (1,-1), "RIGHT"),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 16))

        story.append(Paragraph("Top 10 by Utilization", styles["Heading2"]))
        top_table_data = [["Service", "Quota", "Code", "Region", "Usage/Limit", "Util %", "Severity"]]
        for r in top:
            top_table_data.append([
                Paragraph(str(r["service"]), small),
                Paragraph(str(r["quota"]), small),
                Paragraph(str(r["code"]), small),
                Paragraph(str(r["region"]), small),
                f'{r["usage"]}/{r["limit"]}',
                f'{r["util"]:.1f}',
                Paragraph(str(r["sev"]), small),
            ])
        # tuned widths to fit A4 landscape
        top_table = Table(top_table_data, colWidths=[70, 260, 70, 60, 90, 70, 60])
        top_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
        ]))
        story.append(top_table)

        story.append(PageBreak())
        story.append(Paragraph("Details", styles["Heading1"]))

        # Full detail table (you may want to paginate or split by service)
        detail_data = [["Service", "Quota", "Code", "Scope", "Account", "Region", "Usage", "Limit", "Util %", "CollectedAt", "Source", "Calc", "MaxRes"]]
        for r in sorted(rows, key=lambda x: (x["service"], x["quota"], x["region"])):
            detail_data.append([
                Paragraph(str(r["service"]), small),
                Paragraph(str(r["quota"]), small),
                Paragraph(str(r["code"]), small),
                Paragraph(str(r["scope"]), small),
                Paragraph(str(r["account"]), small),
                Paragraph(str(r["region"]), small),
                Paragraph(str(r["usage"]), small),
                Paragraph(str(r["limit"]), small),
                Paragraph(f'{r["util"]:.1f}', small),
                Paragraph(str(r["collectedAt"]), small),
                Paragraph(str(r["source"]), small),
                Paragraph(str(r["calc"]), small),
                Paragraph(str(r["maxRes"]), small),
            ])

        # let ReportLab auto-size to available width; small font to avoid overlap
        # widths tuned for landscape A4 (usable width ~770)
        detail_col_widths = [38, 140, 50, 58, 63, 48, 38, 38, 38, 72, 58, 58, 50]
        detail_table = Table(detail_data, repeatRows=1, colWidths=detail_col_widths)
        detail_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 6),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
        ]))
        story.append(detail_table)

        doc.build(story)

if __name__ == "__main__":
    session = boto3.Session(profile_name='BA')
    account_id = session.client('sts').get_caller_identity().get('Account')
    region = session.region_name or session.client('sts').meta.region_name
    client = session.client('service-quotas')
    db = QuotaLogDb(session=session, table_name='qm-quotalog')
    report = QuotaReport(session)
    current_quota = report.get_quota_report_ec2()
    items = []
    for quota in current_quota:
        pk = f"QUOTA#{account_id}#{region}#quota#{quota['QuotaCode']}"
        item = db.get_latest_quota_entry(pk)
        if item:
            items.append(item)
    report.build_quota_report(items, outfile="ec2-quota-report.pdf")
