from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import get_settings
from app.core.timezone import now_local
from app.models.stoppage import StoppageRecord


NAVY = colors.HexColor("#1B3A4B")
LIGHT = colors.HexColor("#EEF2F6")
ACCENT = colors.HexColor("#C45C26")


def _header_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, landscape(A4)[1] - 16 * mm, landscape(A4)[0], 16 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(15 * mm, landscape(A4)[1] - 10 * mm, get_settings().app_name)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(
        landscape(A4)[0] - 15 * mm,
        8 * mm,
        f"Page {doc.page}  |  Generated {now_local().strftime('%d %b %Y %I:%M %p')} IST",
    )
    canvas.restoreState()


def _table(data: list[list], col_widths=None) -> Table:
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D0D5DD")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def build_pdf(
    records: list[StoppageRecord],
    summaries: dict,
    kpis: dict,
    filters_text: str,
) -> bytes:
    settings = get_settings()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=22 * mm,
        bottomMargin=14 * mm,
        title="Downtime Report",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleLocal", parent=styles["Title"], fontSize=16, textColor=NAVY, alignment=TA_LEFT)
    heading = ParagraphStyle("H", parent=styles["Heading2"], textColor=NAVY, fontSize=12, spaceBefore=8)
    body = ParagraphStyle("B", parent=styles["Normal"], fontSize=9, leading=12)

    story = [
        Paragraph("Downtime Report", title),
        Paragraph(settings.company_name, body),
        Paragraph(f"Filters: {filters_text}", body),
        Paragraph(
            f"Generated: {now_local().strftime('%d %b %Y %I:%M %p')} (Asia/Kolkata)",
            body,
        ),
        Spacer(1, 8),
        Paragraph("KPI summary", heading),
        _table(
            [
                ["Metric", "Value"],
                ["Total downtime", f"{kpis['total_downtime']} min"],
                ["Stoppage entries", str(kpis["total_entries"])],
                ["Current production date", kpis["production_date"]],
                ["Current shift", kpis["shift_code"]],
            ],
            col_widths=[90 * mm, 80 * mm],
        ),
    ]

    def summary_section(title_text: str, rows: list[tuple]) -> None:
        story.append(Paragraph(title_text, heading))
        data = [["Name", "Downtime (min)", "Entries"]]
        data.extend([[name, f"{float(down):.0f}", str(count)] for name, down, count in rows[:30]])
        if not rows:
            data.append(["No stoppage recorded", "0", "0"])
        story.append(_table(data, col_widths=[110 * mm, 40 * mm, 30 * mm]))

    summary_section("Machine summary", summaries["machines"])
    summary_section("Reason summary", summaries["reasons"])
    summary_section("Shift summary", summaries["shifts"])
    summary_section("Daily summary", summaries["daily"])

    story.append(PageBreak())
    story.append(Paragraph("Detailed records", heading))
    detail = [["Production Date", "Shift", "Supervisor", "Machine", "Reason", "Duration", "Details", "Remarks"]]
    for record in records[:2000]:
        detail.append(
            [
                record.production_date.strftime("%d %b %Y"),
                record.shift.code,
                record.supervisor.name,
                record.machine.code,
                record.reason.name,
                f"{float(record.duration_minutes):.0f} min",
                (record.details or "")[:80],
                (record.remarks or "")[:80],
            ]
        )
    if len(detail) == 1:
        detail.append(["No stoppage recorded for the selected filters.", "", "", "", "", "", "", ""])
    story.append(_table(detail, col_widths=[28 * mm, 16 * mm, 28 * mm, 20 * mm, 42 * mm, 22 * mm, 50 * mm, 50 * mm]))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buffer.getvalue()
