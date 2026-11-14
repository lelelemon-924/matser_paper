# -*- coding: utf-8 -*-
"""
Minimalist, Large-Font Academic Layout Helpers (Zero AI-Card Slop)
for HITSZ Master's Thesis Defense PPT (16:9 widescreen, 13.333 x 7.5 in).
"""
import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import qn

SLIDE_W = 13.333
SLIDE_H = 7.500
MARGIN_X = 0.70
CONTENT_W = SLIDE_W - 2 * MARGIN_X  # 11.933 in

# Ultra-restrained academic palette: HIT Navy + Charcoal Ink + Subtle Accent
NAVY = RGBColor(0x00, 0x3B, 0x66)       # HIT Navy for titles, rules, highlights
INK = RGBColor(0x1A, 0x1A, 0x1A)        # Primary body text (crisp near-black)
SUB_INK = RGBColor(0x44, 0x4C, 0x56)    # Secondary text
MUTED = RGBColor(0x6E, 0x77, 0x81)      # Captions, section tag, page numbers
ACCENT_RED = RGBColor(0x9E, 0x2A, 0x2B) # Used sparingly for critical number/issue

WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT_BG = RGBColor(0xF6, 0xF8, 0xFA)    # Subtle background only for equations/cases
HL_ROW = RGBColor(0xF0, 0xF5, 0xFA)     # Subtle highlight row in Booktabs table
RULE_DARK = RGBColor(0x00, 0x3B, 0x66)
RULE_GRAY = RGBColor(0xD0, 0xD7, 0xDE)

FONT_CN = "微软雅黑"
FONT_EN = "Arial"
FONT_MONO = "Consolas"

ASSETS_DIR = os.path.join("ppt", "slides_assets")


def asset(filename: str) -> str:
    p = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(p):
        raise FileNotFoundError(f"Missing asset: {p}")
    return p


def set_run_font(run, size_pt: float, bold: bool = False, italic: bool = False,
                 color: RGBColor = INK, font_cn: str = FONT_CN, font_en: str = FONT_EN):
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font_en
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = OxmlElement("a:ea")
        rPr.append(ea)
    ea.set("typeface", font_cn)


def add_para(tf, runs, space_before: float = 0, space_after: float = 8,
             line_spacing: float = 1.35, align=PP_ALIGN.LEFT, first: bool = False):
    """
    Add a clean paragraph.
    runs: list of (text, size_pt, bold, color[, font_en, italic])
    """
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after = Pt(space_after)
    p.line_spacing = line_spacing
    for seg in runs:
        txt, sz = seg[0], seg[1]
        bd = seg[2] if len(seg) > 2 else False
        col = seg[3] if len(seg) > 3 else INK
        fen = seg[4] if len(seg) > 4 else FONT_EN
        fcn = FONT_MONO if fen == FONT_MONO else FONT_CN
        it = seg[5] if len(seg) > 5 else False
        r = p.add_run()
        r.text = txt
        set_run_font(r, sz, bold=bd, italic=it, color=col, font_cn=fcn, font_en=fen)
    return p


def add_textbox(slide, x: float, y: float, w: float, h: float, valign=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = valign
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    return tb, tf


def add_line(slide, x: float, y: float, w: float, color: RGBColor = RULE_GRAY, pt: float = 0.75):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(max(0.01, pt / 72.0)))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def add_box(slide, x: float, y: float, w: float, h: float,
            fill: RGBColor = SOFT_BG, border: RGBColor = RULE_GRAY, border_pt: float = 0.6):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if border is None or border_pt <= 0:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = border
        shp.line.width = Pt(border_pt)
    shp.shadow.inherit = False
    return shp


def add_bullets(slide, x: float, y: float, w: float, h: float, items: list,
                main_size: float = 17.0, sub_size: float = 15.0, gap: float = 12.0,
                valign=MSO_ANCHOR.TOP):
    """
    Render clean, spacious academic bullet points directly on white canvas (no AI boxes).
    """
    _, tf = add_textbox(slide, x, y, w, h, valign=valign)
    for idx, item in enumerate(items):
        is_first = (idx == 0)
        if isinstance(item, str):
            add_para(tf, [("•  " + item, main_size, False, INK)],
                     space_before=(0 if is_first else gap), space_after=4, line_spacing=1.35, first=is_first)
        elif len(item) == 2:
            lead, body = item
            runs = [("•  ", main_size, True, NAVY)]
            if lead:
                runs.append((lead, main_size, True, INK))
            if body:
                runs.append((body, main_size, False, INK))
            add_para(tf, runs, space_before=(0 if is_first else gap), space_after=4, line_spacing=1.35, first=is_first)
        else:
            lead, body, sub = item[0], item[1], item[2]
            runs = [("•  ", main_size, True, NAVY)]
            if lead:
                runs.append((lead, main_size, True, INK))
            if body:
                runs.append((body, main_size, False, INK))
            add_para(tf, runs, space_before=(0 if is_first else gap), space_after=3, line_spacing=1.32, first=is_first)
            if sub:
                add_para(tf, [("    " + sub, sub_size, False, SUB_INK)],
                         space_before=0, space_after=4, line_spacing=1.30)
    return tf


