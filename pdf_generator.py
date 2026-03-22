import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO


# ── Color Palette ──────────────────────────────────────────────
PURPLE      = colors.HexColor('#7C3AED')
DARK_PURPLE = colors.HexColor('#5B21B6')
LIGHT_BG    = colors.HexColor('#F5F3FF')
DARK_BG     = colors.HexColor('#1E1B2E')
GRAY_TEXT   = colors.HexColor('#6B7280')
DARK_TEXT   = colors.HexColor('#1F2937')
WHITE       = colors.white
ACCENT_TEAL = colors.HexColor('#06B6D4')


def _sanitize(text: str) -> str:
    """Escape XML and convert markdown bold to ReportLab tags."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = text.replace('*', '')
    text = re.sub(r'^- ', '• ', text)
    return text


def _build_styles():
    """Create a modern, professional style set."""
    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        'ModernTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=28,
        textColor=PURPLE, spaceAfter=4, alignment=TA_CENTER
    )
    subtitle = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11,
        textColor=GRAY_TEXT, spaceAfter=20, alignment=TA_CENTER
    )
    section_header = ParagraphStyle(
        'SectionHead', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=14,
        textColor=WHITE, backColor=PURPLE,
        spaceBefore=24, spaceAfter=14,
        borderPadding=(8, 12, 8, 12), leading=20
    )
    query_style = ParagraphStyle(
        'QueryBox', parent=styles['Normal'],
        fontName='Helvetica-BoldOblique', fontSize=12,
        textColor=DARK_PURPLE, backColor=LIGHT_BG,
        spaceBefore=12, spaceAfter=12,
        borderPadding=(10, 12, 10, 12), leading=18
    )
    body = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10.5,
        textColor=DARK_TEXT, spaceAfter=10, leading=16
    )
    code_block = ParagraphStyle(
        'Code', parent=styles['Code'],
        fontName='Courier', fontSize=8,
        textColor=colors.HexColor('#A78BFA'),
        backColor=DARK_BG,
        borderPadding=(10, 12, 10, 12),
        spaceBefore=10, spaceAfter=16, leading=12
    )
    footer = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8,
        textColor=GRAY_TEXT, alignment=TA_CENTER
    )
    return {
        'title': title, 'subtitle': subtitle,
        'section': section_header, 'query': query_style,
        'body': body, 'code': code_block, 'footer': footer
    }


def generate_pdf_report(messages: list, output_path: str = "Data_Detective_Report.pdf"):
    """
    Generate a modern, multi-query PDF report from the full session history.

    Args:
        messages: List of dicts with keys: role, content, code (optional), chart (optional).
        output_path: Where to save the PDF.

    Returns:
        str: Absolute path to the generated PDF.
    """
    import plotly.io as pio

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch
    )
    s = _build_styles()
    story = []

    # ── Cover / Title ──────────────────────────────────────────
    story.append(Spacer(1, 0.6 * inch))
    story.append(Paragraph("Data Detective", s['title']))
    story.append(Paragraph("Autonomous Analysis Report", s['subtitle']))

    # Metadata line
    now = datetime.now().strftime("%B %d, %Y  •  %I:%M %p")
    total_queries = sum(1 for m in messages if m['role'] == 'user')
    meta_line = f"Generated on {now}  |  {total_queries} queries analyzed"
    story.append(Paragraph(meta_line, s['subtitle']))

    # Accent line
    story.append(HRFlowable(
        width="80%", thickness=2, color=PURPLE,
        spaceBefore=10, spaceAfter=20
    ))

    # ── Per-Query Sections ─────────────────────────────────────
    query_num = 0
    i = 0
    while i < len(messages):
        msg = messages[i]

        if msg['role'] == 'user':
            query_num += 1

            # Section header
            story.append(Paragraph(f"Query {query_num}", s['section']))
            story.append(Paragraph(
                f"Q: {_sanitize(msg['content'])}", s['query']
            ))

            # Look ahead for the assistant response
            if i + 1 < len(messages) and messages[i + 1]['role'] == 'assistant':
                asst = messages[i + 1]

                # Insights
                story.append(Spacer(1, 12))
                for line in asst['content'].split('\n'):
                    if line.strip():
                        story.append(Paragraph(_sanitize(line), s['body']))

                # Chart
                chart_json = asst.get('chart')
                if chart_json:
                    try:
                        fig = pio.from_json(chart_json)
                        img_bytes = pio.to_image(fig, format="png", width=700, height=420)
                        img_stream = BytesIO(img_bytes)
                        story.append(Spacer(1, 14))
                        story.append(Image(img_stream, width=460, height=276))
                        story.append(Spacer(1, 14))
                    except Exception as e:
                        story.append(Paragraph(
                            f"<i>Chart could not be embedded: {_sanitize(str(e))}</i>",
                            s['body']
                        ))

                # Code
                code = asst.get('code', '')
                if code:
                    story.append(Spacer(1, 6))
                    story.append(Paragraph("Generated Code", s['section']))
                    safe_code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    safe_code = safe_code.replace('\n', '<br/>')
                    story.append(Paragraph(safe_code, s['code']))

                i += 2  # Skip both user + assistant
            else:
                i += 1
        else:
            i += 1

        # Page break between queries for clean separation
        if query_num > 0 and i < len(messages):
            story.append(PageBreak())

    # ── Footer ─────────────────────────────────────────────────
    story.append(Spacer(1, 0.4 * inch))
    story.append(HRFlowable(
        width="100%", thickness=1, color=PURPLE,
        spaceBefore=10, spaceAfter=10
    ))
    story.append(Paragraph(
        "Powered by Autonomous Data Detective Agent  •  github.com/sk191",
        s['footer']
    ))

    doc.build(story)
    return os.path.abspath(output_path)
