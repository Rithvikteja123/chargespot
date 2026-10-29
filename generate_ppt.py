"""
ChargeSpot PowerPoint Generator
Produces a polished 10-slide presentation (16:9) with forest-green theme,
embedded project screenshots, diagrams, and speaker notes.
"""
import os, math
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.oxml.ns import qn
from lxml import etree
import copy

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
SS     = os.path.join(BASE, "report_screenshots")
OUT    = os.path.join(BASE, "docs", "ChargeSpot_Presentation.pptx")

SS_HOME     = os.path.join(SS, "01_home_dashboard.png")
SS_CARDS    = os.path.join(SS, "01b_home_station_cards.png")
SS_FIND     = os.path.join(SS, "02_find_station.png")
SS_MANAGE   = os.path.join(SS, "03_manage_stations.png")
SS_ADD      = os.path.join(SS, "03b_add_station.png")
SS_SESSIONS = os.path.join(SS, "04_charging_sessions.png")
SS_INSIGHTS = os.path.join(SS, "05_insights_charts.png")
SS_ML       = os.path.join(SS, "05b_ml_prediction.png")

# ── Colours ────────────────────────────────────────────────────────────────────
C_FOREST   = RGBColor(0x1B, 0x43, 0x32)   # Forest green — primary
C_MID      = RGBColor(0x2D, 0x6A, 0x4F)   # Mid green
C_ACCENT   = RGBColor(0x40, 0x91, 0x6C)   # Light green accent
C_SOFT     = RGBColor(0xD8, 0xF3, 0xDC)   # Soft mint card bg
C_OFFWHITE = RGBColor(0xF8, 0xF9, 0xF5)   # Off-white slide bg
C_WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
C_DARK     = RGBColor(0x1A, 0x1A, 0x2E)   # Near-black body text
C_GREY     = RGBColor(0x6C, 0x75, 0x7D)   # Muted grey
C_LTGREY   = RGBColor(0xE9, 0xEC, 0xEF)   # Card bg light
C_AMBER    = RGBColor(0xE9, 0xC4, 0x6A)   # Amber accent
C_CODEBG   = RGBColor(0xF1, 0xF3, 0xF5)   # Code block bg
C_CODETEXT = RGBColor(0x1B, 0x43, 0x32)

# ── Slide dimensions (16:9) ────────────────────────────────────────────────────
W = Inches(13.33)
H = Inches(7.5)

# ── Helpers ────────────────────────────────────────────────────────────────────
def new_prs():
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H
    return prs

def blank_slide(prs):
    """Add a completely blank slide."""
    blank = prs.slide_layouts[6]   # layout 6 = blank
    return prs.slides.add_slide(blank)

def rect(slide, l, t, w, h, fill=None, line=None):
    """Add a filled rectangle shape."""
    shape = slide.shapes.add_shape(1, l, t, w, h)   # MSO_SHAPE_TYPE.RECTANGLE = 1
    shape.line.fill.background()
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if line:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def txbox(slide, text, l, t, w, h,
          size=18, bold=False, color=C_DARK,
          align=PP_ALIGN.LEFT, italic=False,
          font="Calibri", wrap=True, valign=None):
    """Add a text box."""
    box = slide.shapes.add_textbox(l, t, w, h)
    tf  = box.text_frame
    tf.word_wrap = wrap
    if valign:
        tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name  = font
    return box

def add_para(tf, text, size=14, bold=False, color=C_DARK,
             align=PP_ALIGN.LEFT, italic=False, space_before=Pt(4)):
    """Append a paragraph to an existing text frame."""
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = space_before
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name  = "Calibri"
    return p

def bullet_box(slide, lines, l, t, w, h, size=15, color=C_DARK,
               bold_first=False, dot="●", line_color=None):
    """Multi-line bullet text box (no built-in list style)."""
    box = slide.shapes.add_textbox(l, t, w, h)
    tf  = box.text_frame
    tf.word_wrap = True
    first = True
    for line in lines:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.space_before = Pt(3)
        run = p.add_run()
        run.text = f"{dot}  {line}"
        run.font.size  = Pt(size)
        run.font.bold  = bold_first and (line == lines[0])
        lc = line_color if line_color else color
        run.font.color.rgb = lc
        run.font.name = "Calibri"
    return box

def add_image(slide, path, l, t, w, h=None):
    if not os.path.exists(path):
        # Draw placeholder rectangle
        r = rect(slide, l, t, w, h or Inches(3), fill=C_LTGREY, line=C_ACCENT)
        txbox(slide, f"[Screenshot: {os.path.basename(path)}]",
              l + Inches(0.1), t + Inches(0.1), w - Inches(0.2), (h or Inches(3)) - Inches(0.2),
              size=11, color=C_GREY, align=PP_ALIGN.CENTER)
        return r
    if h:
        return slide.shapes.add_picture(path, l, t, w, h)
    else:
        return slide.shapes.add_picture(path, l, t, w)