def add_picture_fit(slide, img_path: str, x: float, y: float, w: float, h: float, caption: str = None):
    """Fit an image cleanly on white background without heavy frames."""
    cap_h = 0.32 if caption else 0.0
    avail_h = h - cap_h
    with Image.open(img_path) as im:
        iw, ih = im.size
    ratio = iw / float(ih)
    if ratio > (w / avail_h):
        dw = w
        dh = w / ratio
    else:
        dh = avail_h
        dw = avail_h * ratio
    dx = x + (w - dw) / 2.0
    dy = y + (avail_h - dh) / 2.0
    pic = slide.shapes.add_picture(img_path, Inches(dx), Inches(dy), width=Inches(dw), height=Inches(dh))
    if caption:
        _, tf = add_textbox(slide, x, y + avail_h + 0.04, w, cap_h)
        add_para(tf, [(caption, 12.5, False, MUTED)], align=PP_ALIGN.CENTER, space_after=0, first=True)
    return pic


def new_slide(prs: Presentation, title: str, section_label: str, page_no: int, total_pages: int, notes: str = ""):
    """Minimalist academic content slide: clean title, subtle section label, thin rule, generous white space."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE

    # Title (left, 23pt bold Navy) + Section Label (right, 12pt muted)
    _, tf_t = add_textbox(slide, MARGIN_X, 0.34, 8.8, 0.50, valign=MSO_ANCHOR.MIDDLE)
    add_para(tf_t, [(title, 23.0, True, NAVY)], space_after=0, line_spacing=1.1, first=True)

    if section_label:
        _, tf_s = add_textbox(slide, SLIDE_W - MARGIN_X - 3.6, 0.40, 3.6, 0.40, valign=MSO_ANCHOR.MIDDLE)
        add_para(tf_s, [(section_label, 12.0, False, MUTED)], align=PP_ALIGN.RIGHT, space_after=0, first=True)

    add_line(slide, MARGIN_X, 0.92, CONTENT_W, color=NAVY, pt=1.1)

    # Minimalist footer (page number + quiet affiliation)
    _, tf_fl = add_textbox(slide, MARGIN_X, 7.04, 6.0, 0.30, valign=MSO_ANCHOR.MIDDLE)
    add_para(tf_fl, [("哈尔滨工业大学（深圳）硕士学位论文答辩", 10.5, False, MUTED)], space_after=0, first=True)

    _, tf_fr = add_textbox(slide, SLIDE_W - MARGIN_X - 1.5, 7.04, 1.5, 0.30, valign=MSO_ANCHOR.MIDDLE)
    add_para(tf_fr, [(f"{page_no} / {total_pages}", 11.5, False, MUTED)], align=PP_ALIGN.RIGHT, space_after=0, first=True)

    if notes:
        slide.notes_slide.notes_text_frame.text = notes.strip()
    return slide


def new_section_slide(prs: Presentation, part_str: str, sec_title: str, sub_items: list,
                      page_no: int, total_pages: int, notes: str = ""):
    """Clean Beamer-like section divider slide with generous breathing room."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE

    add_picture_fit(slide, asset("hitsz_logo_blue.png"), MARGIN_X, 0.48, 2.8, 0.52)

    add_line(slide, 1.35, 2.45, 0.85, color=NAVY, pt=3.0)
    _, tf_p = add_textbox(slide, 1.35, 2.62, 10.2, 0.45)
    add_para(tf_p, [(part_str, 16.0, True, NAVY)], space_after=0, first=True)

    _, tf_t = add_textbox(slide, 1.35, 3.12, 10.6, 0.85)
    add_para(tf_t, [(sec_title, 30.0, True, INK)], space_after=0, line_spacing=1.2, first=True)

    add_line(slide, 1.35, 4.15, 9.8, color=RULE_GRAY, pt=0.8)

    if sub_items:
        _, tf_sub = add_textbox(slide, 1.35, 4.40, 10.2, 1.80)
        for i, st in enumerate(sub_items):
            add_para(tf_sub, [(st, 16.0, False, SUB_INK)],
                     space_before=(0 if i == 0 else 8), space_after=2, first=(i == 0))

    _, tf_fr = add_textbox(slide, SLIDE_W - MARGIN_X - 1.5, 7.04, 1.5, 0.30, valign=MSO_ANCHOR.MIDDLE)
    add_para(tf_fr, [(f"{page_no} / {total_pages}", 11.5, False, MUTED)], align=PP_ALIGN.RIGHT, space_after=0, first=True)

    if notes:
        slide.notes_slide.notes_text_frame.text = notes.strip()
    return slide


