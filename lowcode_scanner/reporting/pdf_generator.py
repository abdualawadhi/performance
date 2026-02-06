"""
PDF Report Generator using ReportLab for Low-Code Performance Scanner.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)


class PDFReportGenerator:
    """Generates professional PDF reports for performance scans."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom styles for the PDF report."""
        self.styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                spaceAfter=20,
                alignment=1,  # Center
                textColor=colors.hexColor("#4A90E2"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=18,
                spaceBefore=15,
                spaceAfter=10,
                textColor=colors.hexColor("#333333"),
                borderPadding=5,
                borderWidth=0,
                leftIndent=0,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="MetricLabel",
                parent=self.styles["Normal"],
                fontSize=12,
                fontWeight="Bold",
            )
        )

    def generate(self, result, url: str, session_name: str, output_path: str) -> str:
        """Generate a PDF report from scan results."""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []

        # Header
        story.append(
            Paragraph(f"Performance Analysis Report", self.styles["ReportTitle"])
        )
        story.append(Paragraph(f"URL: {url}", self.styles["Normal"]))
        story.append(
            Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                self.styles["Normal"],
            )
        )
        story.append(Paragraph(f"Session: {session_name}", self.styles["Normal"]))
        story.append(Spacer(1, 0.25 * inch))

        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles["SectionHeader"]))
        overall_score = getattr(result.performance_matrix, "overall_score", 0)
        score_color = (
            colors.green
            if overall_score >= 90
            else colors.orange if overall_score >= 70 else colors.red
        )

        summary_data = [
            [
                Paragraph("<b>Overall Performance Score:</b>", self.styles["Normal"]),
                Paragraph(
                    f"<font color='{score_color}'>{overall_score:.1f}/100</font>",
                    self.styles["Normal"],
                ),
            ],
            [
                Paragraph("<b>Platform Detected:</b>", self.styles["Normal"]),
                Paragraph(
                    str(getattr(result, "platform", "Generic")).title(),
                    self.styles["Normal"],
                ),
            ],
        ]

        t = Table(summary_data, colWidths=[2.5 * inch, 3.5 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 0.25 * inch))

        # Performance Matrix
        story.append(
            Paragraph("Detailed Performance Matrix", self.styles["SectionHeader"])
        )

        rows = getattr(result.performance_matrix, "rows", [])
        if rows:
            matrix_data = [["Scenario", "Score", "Load Time", "Memory", "LCP"]]
            for row in rows:
                matrix_data.append(
                    [
                        getattr(row.scenario, "display_name", str(row.scenario)),
                        f"{getattr(row, 'performance_score', 0):.1f}",
                        f"{getattr(row, 'load_time_s', 0):.2f}s",
                        f"{getattr(row, 'memory_usage_max_mb', 0):.1f} MB",
                        f"{getattr(row, 'largest_contentful_paint_ms', 0):.0f}ms",
                    ]
                )

            mt = Table(matrix_data, hAlign="LEFT")
            mt.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.hexColor("#4A90E2")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ]
                )
            )
            story.append(mt)
        else:
            story.append(
                Paragraph("No scenario data available.", self.styles["Normal"])
            )

        story.append(Spacer(1, 0.25 * inch))

        # Observations
        story.append(Paragraph("Key Observations", self.styles["SectionHeader"]))
        unique_obs = []
        for row in rows:
            for obs in getattr(row, "key_observations", []):
                if obs not in unique_obs:
                    unique_obs.append(obs)

        if unique_obs:
            for obs in unique_obs:
                story.append(Paragraph(f"• {obs}", self.styles["Normal"]))
        else:
            story.append(
                Paragraph("No specific observations noted.", self.styles["Normal"])
            )

        # Build PDF
        doc.build(story)
        return output_path