def add_notes(slide, text):
    notes = slide.notes_slide
    tf = notes.notes_text_frame
    tf.text = text

def green_header_bar(slide, title, subtitle=None):
    """Full-width dark-green header band at top."""
    rect(slide, 0, 0, W, Inches(1.25), fill=C_FOREST)
    txbox(slide, title,
          Inches(0.4), Inches(0.15), W - Inches(0.8), Inches(0.7),
          size=26, bold=True, color=C_WHITE, font="Calibri")
    if subtitle:
        txbox(slide, subtitle,
              Inches(0.4), Inches(0.82), W - Inches(0.8), Inches(0.4),
              size=13, color=C_SOFT, font="Calibri", italic=True)

def divider_line(slide, y=Inches(1.3), color=C_SOFT):
    """Thin horizontal rule below header."""
    sh = slide.shapes.add_shape(1, 0, y, W, Pt(2))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()

def slide_bg(slide):
    """Off-white background rect."""
    rect(slide, 0, 0, W, H, fill=C_OFFWHITE)

def card(slide, l, t, w, h, fill=C_WHITE, border=C_SOFT):
    r = rect(slide, l, t, w, h, fill=fill, line=border)
    return r

def slide_number(slide, n):
    txbox(slide, str(n), W - Inches(0.5), H - Inches(0.35),
          Inches(0.4), Inches(0.28), size=10, color=C_GREY, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def slide_01_title(prs):
    s = blank_slide(prs)
    # Background gradient: dark green top → off-white bottom
    rect(s, 0, 0, W, H, fill=C_FOREST)
    rect(s, 0, Inches(4.5), W, Inches(3), fill=C_OFFWHITE)
    # Decorative accent bar
    rect(s, 0, Inches(4.45), W, Inches(0.08), fill=C_AMBER)

    # Lightning bolt emoji area
    txbox(s, "⚡", Inches(0.5), Inches(0.5), Inches(1.2), Inches(1.2),
          size=60, color=C_AMBER, align=PP_ALIGN.CENTER)

    # Title
    txbox(s, "ChargeSpot",
          Inches(1.5), Inches(0.5), Inches(11), Inches(1.2),
          size=54, bold=True, color=C_WHITE, font="Calibri")

    # Tagline
    txbox(s, "EV Charging Availability & Usage Analytics System",
          Inches(1.5), Inches(1.65), Inches(10.5), Inches(0.6),
          size=22, color=C_SOFT, italic=True)

    # Separator
    rect(s, Inches(1.5), Inches(2.4), Inches(5), Pt(2), fill=C_AMBER)

    # Sub info
    txbox(s, "CSE494 — Intelligent NoSQL Databases",
          Inches(1.5), Inches(2.55), Inches(10), Inches(0.45),
          size=16, color=C_SOFT)

    txbox(s, "Academic Task 2  |  Lovely Professional University",
          Inches(1.5), Inches(3.0), Inches(10), Inches(0.4),
          size=14, color=RGBColor(0xA8, 0xCB, 0xB5))

    # Bottom pills
    for i, label in enumerate(["Python", "MongoDB", "Streamlit", "scikit-learn", "PyMongo"]):
        lx = Inches(0.5 + i * 2.5)
        card(s, lx, Inches(4.75), Inches(2.2), Inches(0.55),
             fill=C_SOFT, border=C_ACCENT)
        txbox(s, label, lx + Inches(0.1), Inches(4.82),
              Inches(2.0), Inches(0.42), size=13, color=C_FOREST,
              bold=True, align=PP_ALIGN.CENTER)

    # GitHub
    txbox(s, "🔗  github.com/Rithvikteja123/chargespot",
          Inches(0.5), Inches(6.8), Inches(8), Inches(0.4),
          size=11, color=C_GREY)

    slide_number(s, 1)
    add_notes(s,
        "Welcome everyone. My name is Rithvik Teja and today I'm presenting ChargeSpot — "
        "an EV Charging Availability and Usage Analytics System that I built for CSE494. "
        "The project uses MongoDB as the database, Python and PyMongo for the backend, "
        "and Streamlit for the interface. Let me walk you through what the system does "
        "and how I designed it.")

def slide_02_problem(prs):
    s = blank_slide(prs)
    slide_bg(s)
    green_header_bar(s, "Problem Statement",
                     "Why do EV drivers and operators need a better system?")
    divider_line(s)

    # Three problem cards
    problems = [
        ("🔌", "No Central Visibility",
         "Drivers have no way to check which charging connectors are available before arriving at a station."),
        ("❌", "Data Inconsistency",
         "Without a structured database, connector statuses become incorrect when sessions start and end manually."),
        ("📊", "No Usage Analytics",
         "Operators cannot identify which stations are heavily used or which connector types need expansion."),
    ]

    for i, (icon, title, desc) in enumerate(problems):
        lx = Inches(0.4 + i * 4.3)
        card(s, lx, Inches(1.5), Inches(4.1), Inches(3.8),
             fill=C_WHITE, border=C_SOFT)
        txbox(s, icon, lx + Inches(0.15), Inches(1.65),
              Inches(0.7), Inches(0.7), size=34, color=C_FOREST)
        txbox(s, title, lx + Inches(0.15), Inches(2.35),
              Inches(3.75), Inches(0.5), size=16, bold=True, color=C_FOREST)
        txbox(s, desc, lx + Inches(0.15), Inches(2.85),
              Inches(3.75), Inches(2.3), size=13, color=C_DARK)

    # Summary bar
    rect(s, 0, Inches(5.5), W, Inches(0.7), fill=C_SOFT)
    txbox(s, "ChargeSpot addresses all three problems with a MongoDB document database, "
            "PyMongo CRUD operations, and aggregation-based analytics.",
          Inches(0.4), Inches(5.57), W - Inches(0.8), Inches(0.55),
          size=13, color=C_FOREST, bold=True, align=PP_ALIGN.CENTER)

    slide_number(s, 2)
    add_notes(s,
        "The problem has three parts. First, EV drivers don't know which connector is free "
        "before they arrive. Second, without a proper database, connector status gets out of sync "
        "when someone starts or ends a charging session. Third, operators have no data to work "
        "with — they can't see usage trends or plan maintenance. ChargeSpot solves all three.")

def slide_03_solution(prs):
    s = blank_slide(prs)
    slide_bg(s)
    green_header_bar(s, "Proposed Solution & Objectives",
                     "What ChargeSpot does and what it demonstrates")
    divider_line(s)

    # Left column — Solution
    card(s, Inches(0.3), Inches(1.45), Inches(6.1), Inches(5.6),
         fill=C_WHITE, border=C_SOFT)
    txbox(s, "🎯  The Application", Inches(0.5), Inches(1.6),
          Inches(5.7), Inches(0.45), size=15, bold=True, color=C_FOREST)

    sol_items = [
        "Station directory: search and filter 10 EV stations",
        "Manage stations with full Create / Read / Update / Delete",
        "Start, complete, and cancel charging sessions",
        "Auto-sync connector status (available → occupied → available)",
        "Five MongoDB aggregation analytics visualised with Plotly",
        "ML congestion prediction using Decision Tree",
    ]
    bullet_box(s, sol_items, Inches(0.5), Inches(2.1),
               Inches(5.7), Inches(4.5), size=13, color=C_DARK, dot="✅")

    # Right column — Objectives
    card(s, Inches(6.6), Inches(1.45), Inches(6.4), Inches(5.6),
         fill=C_FOREST, border=C_FOREST)
    txbox(s, "📌  Course Objectives Met", Inches(6.8), Inches(1.6),
          Inches(6.0), Inches(0.45), size=15, bold=True, color=C_AMBER)

    obj_items = [
        "MongoDB document design (embedded + referenced)",
        "$jsonSchema validation at collection level",
        "PyMongo CRUD operations (all four)",
        "Five aggregation pipelines ($match, $unwind, $group, $lookup…)",
        "B-Tree index + explain() performance verification",
        "scikit-learn ML integration (explainable Decision Tree)",
    ]
    bullet_box(s, obj_items, Inches(6.8), Inches(2.15),
               Inches(5.9), Inches(4.5), size=13, color=C_SOFT, dot="→")

    slide_number(s, 3)
    add_notes(s,
        "ChargeSpot achieves the practical goal — a working EV charging tracker — while "
        "demonstrating every database concept required for CSE494. The left side shows what "
        "the application does for a user. The right side maps each feature to a specific "
        "NoSQL concept. So the project is not just a demo; it's a full course requirement checklist.")

def slide_04_stack(prs):
    s = blank_slide(prs)
    slide_bg(s)
    green_header_bar(s, "Technology Stack",
                     "Python · MongoDB · Streamlit · scikit-learn")
    divider_line(s)

    techs = [
        ("🗄️",  "MongoDB 7.0",     "NoSQL document database", C_FOREST),
        ("🐍",  "Python 3.14",     "Application logic & service layer", C_MID),
        ("🔌",  "PyMongo 4.19",    "Python driver — CRUD & aggregations", C_ACCENT),
        ("🌐",  "Streamlit 1.66",  "Reactive web UI with custom CSS", C_FOREST),
        ("📊",  "Plotly 7.1",      "Interactive bar, donut, pie charts", C_MID),
        ("🤖",  "scikit-learn 1.9","Decision Tree congestion predictor", C_ACCENT),
        ("🐼",  "Pandas 3.1",      "Tabular data formatting", C_FOREST),
        ("🔐",  "python-dotenv",   "Secure .env config management", C_MID),
    ]

    cols = 4
    for i, (icon, name, desc, color) in enumerate(techs):
        row = i // cols
        col = i % cols
        lx = Inches(0.3 + col * 3.2)
        ly = Inches(1.5 + row * 2.6)
        card(s, lx, ly, Inches(3.0), Inches(2.3), fill=C_WHITE, border=C_SOFT)
        txbox(s, icon, lx + Inches(0.1), ly + Inches(0.15),
              Inches(0.6), Inches(0.6), size=24, color=color)
        txbox(s, name, lx + Inches(0.7), ly + Inches(0.2),
              Inches(2.1), Inches(0.4), size=13, bold=True, color=color)
        txbox(s, desc, lx + Inches(0.1), ly + Inches(0.8),
              Inches(2.75), Inches(1.35), size=11, color=C_DARK)

    slide_number(s, 4)
    add_notes(s,
        "These eight technologies form the complete stack. MongoDB stores the data. "
        "Python and PyMongo connect to it. Streamlit builds the web interface without "
        "requiring any HTML or JavaScript. Plotly draws the analytics charts. "
        "scikit-learn provides the machine learning model. "
        "Pandas helps display tables, and python-dotenv keeps the database URI out of the code.")

def slide_05_db_design(prs):
    s = blank_slide(prs)
    slide_bg(s)
    green_header_bar(s, "MongoDB Database Design",
                     "chargespot_db  ·  stations collection  ·  charging_sessions collection")
    divider_line(s)

    # Left: Embedding explanation
    card(s, Inches(0.3), Inches(1.45), Inches(5.8), Inches(5.55),
         fill=C_WHITE, border=C_SOFT)
    txbox(s, "📦  stations  (Embedded Connectors)",
          Inches(0.45), Inches(1.6), Inches(5.5), Inches(0.45),
          size=14, bold=True, color=C_FOREST)

    doc_text = (
        '{\n'
        '  "station_id": "CS001",\n'
        '  "name": "Campus North Hub",\n'
        '  "city": "Phagwara",\n'
        '  "status": "operational",\n'
        '  "charging_speed_kw": 60,\n'
        '  "connectors": [\n'
        '    { "connector_id": "C1",\n'
        '      "connector_type": "CCS2",\n'
        '      "power_kw": 60,\n'
        '      "status": "available" },\n'
        '    { "connector_id": "C2", ... }\n'
        '  ]\n'
        '}'
    )
    card(s, Inches(0.45), Inches(2.1), Inches(5.4), Inches(3.6),
         fill=C_CODEBG, border=C_SOFT)
    box = s.shapes.add_textbox(Inches(0.55), Inches(2.2), Inches(5.2), Inches(3.4))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = doc_text
    r.font.name = "Courier New"
    r.font.size = Pt(9.5)
    r.font.color.rgb = C_CODETEXT

    txbox(s, "✅ Connectors embedded — always fetched with the station (1:Few)",
          Inches(0.45), Inches(5.8), Inches(5.5), Inches(0.6),
          size=11, color=C_ACCENT, italic=True)

    # Right: Session reference
    card(s, Inches(6.4), Inches(1.45), Inches(6.6), Inches(5.55),
         fill=C_FOREST, border=C_FOREST)
    txbox(s, "🗂️  charging_sessions  (Referenced)",
          Inches(6.55), Inches(1.6), Inches(6.3), Inches(0.45),
          size=14, bold=True, color=C_AMBER)

    sess_text = (
        '{\n'
        '  "session_id": "SESS-1001",\n'
        '  "station_id": "CS001",   ← reference\n'
        '  "connector_id": "C2",\n'
        '  "vehicle_id": "EV-NEXON-01",\n'
        '  "started_at": ISODate(...),\n'
        '  "ended_at": null,\n'
        '  "energy_kwh": 12.4,\n'
        '  "status": "in_progress"\n'
        '}'
    )
    card(s, Inches(6.55), Inches(2.1), Inches(6.25), Inches(3.1),
         fill=RGBColor(0x10, 0x2B, 0x20), border=C_MID)
    box2 = s.shapes.add_textbox(Inches(6.65), Inches(2.2), Inches(6.05), Inches(2.95))
    tf2 = box2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    r2 = p2.add_run()
    r2.text = sess_text
    r2.font.name = "Courier New"
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = C_SOFT

    # Why referenced
    reasons = [
        "Sessions grow without bound over time",
        "Embedding would breach MongoDB 16 MB doc limit",
        "Separate collection → independent indexes + $group",
        "$lookup joins sessions ↔ stations in aggregations",
    ]
    bullet_box(s, reasons, Inches(6.55), Inches(5.28),
               Inches(6.3), Inches(1.6), size=11.5, color=C_SOFT, dot="→")

    slide_number(s, 5)
    add_notes(s,
        "The database has two collections. Stations embed connectors because a station "
        "always has a small fixed number of connectors — two to five — and we always "
        "fetch them together. Charging sessions are stored separately because they grow "
        "without limit. If we embedded sessions inside the station document, we would "
        "eventually hit MongoDB's 16 megabyte document size limit. "
        "The foreign key is station_id, which we use in $lookup aggregations.")

def slide_06_ui(prs):
    s = blank_slide(prs)
    slide_bg(s)
    green_header_bar(s, "Application Modules & Interface",
                     "Five pages — Home · Find · Manage · Sessions · Insights")
    divider_line(s)

    # Module labels across top
    modules = [
        ("🏠 Home", "KPI dashboard\n& live status"),
        ("🔍 Find", "Search &\nfilter stations"),
        ("⚙️ Manage", "Full CRUD\noperations"),
        ("⚡ Sessions", "Lifecycle\nmanagement"),
        ("📊 Insights", "Aggregations\n& ML"),
    ]
    for i, (name, desc) in enumerate(modules):
        lx = Inches(0.25 + i * 2.6)
        card(s, lx, Inches(1.4), Inches(2.4), Inches(0.95),
             fill=C_FOREST if i == 0 else C_SOFT, border=C_SOFT)
        color = C_WHITE if i == 0 else C_FOREST
        txbox(s, name, lx + Inches(0.1), Inches(1.45),
              Inches(2.2), Inches(0.4), size=12, bold=True, color=color,
              align=PP_ALIGN.CENTER)
        txbox(s, desc, lx + Inches(0.1), Inches(1.82),
              Inches(2.2), Inches(0.48), size=9.5, color=color,
              align=PP_ALIGN.CENTER)

    # Screenshots: Home (large left) + Find (right top) + Insights (right bottom)
    add_image(s, SS_HOME, Inches(0.25), Inches(2.5), Inches(6.2), Inches(4.5))
    txbox(s, "Home Dashboard — KPI cards, live donut chart, recent sessions",
          Inches(0.25), Inches(7.0), Inches(6.2), Inches(0.35),
          size=9, color=C_GREY, italic=True, align=PP_ALIGN.CENTER)

    add_image(s, SS_FIND, Inches(6.65), Inches(2.5), Inches(6.4), Inches(2.1))
    txbox(s, "Find a Station — search, city/status/speed filters, connector badges",
          Inches(6.65), Inches(4.6), Inches(6.4), Inches(0.35),
          size=9, color=C_GREY, italic=True, align=PP_ALIGN.CENTER)

    add_image(s, SS_SESSIONS, Inches(6.65), Inches(5.1), Inches(6.4), Inches(2.1))
    txbox(s, "Charging Sessions — start, complete, cancel with connector sync",
          Inches(6.65), Inches(7.2), Inches(6.4), Inches(0.35),
          size=9, color=C_GREY, italic=True, align=PP_ALIGN.CENTER)

    slide_number(s, 6)
    add_notes(s,
        "The application has five pages. The home dashboard shows the network health at a "
        "glance — total stations, available connectors, and energy delivered — all pulled from "
        "MongoDB aggregation pipelines. The Find page lets users search by city, connector "
        "type, and minimum charging speed. The Sessions page manages the full session lifecycle. "
        "When a session starts, the connector immediately transitions to occupied. "
        "When it ends, it returns to available.")

def slide_07_crud_agg(prs):
    s = blank_slide(prs)
    slide_bg(s)
    green_header_bar(s, "CRUD · Validation · Indexing · Aggregation Pipelines",
                     "All four database operations + five analytics pipelines verified")
    divider_line(s)

    # Left: CRUD + Validation
    card(s, Inches(0.3), Inches(1.45), Inches(6.0), Inches(5.55),
         fill=C_WHITE, border=C_SOFT)
    txbox(s, "🛠️  CRUD & Validation", Inches(0.45), Inches(1.55),
          Inches(5.7), Inches(0.4), size=14, bold=True, color=C_FOREST)

    crud_items = [
        "CREATE  insert_one() — add station + $jsonSchema check",
        "READ    find() / find_one() — compound regex query",
        "UPDATE  update_one($set) — metadata + connectors.$.status",
        "DELETE  delete_one() — blocked if active sessions exist",
        "$jsonSchema rejects: negative speed, bad enum, empty connectors",
        "IXSCAN confirmed via explain() — O(log N) vs O(N) COLLSCAN",
    ]
    bullet_box(s, crud_items, Inches(0.45), Inches(2.0),
               Inches(5.7), Inches(4.7), size=11.5, color=C_DARK, dot="›")

    # Right: 5 Pipelines
    card(s, Inches(6.5), Inches(1.45), Inches(6.5), Inches(5.55),
         fill=C_FOREST, border=C_FOREST)
    txbox(s, "📈  5 Aggregation Pipelines", Inches(6.65), Inches(1.55),
          Inches(6.2), Inches(0.4), size=14, bold=True, color=C_AMBER)

    pipelines = [
        "① Connector status count  ($unwind → $group)",
        "② Energy by station  ($match → $group → $lookup → $project → $sort)",
        "③ Most-used stations  ($group → $lookup → $sort → $limit)",
        "④ Session status breakdown  ($group → $project)",
        "⑤ Connector standard pricing  ($unwind → $group → $sort)",
    ]
    bullet_box(s, pipelines, Inches(6.65), Inches(2.0),
               Inches(6.2), Inches(3.2), size=11.5, color=C_SOFT, dot="")

    # Verified result banner
    rect(s, Inches(6.5), Inches(5.25), Inches(6.5), Inches(1.65),
         fill=RGBColor(0x10, 0x2B, 0x20))
    verified_text = (
        "VERIFIED OUTPUT:\n"
        "  available: 20  ·  occupied: 6  ·  out_of_service: 7\n"
        "  Top station: CS004  —  247.97 kWh  ·  9 sessions\n"
        "  CCS2: 18 connectors  ·  Avg Rs. 17.08 / kWh"
    )
    box = s.shapes.add_textbox(Inches(6.65), Inches(5.3), Inches(6.2), Inches(1.55))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = verified_text
    r.font.name = "Courier New"
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x98, 0xF5, 0xA0)

    slide_number(s, 7)
    add_notes(s,
        "This slide covers the database operations and analytics. For CRUD, each operation "
        "uses a specific PyMongo method. The update for connectors uses the dollar positional "
        "operator — that's the dollar sign in connectors dot dollar dot status — which updates "
        "only the matched connector inside the embedded array. "
        "For schema validation, I tested a deliberately invalid document — negative speed, "
        "wrong status enum, empty connector array — and MongoDB rejected it with a WriteError. "
        "For aggregations, the most complex one is Pipeline 2 which chains five stages including "
        "a $lookup join between the sessions and stations collections.")

