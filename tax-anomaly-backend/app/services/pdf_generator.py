"""PDF report generation for tax anomaly analysis."""

import io
from datetime import datetime, timezone

from fpdf import FPDF

from app.models.schemas import AnalysisResult, SeverityLevel, ComparisonResult


class TaxReportPDF(FPDF):
    """Custom PDF class for tax anomaly reports."""

    def header(self) -> None:
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Tax Anomaly Detection Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 9)
        self.cell(
            0, 6,
            f"Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y %H:%M UTC')}",
            new_x="LMARGIN", new_y="NEXT", align="C",
        )
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


SEVERITY_COLORS: dict[SeverityLevel, tuple[int, int, int]] = {
    SeverityLevel.CRITICAL: (220, 38, 38),
    SeverityLevel.HIGH: (234, 88, 12),
    SeverityLevel.MEDIUM: (202, 138, 4),
    SeverityLevel.LOW: (22, 163, 74),
}


def generate_analysis_pdf(
    result: AnalysisResult,
    comparison: ComparisonResult | None = None,
) -> bytes:
    """Generate a PDF report for an analysis result."""
    pdf = TaxReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Client info
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Client Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Client ID: {result.client_id}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Tax Year: {result.tax_year}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(
        0, 6,
        f"Overall Risk Score: {result.risk_score:.0f} / 100",
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.cell(
        0, 6,
        f"Total Anomalies Found: {result.total_anomalies}",
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5, result.summary)
    pdf.ln(6)

    # Anomalies
    if result.anomalies:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Flagged Items", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        for i, anomaly in enumerate(result.anomalies, 1):
            color = SEVERITY_COLORS.get(anomaly.severity, (100, 100, 100))

            pdf.set_fill_color(*color)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(
                0, 7,
                f"  #{i}  [{anomaly.severity.value.upper()}]  "
                f"Score: {anomaly.severity_score:.0f}/100  |  "
                f"Type: {anomaly.anomaly_type.value.replace('_', ' ').title()}",
                new_x="LMARGIN", new_y="NEXT", fill=True,
            )

            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 9)
            pdf.ln(2)
            pdf.multi_cell(0, 5, f"Description: {anomaly.description}")
            pdf.cell(
                0, 5,
                f"Expected Range: {anomaly.expected_range}",
                new_x="LMARGIN", new_y="NEXT",
            )
            pdf.set_font("Helvetica", "I", 9)
            pdf.multi_cell(0, 5, f"Recommendation: {anomaly.recommendation}")
            pdf.ln(4)

    # Prior year comparison
    if comparison:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(
            0, 8,
            f"Prior Year Comparison ({comparison.prior_year} vs {comparison.current_year})",
            new_x="LMARGIN", new_y="NEXT",
        )
        pdf.ln(2)

        # Table header
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(50, 7, "Category", border=1, fill=True)
        pdf.cell(35, 7, f"{comparison.prior_year}", border=1, fill=True, align="R")
        pdf.cell(35, 7, f"{comparison.current_year}", border=1, fill=True, align="R")
        pdf.cell(30, 7, "Change", border=1, fill=True, align="R")
        pdf.cell(25, 7, "% Change", border=1, fill=True, align="R")
        pdf.ln()

        pdf.set_font("Helvetica", "", 9)
        for comp in comparison.comparisons:
            if comp.is_significant:
                pdf.set_text_color(220, 38, 38)
                pdf.set_font("Helvetica", "B", 9)
            else:
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", "", 9)

            pdf.cell(50, 6, comp.field[:25], border=1)
            pdf.cell(35, 6, f"${comp.prior_year:,.0f}", border=1, align="R")
            pdf.cell(35, 6, f"${comp.current_year:,.0f}", border=1, align="R")

            sign = "+" if comp.change_amount >= 0 else "-"
            pdf.cell(30, 6, f"{sign}${abs(comp.change_amount):,.0f}", border=1, align="R")
            pdf.cell(
                25, 6,
                f"{sign}{comp.change_percent:.1f}%",
                border=1, align="R",
            )
            pdf.ln()

        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(
            0, 6,
            f"Significant changes (>{25}% YoY): {comparison.significant_changes}",
            new_x="LMARGIN", new_y="NEXT",
        )

    # Disclaimer
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(
        0, 4,
        "DISCLAIMER: This report is generated by an AI-powered anomaly detection system "
        "and is intended for informational purposes only. It does not constitute tax advice. "
        "All flagged items should be reviewed by a qualified tax professional before taking action.",
    )

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
