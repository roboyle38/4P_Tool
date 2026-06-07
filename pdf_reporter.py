"""
pdf_reporter.py

Generates a PDF report from 4P assay analysis results.
Uses reportlab for PDF generation.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def generate_pdf(
    filepath, 
    A, B, C, D,      # 4PL parameters
    r2, sse, residual_sd,  # model diagnostics
    lloq, uloq,      # LOQ estimates
    unknown_table_dict,    # formatted unknown summary
    calibration_table_dict, # formatted calibrator summary
    unknown_groups,        # raw unknown replicates (for appendix)
    calibration_groups,    # raw calibrator replicates (for appendix)
    sample_outliers,       # unknown outlier flags
    cal_outliers,          # calibrator outlier flags
    figure,                # matplotlib figure for the plot
    source_filename):
        
    """
    Generate a PDF report from 4P assay analysis results.
    """
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=1*inch, bottomMargin=1*inch,)

    styles = getSampleStyleSheet()
    story = []

    # -----------------------------------------------------------------------
    # 1) Title and metadata
    # -----------------------------------------------------------------------
    story.append(Paragraph("4P Assay Tool", styles["Title"]))
    story.append(Paragraph("Assay Analysis Report", styles["Heading2"]))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Source file: {source_filename}", styles["Normal"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 0.3*inch))


# -----------------------------------------------------------------------
    # 2) Model parameters table
    # -----------------------------------------------------------------------
    story.append(Paragraph("Model Parameters", styles["Heading2"]))
    story.append(Spacer(1, 0.1*inch))

    params_data = [
        ["Parameter", "Value"],
        ["A (Low)", round(A, 4)],
        ["B (Slope)", round(B, 4)],
        ["C (EC50)", round(C, 4)],
        ["D (High)", round(D, 4)],
        ["R2", round(r2, 4)],
        ["SSE", round(sse, 4)],
        ["Residual SD", round(residual_sd, 4)],
        ["Estimated LLOQ", lloq if lloq is not None else "---"],
        ["Estimated ULOQ", uloq if uloq is not None else "---"],
    ]

    params_table = Table(params_data, colWidths=[3*inch, 2*inch])
    params_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    story.append(params_table)
    story.append(Spacer(1, 0.3*inch))



    # -----------------------------------------------------------------------
    # 3) Calibration curve plot
    # -----------------------------------------------------------------------
    story.append(Paragraph("Calibration Curve", styles["Heading2"]))
    story.append(Spacer(1, 0.1*inch))

    # Save figure to a memory buffer
    buf = io.BytesIO()
    figure.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)

    # Add image to story
    plot_image = Image(buf, width=5*inch, height=3.5*inch)
    story.append(plot_image)
    story.append(Spacer(1, 0.3*inch))

# -----------------------------------------------------------------------
    # 4) Unknown samples table
    # -----------------------------------------------------------------------
    story.append(Paragraph("Unknown Samples", styles["Heading2"]))
    story.append(Spacer(1, 0.1*inch))

    # Build table data from table dict
    unknown_data = [unknown_table_dict["headers"]]
    for row in unknown_table_dict["rows"]:
        unknown_data.append([str(v) for v in row])

    unknown_tab = Table(unknown_data, repeatRows=1)
    unknown_tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    story.append(unknown_tab)
    story.append(Spacer(1, 0.3*inch))

# -----------------------------------------------------------------------
    # 5) Calibrators table
    # -----------------------------------------------------------------------
    story.append(Paragraph("Calibrators", styles["Heading2"]))
    story.append(Spacer(1, 0.1*inch))

    cal_data = [calibration_table_dict["headers"]]
    for row in calibration_table_dict["rows"]:
        cal_data.append([str(v) for v in row])

    cal_tab = Table(cal_data, repeatRows=1)
    cal_tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    story.append(cal_tab)
    story.append(PageBreak())

# -----------------------------------------------------------------------
    # 6) Appendix - Raw Data
    # -----------------------------------------------------------------------
    story.append(Paragraph("Appendix — Raw Data", styles["Title"]))
    story.append(Spacer(1, 0.2*inch))

    # --- Unknown sample raw replicates ---
    story.append(Paragraph("Unknown Sample Raw Replicates", styles["Heading2"]))
    story.append(Spacer(1, 0.1*inch))

    unk_raw_data = [["Sample ID", "Replicate", "Signal", "Outlier"]]
    for sample_id, info in unknown_groups.items():
        flagged = sample_outliers.get(sample_id, [])
        for i, signal in enumerate(info["signals"]):
            is_outlier = "YES" if signal in flagged else ""
            unk_raw_data.append([
                sample_id,
                i + 1,
                round(signal, 4),
                is_outlier,
            ])

    unk_raw_tab = Table(unk_raw_data, repeatRows=1)
    unk_raw_tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    story.append(unk_raw_tab)
    story.append(Spacer(1, 0.3*inch))

    # --- Calibrator raw replicates ---
    story.append(Paragraph("Calibrator Raw Replicates", styles["Heading2"]))
    story.append(Spacer(1, 0.1*inch))

    cal_raw_data = [["Calibrator ID", "Level", "Replicate", "Signal", "Outlier"]]
    for calib_id, info in calibration_groups.items():
        flagged = cal_outliers.get(calib_id, {}).get("outliers", [])
        for i, signal in enumerate(info["signals"]):
            is_outlier = "YES" if signal in flagged else ""
            cal_raw_data.append([
                calib_id,
                info["concentration"],
                i + 1,
                round(signal, 4),
                is_outlier,
            ])

    cal_raw_tab = Table(cal_raw_data, repeatRows=1)
    cal_raw_tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    story.append(cal_raw_tab)



    # -----------------------------------------------------------------------
    # Build PDF
    # -----------------------------------------------------------------------
    doc.build(story)