def slide_08_ml(prs):
    s = blank_slide(prs)
    slide_bg(s)
    green_header_bar(s, "Machine Learning — Station Busy Predictor",
                     "DecisionTreeClassifier  ·  91.3% accuracy on synthetic demo data")
    divider_line(s)

    # Left: ML screenshot
    add_image(s, SS_ML, Inches(0.3), Inches(1.5), Inches(6.0), Inches(5.55))

    # Right: Explanation cards
    # Features card
    card(s, Inches(6.6), Inches(1.5), Inches(6.4), Inches(2.1),
         fill=C_WHITE, border=C_SOFT)
    txbox(s, "🎛️  Input Features", Inches(6.75), Inches(1.6),
          Inches(6.1), Inches(0.38), size=13, bold=True, color=C_FOREST)
    features = ["Hour of day (0–23)", "Day type (Weekday / Weekend)",
                "Charging speed (kW)", "Connector count", "Is peak hours"]
    bullet_box(s, features, Inches(6.75), Inches(2.0),
               Inches(6.1), Inches(1.5), size=11, color=C_DARK, dot="●")

    # Model card
    card(s, Inches(6.6), Inches(3.75), Inches(6.4), Inches(1.8),
         fill=C_SOFT, border=C_SOFT)
    txbox(s, "🌳  Model Setup", Inches(6.75), Inches(3.85),
          Inches(6.1), Inches(0.38), size=13, bold=True, color=C_FOREST)
    model_facts = ["600 synthetic samples  ·  seed=42 (reproducible)",
                   "75 / 25 train-test split  ·  stratify=y",
                   "Max depth = 4  ·  Accuracy = 91.3%"]
    bullet_box(s, model_facts, Inches(6.75), Inches(4.25),
               Inches(6.1), Inches(1.2), size=11, color=C_DARK, dot="→")

    # Disclaimer card
    card(s, Inches(6.6), Inches(5.7), Inches(6.4), Inches(1.35),
         fill=RGBColor(0xFF, 0xF3, 0xCD), border=C_AMBER)
    txbox(s, "⚠️  Academic Disclaimer", Inches(6.75), Inches(5.8),
          Inches(6.1), Inches(0.38), size=12, bold=True,
          color=RGBColor(0x85, 0x63, 0x04))
    txbox(s,
          "91.3% is evaluated on synthetic / demo data only. "
          "Real-world accuracy would require re-training on actual charging logs. "
          "The model never writes to MongoDB.",
          Inches(6.75), Inches(6.2), Inches(6.1), Inches(0.75),
          size=11, color=RGBColor(0x85, 0x63, 0x04))

    slide_number(s, 8)
    add_notes(s,
        "For the machine learning component, I used a Decision Tree classifier because it "
        "produces interpretable rules — I can explain exactly why the model predicted a station "
        "as busy. The model takes five inputs: the hour, whether it's a weekend, the charger "
        "speed, the number of connectors, and whether it's a peak period. "
        "I generated 600 synthetic training samples. The split is 75% training, 25% test, with "
        "stratification to keep the busy and not-busy ratio equal in both sets. "
        "The 91.3% accuracy is on this synthetic data — I want to be clear that this has not "
        "been tested on real charging network logs. Also importantly, the model only reads "
        "station attributes — it never writes to the database.")