def _cell_border(cell, side: str, pt: float, rgb_hex: str = None):
    tcPr = cell._tc.get_or_add_tcPr()
    tag = f"a:ln{side}"
    old = tcPr.find(qn(tag))
    if old is not None:
        tcPr.remove(old)
    ln = OxmlElement(tag)
    if pt <= 0 or rgb_hex is None:
        ln.append(OxmlElement("a:noFill"))
    else:
        ln.set("w", str(int(pt * 12700)))
        ln.set("cap", "flat")
        ln.set("cmpd", "sng")
        ln.set("algn", "ctr")
        sf = OxmlElement("a:solidFill")
        clr = OxmlElement("a:srgbClr")
        clr.set("val", rgb_hex)
        sf.append(clr)
        ln.append(sf)
    tcPr.append(ln)


def add_three_line_table(slide, x: float, y: float, w: float, h: float,
                         headers: list, rows: list, col_widths: list = None,
                         col_aligns: list = None, font_size: float = 14.0,
                         header_size: float = 14.5, highlight_rows: set = None,
                         sub_rules: set = None, red_cells: set = None, bold_cells: set = None):
    """Pure, spacious LaTeX Booktabs three-line table with large readable fonts."""
    n_rows = len(rows) + 1
    n_cols = len(headers)
    highlight_rows = highlight_rows or set()
    sub_rules = sub_rules or set()
    red_cells = red_cells or set()
    bold_cells = bold_cells or set()

    shape = slide.shapes.add_table(n_rows, n_cols, Inches(x), Inches(y), Inches(w), Inches(h))
    tbl = shape.table
    tblPr = tbl._tbl.tblPr
    for attr in ("bandRow", "firstRow", "lastRow", "bandCol", "firstCol", "lastCol"):
        tblPr.set(attr, "0")

    if col_widths:
        s = sum(col_widths)
        for j, cw in enumerate(col_widths):
            tbl.columns[j].width = Inches(w * cw / s)

    if col_aligns is None:
        col_aligns = [PP_ALIGN.LEFT] + [PP_ALIGN.CENTER] * (n_cols - 1)

    for j, htxt in enumerate(headers):
        c = tbl.cell(0, j)
        c.fill.solid()
        c.fill.fore_color.rgb = WHITE
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.margin_left = Inches(0.08)
        c.margin_right = Inches(0.08)
        c.margin_top = Inches(0.05)
        c.margin_bottom = Inches(0.05)
        _cell_border(c, "L", 0)
        _cell_border(c, "R", 0)
        _cell_border(c, "T", 1.6, "003B66")
        _cell_border(c, "B", 1.0, "003B66")
        add_para(c.text_frame, [(str(htxt), header_size, True, NAVY)],
                 align=col_aligns[j], space_after=0, line_spacing=1.15, first=True)

    for i, rdata in enumerate(rows):
        is_hl = (i in highlight_rows)
        is_last = (i == len(rows) - 1)
        has_sub = (i in sub_rules)
        for j, val in enumerate(rdata):
            c = tbl.cell(i + 1, j)
            c.fill.solid()
            c.fill.fore_color.rgb = HL_ROW if is_hl else WHITE
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_left = Inches(0.08)
            c.margin_right = Inches(0.08)
            c.margin_top = Inches(0.05)
            c.margin_bottom = Inches(0.05)
            _cell_border(c, "L", 0)
            _cell_border(c, "R", 0)
            _cell_border(c, "T", 1.0 if i == 0 else (0.6 if (i - 1) in sub_rules else 0),
                         "003B66" if i == 0 else "D0D7DE")
            if is_last:
                _cell_border(c, "B", 1.6, "003B66")
            elif has_sub:
                _cell_border(c, "B", 0.6, "D0D7DE")
            else:
                _cell_border(c, "B", 0)

            bd = is_hl or ((i, j) in bold_cells)
            col = ACCENT_RED if (i, j) in red_cells else (NAVY if is_hl else INK)
            add_para(c.text_frame, [(str(val), font_size, bd, col)],
                     align=col_aligns[j], space_after=0, line_spacing=1.20, first=True)
    return shape