def slide_09_testing(prs):
    s = blank_slide(prs)
    slide_bg(s)
    green_header_bar(s, "Testing & Verified Results",
                     "Automated test suites: test_crud.py  ·  test_aggregations.py")
    divider_line(s)

    # Left: test matrix
    card(s, Inches(0.3), Inches(1.45), Inches(6.1), Inches(5.55),
         fill=C_WHITE, border=C_SOFT)
    txbox(s, "✅  All 14 Tests Passed", Inches(0.45), Inches(1.55),
          Inches(5.8), Inches(0.4), size=14, bold=True, color=C_FOREST)

    tests = [
        ("TC-01", "$jsonSchema rejects invalid document"),
        ("TC-02", "insert_one() creates station CS999"),
        ("TC-03", "find_one() reads station correctly"),
        ("TC-04", "update_one($set) updates speed to 120 kW"),
        ("TC-05", "Session start → connector: occupied"),
        ("TC-06", "delete_one() blocked by active session"),
        ("TC-07", "Session end → connector: available"),
        ("TC-08", "delete_one() cleans up test records"),
        ("TC-09", "explain() confirms IXSCAN on station_id"),
        ("TC-10–14", "All 5 aggregation pipelines verified"),
    ]
    for i, (code, desc) in enumerate(tests):
        ly = Inches(2.05 + i * 0.47)
        rect(s, Inches(0.45), ly, Inches(1.1), Inches(0.38),
             fill=C_FOREST)
        txbox(s, code, Inches(0.48), ly + Inches(0.04),
              Inches(1.05), Inches(0.3), size=9, bold=True, color=C_AMBER)
        txbox(s, desc, Inches(1.65), ly + Inches(0.04),
              Inches(4.65), Inches(0.3), size=10.5, color=C_DARK)

    # Right: terminal output
    card(s, Inches(6.6), Inches(1.45), Inches(6.4), Inches(5.55),
         fill=RGBColor(0x0D, 0x1F, 0x17), border=C_MID)
    txbox(s, "Terminal Output (test_crud.py)",
          Inches(6.75), Inches(1.55), Inches(6.1), Inches(0.38),
          size=12, bold=True, color=C_AMBER)

    terminal = (
        "✓ MongoDB Connection Verified.\n\n"
        "TEST 1: Schema Validation Rejection\n"
        "  Msg: 'Validation failed: Document failed'\n"
        "  ✓ PASSED\n\n"
        "TEST 5: Session Start + Connector Sync\n"
        "  Session 'SESS-TEST-999' started!\n"
        "  Connector 'C1' is now occupied.\n"
        "  ✓ PASSED\n\n"
        "TEST 6: Referential Integrity Guard\n"
        "  Cannot delete CS999: 1 active session.\n"
        "  ✓ PASSED\n\n"
        "TEST 9: Index explain() — IXSCAN\n"
        "  Stage: FETCH (input: IXSCAN)\n"
        "  ✓ PASSED\n\n"
        "ALL 9 TESTS PASSED!"
    )
    box = s.shapes.add_textbox(Inches(6.75), Inches(2.0), Inches(6.1), Inches(4.8))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = terminal
    r.font.name = "Courier New"
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x98, 0xF5, 0xA0)

    slide_number(s, 9)
    add_notes(s,
        "I wrote two automated test files. test_crud.py has nine tests and test_aggregations.py "
        "has five tests — one per pipeline. For the CRUD tests, I first deliberately submit "
        "an invalid document to prove that MongoDB's schema validator rejects it. Then I test "
        "each operation in order: create, read, update, session start with connector sync, "
        "deletion protection while a session is active, session end with connector restoration, "
        "and finally deletion of the test records. Test 9 calls explain() and confirms the "
        "query planner chose IXSCAN instead of COLLSCAN. All 14 tests passed.")

def slide_10_conclusion(prs):
    s = blank_slide(prs)
    slide_bg(s)
    green_header_bar(s, "Conclusion & Future Scope",
                     "What was built · What was demonstrated · What comes next")
    divider_line(s)

    # Achieved card
    card(s, Inches(0.3), Inches(1.45), Inches(6.1), Inches(3.7),
         fill=C_FOREST, border=C_FOREST)
    txbox(s, "✅  What Was Achieved", Inches(0.45), Inches(1.55),
          Inches(5.8), Inches(0.4), size=14, bold=True, color=C_AMBER)
    achieved = [
        "Hybrid MongoDB document model with clear design rationale",
        "$jsonSchema validation rejected invalid data at DB level",
        "All 4 CRUD operations with referential integrity guard",
        "5 aggregation pipelines — data stays in the database",
        "B-Tree index verified via explain() (IXSCAN)",
        "Explainable ML congestion predictor — 91.3% on demo data",
        "Polished Streamlit UI across 5 functional pages",
    ]
    bullet_box(s, achieved, Inches(0.45), Inches(2.0),
               Inches(5.8), Inches(3.0), size=11.5, color=C_SOFT, dot="✓")

    # Future card
    card(s, Inches(6.6), Inches(1.45), Inches(6.4), Inches(3.7),
         fill=C_WHITE, border=C_SOFT)
    txbox(s, "🚀  Future Scope", Inches(6.75), Inches(1.55),
          Inches(6.1), Inches(0.4), size=14, bold=True, color=C_FOREST)
    future = [
        "Real OCPP charging station API integration",
        "Geospatial search with MongoDB $geoNear + maps",
        "Role-based login for operators and drivers",
        "Real-time connector updates via WebSocket / MQTT",
        "Re-train ML on real charging network data",
        "Docker + CI/CD pipeline for deployment",
    ]
    bullet_box(s, future, Inches(6.75), Inches(2.0),
               Inches(6.1), Inches(3.0), size=11.5, color=C_DARK, dot="→")

    # Verified stats bar
    rect(s, 0, Inches(5.3), W, Inches(0.9), fill=C_SOFT)
    stats = "10 stations  ·  33 connectors  ·  42 sessions  ·  1,145.85 kWh delivered  ·  91.3% ML accuracy"
    txbox(s, stats, Inches(0.4), Inches(5.4), W - Inches(0.8), Inches(0.65),
          size=14, bold=True, color=C_FOREST, align=PP_ALIGN.CENTER)

    # Thank you bottom
    rect(s, 0, Inches(6.3), W, Inches(1.2), fill=C_FOREST)
    txbox(s, "Thank you — Questions welcome!",
          Inches(0.4), Inches(6.4), Inches(8), Inches(0.55),
          size=20, bold=True, color=C_WHITE)
    txbox(s, "🔗  github.com/Rithvikteja123/chargespot",
          Inches(8.5), Inches(6.55), Inches(4.5), Inches(0.4),
          size=12, color=C_SOFT, align=PP_ALIGN.RIGHT)

    slide_number(s, 10)
    add_notes(s,
        "To conclude — ChargeSpot demonstrates every course requirement for CSE494 in one "
        "working application: document design, validation, CRUD, indexing, aggregation, "
        "and machine learning. The database contains 10 stations, 33 connectors, and 42 "
        "session records. All 14 automated tests passed. The verified energy delivered across "
        "all completed sessions is 1,145 kilowatt-hours. "
        "For future work, the most impactful improvement would be connecting to a real "
        "OCPP charging API so the data reflects actual station activity. "
        "I'm happy to take any questions about the database design, the aggregation pipelines, "
        "or the machine learning module.")

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(os.path.join(BASE, "docs"), exist_ok=True)
    prs = new_prs()

    print("Building slides…")
    slide_01_title(prs)    ; print("  01 Title ✓")
    slide_02_problem(prs)  ; print("  02 Problem ✓")
    slide_03_solution(prs) ; print("  03 Solution ✓")
    slide_04_stack(prs)    ; print("  04 Stack ✓")
    slide_05_db_design(prs); print("  05 DB Design ✓")
    slide_06_ui(prs)       ; print("  06 UI ✓")
    slide_07_crud_agg(prs) ; print("  07 CRUD + Agg ✓")
    slide_08_ml(prs)       ; print("  08 ML ✓")
    slide_09_testing(prs)  ; print("  09 Testing ✓")
    slide_10_conclusion(prs); print("  10 Conclusion ✓")

    prs.save(OUT)
    size_kb = os.path.getsize(OUT) // 1024
    print(f"\nPresentation saved: {OUT}")
    print(f"File size: {size_kb} KB")
