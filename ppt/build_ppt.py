"""基于本科答辩模板（结题答辩.pptx）的版式生成硕士答辩 PPT。

只复用模板的封面、目录、章节过渡页、内容页标题框架与结束页的装饰元素，
正文内容全部重新生成。运行：python build_ppt.py
"""
import copy
import os
import re

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(HERE, "结题答辩.pptx")
OUTPUT = os.path.join(HERE, "硕士答辩.pptx")
A = lambda name: os.path.join(HERE, "assets", name)          # noqa: E731
F = lambda name: os.path.join(ROOT, "figures", name)         # noqa: E731

FONT = "微软雅黑"
NUM_FONT = "Century Gothic"
THEME_HEX = "7391B5"                    # 替换模板主题色 accent1（原 4472C4）
MAIN = RGBColor(0x73, 0x91, 0xB5)       # 主色：浅雾蓝，用于色块填充（配白字）
MID = RGBColor(0x8F, 0xA7, 0xC4)
SOFT = RGBColor(0xBC, 0xCA, 0xDB)
PALE = RGBColor(0xEF, 0xF3, 0xF8)
BLUE = MAIN
DBLUE = RGBColor(0x4A, 0x6A, 0x91)      # 强调文字
TXT = RGBColor(0x33, 0x33, 0x33)
SUB = RGBColor(0x66, 0x6B, 0x73)
RED = RGBColor(0xA8, 0x62, 0x5C)        # 仅用于“危险 / rejected”类语义
GREEN = RGBColor(0x5E, 0x8A, 0x6E)      # 仅用于“安全 / chosen”类语义
LIGHT = RGBColor(0xF5, 0xF7, 0xFA)
LINE = RGBColor(0xD2, 0xDA, 0xE4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
STAGE = {k: MAIN for k in ("CPT", "SFT", "RLAIF", "DPO")}
STAGE_LIGHT = {k: PALE for k in ("CPT", "SFT", "RLAIF", "DPO")}
STAGE_T = {k: DBLUE for k in ("CPT", "SFT", "RLAIF", "DPO")}
HL_FILL = RGBColor(0xE4, 0xEB, 0xF3)
M = lambda name: os.path.join(HERE, "assets", "m_" + name)   # noqa: E731  按 PPT 配色重绘的论文图

# ---------------------------------------------------------------- 模板克隆工具

R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
BRIGHT_BLUES = {"0070C0", "4472C4", "2E75B6", "0066CC", "3A5A80"}


def _set_font(tb, typeface, spacing=None):
    """把文本框中所有 run 的西文字体设为 typeface，可选字距（1/100 pt）。"""
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            rpr = r._r.get_or_add_rPr()
            rpr.find(qn("a:latin")).set("typeface", typeface)
            if spacing is not None:
                rpr.set("spc", str(spacing))


def clone_slide(prs, src, keep_names=None):
    new = prs.slides.add_slide(src.slide_layout)
    for shp in list(new.shapes):
        shp._element.getparent().remove(shp._element)
    rid_map = {}
    for rid, rel in src.part.rels.items():
        if rel.reltype.endswith("/slideLayout") or rel.reltype.endswith("/notesSlide"):
            continue
        if rel.is_external:
            rid_map[rid] = new.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
        else:
            rid_map[rid] = new.part.relate_to(rel.target_part, rel.reltype)
    tree = new.shapes._spTree
    for el in src.shapes._spTree.iterchildren():
        tag = etree.QName(el).localname
        if tag in ("nvGrpSpPr", "grpSpPr", "extLst"):
            continue
        name_el = el.find(".//" + qn("p:cNvPr"))
        name = name_el.get("name") if name_el is not None else ""
        if keep_names is not None and name not in keep_names:
            continue
        new_el = copy.deepcopy(el)
        for node in new_el.iter():
            for attr, val in list(node.attrib.items()):
                if attr.startswith(R_NS) and val in rid_map:
                    node.set(attr, rid_map[val])
            if node.tag == qn("a:srgbClr") and node.get("val", "").upper() in BRIGHT_BLUES:
                node.set("val", THEME_HEX)
        tree.append(new_el)
    return new


def delete_slide(prs, slide):
    lst = prs.slides._sldIdLst
    for sld_id in list(lst):
        if prs.part.related_part(sld_id.rId) is slide.part:
            prs.part.drop_rel(sld_id.rId)
            lst.remove(sld_id)
            return


def shape_by_name(slide, name):
    for shp in slide.shapes:
        if shp.name == name:
            return shp
    raise KeyError(name)


def replace_text(shape, lines, size=None):
    """保留首个 run 的格式，替换为多行文本。"""
    tf = shape.text_frame
    p0 = tf.paragraphs[0]
    r0 = p0.runs[0]._r if p0.runs else None
    rpr = copy.deepcopy(r0.find(qn("a:rPr"))) if r0 is not None else None
    ppr = copy.deepcopy(p0._p.find(qn("a:pPr")))
    txbody = tf._txBody
    for p in list(txbody.findall(qn("a:p"))):
        txbody.remove(p)
    for line in lines:
        p = etree.SubElement(txbody, qn("a:p"))
        if ppr is not None:
            p.append(copy.deepcopy(ppr))
        r = etree.SubElement(p, qn("a:r"))
        if rpr is not None:
            rp = copy.deepcopy(rpr)
            if size:
                rp.set("sz", str(int(size * 100)))
            r.append(rp)
        t = etree.SubElement(r, qn("a:t"))
        t.text = line


# ---------------------------------------------------------------- 绘图工具

def _apply_font(run, size, color=TXT, bold=False):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    f.name = FONT
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rpr, qn(tag))
        el.set("typeface", FONT)


TOKEN = re.compile(r"(\*\*.+?\*\*|!!.+?!!|~~.+?~~)")


def _add_runs(p, text, size, color, bold):
    """**加粗蓝** / !!加粗红!! / ~~灰色小字~~"""
    for seg in TOKEN.split(text):
        if not seg:
            continue
        c, b, s = color, bold, size
        if seg.startswith("**"):
            seg, c, b = seg[2:-2], DBLUE, True
        elif seg.startswith("!!"):
            seg, c, b = seg[2:-2], RED, True
        elif seg.startswith("~~"):
            seg, c, s = seg[2:-2], SUB, size - 2
        r = p.add_run()
        r.text = seg
        _apply_font(r, s, c, b)


def text(slide, x, y, w, h, paras, size=16, color=TXT, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, bullet=None, spacing=1.15, space_after=4, margin=0.05):
    """paras: str 或 list[str]；每个元素一段。bullet: None / '•' / '▪' / 'num'。"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(margin))
    if isinstance(paras, str):
        paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(space_after)
        if bullet:
            mark = f"{i + 1}. " if bullet == "num" else f"{bullet} "
            r = p.add_run()
            r.text = mark
            _apply_font(r, size, BLUE, True)
        _add_runs(p, para, size, color, bold)
    return tb


def box(slide, x, y, w, h, fill=LIGHT, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
        radius=0.08, line_w=1.0):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.text_frame.text = ""
    return s


def label(slide, x, y, w, h, txt, fill, color=WHITE, size=14, bold=True, line=None,
          shape=MSO_SHAPE.ROUNDED_RECTANGLE, align=PP_ALIGN.CENTER, radius=0.15):
    s = box(slide, x, y, w, h, fill=fill, line=line, shape=shape, radius=radius)
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(0.04))
    lines = txt.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = 1.05
        _add_runs(p, ln, size if i == 0 else size - 2, color, bold if i == 0 else False)
    return s


def card(slide, x, y, w, h, title, body, color, size=14, title_size=15, bullet="•",
         fill=None, title_h=0.42):
    """浅底卡片：标题用文字强调，卡片顶部不再铺整条深色。"""
    box(slide, x, y, w, h, fill=fill or WHITE, line=color, radius=0.04, line_w=1.25)
    text(slide, x + 0.12, y + 0.02, w - 0.24, title_h - 0.04, title, size=title_size,
         color=DBLUE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    box(slide, x + 0.12, y + title_h - 0.01, w - 0.24, 0.012, fill=SOFT, shape=MSO_SHAPE.RECTANGLE)
    text(slide, x + 0.08, y + title_h + 0.05, w - 0.16, h - title_h - 0.1, body, size=size,
         bullet=bullet, spacing=1.1, space_after=3)


def subhead(slide, x, y, w, txt, size=19, color=BLUE):
    tb = text(slide, x, y, w, 0.45, f"◆ {txt}", size=size, color=color, bold=True)
    return tb


def arrow(slide, x, y, w, h, color=BLUE, shape=MSO_SHAPE.RIGHT_ARROW):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def picture(slide, path, x, y, w=None, h=None):
    """在 (x, y, w, h) 框内等比放置图片并居中。"""
    from PIL import Image
    iw, ih = Image.open(path).size
    ar = iw / ih
    if w is not None and h is not None:
        if w / h > ar:
            nw, nh = h * ar, h
        else:
            nw, nh = w, w / ar
        x, y = x + (w - nw) / 2, y + (h - nh) / 2
        w, h = nw, nh
    elif w is not None:
        h = w / ar
    else:
        w = h * ar
    return slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))


def table(slide, x, y, w, rows, col_w=None, row_h=0.36, size=13, head_fill=BLUE,
          hl_rows=(), hl_fill=HL_FILL, first_col_left=True, bold_hl=True,
          left_cols=(), head_h=None):
    nr, nc = len(rows), len(rows[0])
    head_h = head_h or row_h
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(head_h + row_h * (nr - 1)))
    tbl = gt.table
    tbl_pr = gt._element.graphic.graphicData.tbl.tblPr
    style_id = tbl_pr.find(qn("a:tableStyleId"))
    if style_id is not None:
        style_id.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"   # No Style, Table Grid
    if col_w:
        tot = sum(col_w)
        for i, cw in enumerate(col_w):
            tbl.columns[i].width = Inches(w * cw / tot)
    for r in range(nr):
        tbl.rows[r].height = Inches(head_h if r == 0 else row_h)
        for c in range(nc):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.05)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            left = (c == 0 and first_col_left) or (c in left_cols and r > 0)
            p.alignment = PP_ALIGN.LEFT if left else PP_ALIGN.CENTER
            val = str(rows[r][c])
            if r == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = head_fill
                _add_runs(p, val, size, WHITE, True)
            else:
                cell.fill.solid()
                if r in hl_rows:
                    cell.fill.fore_color.rgb = hl_fill
                else:
                    cell.fill.fore_color.rgb = WHITE if r % 2 else RGBColor(0xF5, 0xF7, 0xFB)
                _add_runs(p, val, size, TXT, bold_hl and r in hl_rows)
            _cell_border(cell)
    return gt


def _cell_border(cell, color="C9D3E3"):
    tc_pr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        ln = tc_pr.find(qn(tag))
        if ln is None:
            ln = etree.SubElement(tc_pr, qn(tag))
        ln.set("w", "9525")
        for ch in list(ln):
            ln.remove(ch)
        sf = etree.SubElement(ln, qn("a:solidFill"))
        clr = etree.SubElement(sf, qn("a:srgbClr"))
        clr.set("val", color)


def banner(slide, y, txt, fill=MAIN, size=16, x=0.55, w=12.25, h=0.5):
    """通栏结论条：浅底细边，避免整条深色填充。fill 只用作边框颜色。"""
    return label(slide, x, y, w, h, txt, PALE, color=DBLUE, size=size, line=fill, radius=0.2)


# ---------------------------------------------------------------- 页面工厂

class Deck:
    def __init__(self):
        self.prs = Presentation(TEMPLATE)
        self.proto = list(self.prs.slides)
        self.cover, self.toc, self.section, self.content = (self.proto[i] for i in (0, 1, 2, 3))
        self.end = self.proto[-1]
        theme = self.prs.slide_masters[0].part.part_related_by(RT.THEME)
        theme._blob = theme.blob.replace(b'<a:accent1><a:srgbClr val="4472C4"/>',
                                         f'<a:accent1><a:srgbClr val="{THEME_HEX}"/>'.encode())

    def _side_bar_slide(self, proto, keep):
        """模板左侧色条 + 校徽 + 页码，去掉方框线等其余装饰。"""
        return clone_slide(self.prs, proto, keep_names=keep)

    def add_cover(self):
        s = clone_slide(self.prs, self.cover)
        replace_text(shape_by_name(s, "文本框 14"), ["面向数字电网知识服务的", "大语言模型训练与对齐方法研究"], size=36)
        en = shape_by_name(s, "TextBox 10")
        replace_text(en, ["Research on Training and Alignment Methods of Large Language Models",
                          "for Digital Power Grid Knowledge Services"], size=18)
        en.top = Emu(4100000)
        text(s, 2.4, 6.55, 8.5, 0.4, "学科：控制科学与工程　　学院：智能科学与工程学院",
             size=14, color=SUB, align=PP_ALIGN.CENTER)
        return s

    def add_toc(self, items):
        s = self._side_bar_slide(self.toc, {"矩形 4", "图片 3", "灯片编号占位符 7"})
        text(s, 2.4, 0.95, 4.0, 0.8, "目录", size=40, color=TXT, bold=True)
        tb = text(s, 2.42, 1.75, 4.0, 0.4, "CONTENTS", size=16, color=MID)
        _set_font(tb, NUM_FONT, spacing=300)
        box(s, 2.45, 2.3, 10.2, 0.02, fill=LINE, shape=MSO_SHAPE.RECTANGLE)
        for i, (it, tag) in enumerate(items):
            cx, cy = 2.45 + (i % 2) * 5.2, 2.75 + (i // 2) * 1.3
            nb = text(s, cx, cy, 1.0, 0.8, f"{i + 1:02d}", size=32, color=MAIN, anchor=MSO_ANCHOR.MIDDLE)
            _set_font(nb, NUM_FONT)
            box(s, cx + 1.05, cy + 0.12, 0.025, 0.56, fill=SOFT, shape=MSO_SHAPE.RECTANGLE)
            text(s, cx + 1.25, cy + (0.02 if tag else 0.18), 3.9, 0.45, it, size=19, color=TXT)
            if tag:
                tg = text(s, cx + 1.27, cy + 0.44, 3.9, 0.35, tag, size=12.5, color=MID)
                _set_font(tg, NUM_FONT, spacing=100)
        return s

    def add_section(self, num, title, keywords=""):
        s = self._side_bar_slide(self.section, {"矩形 1", "图片 7", "灯片编号占位符 2"})
        nb = text(s, 2.1, 2.3, 2.5, 1.7, f"{num:02d}", size=96, color=MAIN, align=PP_ALIGN.RIGHT,
                  anchor=MSO_ANCHOR.MIDDLE, margin=0)
        _set_font(nb, NUM_FONT)
        box(s, 4.95, 2.45, 0.03, 1.45, fill=SOFT, shape=MSO_SHAPE.RECTANGLE)
        pb = text(s, 5.3, 2.3, 5.0, 0.45, f"PART {num:02d}", size=16, color=MID)
        _set_font(pb, NUM_FONT, spacing=200)
        text(s, 5.3, 2.75, 7.5, 0.8, title, size=36, color=TXT, bold=True)
        if keywords:
            text(s, 5.3, 3.55, 7.5, 0.45, keywords, size=15, color=SUB)
        return s

    def add_content(self, title, stage=None, title_size=26):
        s = clone_slide(self.prs, self.content,
                        keep_names={"组合 53", "直接连接符 59", "图片 5", "灯片编号占位符 2"})
        grp = shape_by_name(s, "组合 53")
        tb = [c for c in grp.shapes if c.has_text_frame][0]
        units = sum(1.0 if ord(ch) > 0x2E80 else 0.56 for ch in title)
        title_size = min(title_size, int(8.1 * 72 / units))
        replace_text(tb, [title], size=title_size)
        tb.text_frame.word_wrap = False
        tb.width = Inches(8.6)
        xfrm = grp._element.find(qn("p:grpSpPr")).find(qn("a:xfrm"))
        for tag in ("a:ext", "a:chExt"):
            xfrm.find(qn(tag)).set("cx", str(Inches(9.0)))
        if stage:
            names = ["CPT", "SFT", "RLAIF", "DPO"]
            x0 = 9.62
            for i, n in enumerate(names):
                on = n == stage
                label(s, x0 + i * 0.82, 1.22, 0.76, 0.27, n,
                      STAGE[n] if on else WHITE, color=WHITE if on else RGBColor(0xA6, 0xA6, 0xA6),
                      size=11, line=None if on else RGBColor(0xD0, 0xD0, 0xD0), radius=0.3)
        return s

    def add_end(self):
        return clone_slide(self.prs, self.end)

    def save(self):
        for s in self.proto:
            delete_slide(self.prs, s)
        self.prs.save(OUTPUT)
        print("saved", OUTPUT, len(self.prs.slides), "slides")


# ---------------------------------------------------------------- 内容

def build():
    d = Deck()
    d.add_cover()
    d.add_toc([("研究背景与总体框架", ""), ("数据体系构建与持续预训练", "CPT"),
               ("指令数据构建与监督微调", "SFT"), ("回答风格强化学习对齐", "RLAIF"),
               ("电力安全合规深层对齐", "DPO"), ("总结与展望", "")])

    # ================= PART 01
    d.add_section(1, "研究背景与总体框架", "行业需求　·　四层挑战　·　技术路线　·　创新点")

    s = d.add_content("电力知识服务需要专业的领域大模型")
    subhead(s, 0.55, 1.55, 5.6, "电力行业的知识资产")
    text(s, 0.65, 2.05, 5.5, 2.6, [
        "技术标准、运行规程、设备手册、检修记录、故障工单、制度文件……",
        "分散在不同业务系统：**术语密集、因果链长、制度约束强**",
        "大语言模型提供新路径：知识问答、故障归因、条款解释、方案比较",
    ], size=16, bullet="•", spacing=1.2, space_after=8)
    label(s, 0.65, 4.75, 5.4, 0.85, "研究依托\n中国南方电网数字电网大模型项目", LIGHT, color=DBLUE, size=16,
          line=LINE)
    text(s, 0.65, 5.75, 5.4, 0.9, "基座模型：Qwen2.5-7B（预训练版）\n目标：可安全部署的电力领域大语言模型",
         size=14, color=SUB)
    subhead(s, 6.5, 1.55, 6.3, "四类核心任务")
    tasks = [
        ("电力知识问答", "例：变压器差动保护的原理是什么？", "准确阐述，层次分明"),
        ("故障诊断", "例：线路跳闸重合不成功", "结论先行，由易到难排查，附安全提示"),
        ("制度问答", "例：高压设备检修需办理哪些票证？", "引用条款来源，界定适用边界"),
        ("技术方案分析", "例：储能配置比例对新能源消纳率的影响", "明确前提假设，多维度权衡"),
    ]
    for i, (t, q, r) in enumerate(tasks):
        cx, cy = 6.55 + (i % 2) * 3.15, 2.1 + (i // 2) * 2.3
        box(s, cx, cy, 3.0, 2.1, fill=WHITE, line=LINE, radius=0.05)
        label(s, cx, cy, 3.0, 0.48, t, BLUE, size=16, radius=0.1)
        text(s, cx + 0.1, cy + 0.58, 2.8, 0.75, q, size=13.5, color=SUB)
        text(s, cx + 0.1, cy + 1.32, 2.8, 0.75, f"输出要求：**{r}**", size=13.5)

    s = d.add_content("四个层面的挑战：单一训练阶段难以兼顾")
    ch = [
        ("知识层面", "CPT", "知识注入", ["发电、输变配、调度、检修多源异构资料",
                                         "设备原理、保护逻辑、制度条款相互关联", "通用模型**领域知识不足**"]),
        ("任务层面", "SFT", "任务微调", ["故障诊断需排查顺序，制度问答需条款依据",
                                         "方案分析需前提假设", "笼统回答**看似完整却不可采纳**"]),
        ("表达层面", "RLAIF", "风格对齐", ["研究人员要机理分析", "运维人员要可执行步骤",
                                           "管理人员要明确裁定", "风格取决于**“谁在问”**"]),
        ("安全层面", "DPO", "安全对齐", ["**“语言合规但工程危险”**",
                                         "以“提高效率”为借口诱导跳过闭锁", "伪装学术讨论的参数越限",
                                         "缺少固定敏感词"]),
    ]
    for i, (t, st, sname, body) in enumerate(ch):
        cx = 0.6 + i * 3.1
        card(s, cx, 1.65, 2.9, 3.35, t, body, STAGE[st], size=14.5, title_size=17, fill=STAGE_LIGHT[st])
        arrow(s, cx + 1.25, 5.1, 0.4, 0.38, color=STAGE[st], shape=MSO_SHAPE.DOWN_ARROW)
        label(s, cx + 0.25, 5.55, 2.4, 0.5, f"{st}　{sname}", PALE, color=DBLUE, size=16,
              line=STAGE[st])
    banner(s, 6.25, "CPT → SFT → RLAIF → DPO 四阶段框架，依次应对知识、任务、表达、安全四个层面的挑战", size=15.5)

    s = d.add_content("研究现状：电力领域缺少从知识注入到安全对齐的系统方法")
    rows = [
        ["研究方向", "代表工作", "现有不足"],
        ["垂直领域大模型", "DAPT、BloombergGPT、Med-PaLM；\n电力：ElecBench、PowerGPT、eGridGPT",
         "多为单任务原型、外部检索或评测基准；CPT 与 SFT 割裂，缺少多阶段训练体系"],
        ["指令数据构建", "Self-Instruct、Evol-Instruct、\nDESIGNER、DFT",
         "面向开放域或统一模板，缺少专家逻辑 + 知识图谱约束的场景原生合成；DFT 未与领域知识注入结合"],
        ["反馈强化学习\n与风格控制", "InstructGPT、RLAIF、GRPO / DAPO；\nCTRL、Prefix-Tuning",
         "风格由语料类别隐式决定，无法按用户角色显式控制"],
        ["DPO 与安全对齐", "DPO、浅层安全对齐（Qi et al., ICLR 2025）、\nXSTest、OR-Bench",
         "面向通用有害内容，未覆盖电力隐蔽风险的中途恢复；强化安全易引发过度拒答"],
    ]
    table(s, 0.6, 1.7, 12.15, rows, col_w=[2.0, 4.4, 5.75], row_h=0.92, size=14.5, left_cols=(1, 2),
          head_h=0.48)
    banner(s, 6.3, "切入点：面向电力业务的“知识—任务—风格—安全”多阶段训练与对齐", size=15.5)

    s = d.add_content("技术路线：CPT—SFT—RLAIF—DPO 四阶段递进训练")
    picture(s, A("fig1-1_总体框架.png"), 0.7, 1.55, 11.9, 4.8)
    text(s, 0.7, 6.4, 11.9, 0.45,
         "以前一阶段输出为初始化，能力逐级累积；七类数据标签 → CPT/SFT，三类用户群体 → RLAIF，四类安全风险 → DPO",
         size=14, color=SUB, align=PP_ALIGN.CENTER)

    s = d.add_content("主要创新点")
    inn = [
        ("SFT", "面向七类电力业务场景的场景原生指令数据合成方法",
         "专家种子 + 设计逻辑 + 知识图谱约束 + 指令演化 + 多维质量筛选", "600 → 6.8 万条"),
        ("SFT", "CPT 领域先验与 DFT 相结合的监督微调策略",
         "CPT 将事实 token 推离低概率区，DFT 压低表面 token 的梯度权重", "FaultDiag +4.7 pp"),
        ("RLAIF", "面向目标用户群体的风格条件化 Prefix 强化学习对齐",
         "三类目 × 三取值风格组合，StyleRM-7B 奖励，GRPO + Clip-Higher", "SHR 90.2%（+27.6 pp）"),
        ("DPO", "基于同状态恢复数据与困难状态加权的深层安全对齐",
         "k = 0 统一根节点拒答，Token 边界截断，HS-Weighting 困难状态加权", "ASR 7.9%｜ORR 5.0%"),
    ]
    for i, (st, t, desc, kpi) in enumerate(inn):
        cy = 1.65 + i * 1.22
        box(s, 0.6, cy, 12.2, 1.05, fill=STAGE_LIGHT[st], line=None, radius=0.1)
        label(s, 0.6, cy, 0.95, 1.05, f"{i + 1}", STAGE[st], size=30, radius=0.1)
        text(s, 1.7, cy + 0.08, 7.9, 0.45, t, size=18, color=STAGE[st], bold=True)
        text(s, 1.7, cy + 0.55, 7.9, 0.45, desc, size=14.5, color=SUB)
        label(s, 9.75, cy + 0.25, 2.85, 0.55, kpi, WHITE, color=STAGE[st], size=16, line=STAGE[st])

    # ================= PART 02
    d.add_section(2, "数据体系构建与持续预训练", "七类电力数据　·　困惑度双阈值筛选　·　1:1 领域-通用混合")

    s = d.add_content("七类电力数据体系与系统化预处理", stage="CPT")
    subhead(s, 0.55, 1.55, 5.5, "数据来源")
    label(s, 0.65, 2.05, 2.75, 1.65,
          "内部语料（授权、脱敏）\n故障工单、缺陷与检修记录\n试验报告、调度日志\n企业标准、规程、两票细则",
          STAGE_LIGHT["CPT"], color=STAGE_T["CPT"], size=14.5, line=STAGE["CPT"], radius=0.06)
    label(s, 3.5, 2.05, 2.6, 1.65, "公开语料\n国家 / 行业标准\n教材与学术论文\n白皮书、市场与安全文件",
          WHITE, color=STAGE_T["CPT"], size=14.5, line=STAGE["CPT"], radius=0.06)
    subhead(s, 6.4, 1.55, 6.3, "七类数据类型标签")
    cats = ["基础科学与仿真理论", "物理电网与工程建设", "新型电力系统与能源互联", "运行控制与二次系统",
            "运维检修与资产管理", "综合管理安全与市场", "制度文件"]
    for i, c in enumerate(cats):
        cx, cy = 6.5 + (i % 2) * 3.1, 2.05 + (i // 2) * 0.43
        label(s, cx, cy, 3.0, 0.37, f"{i + 1}. {c}", LIGHT, color=TXT, size=13, bold=False, line=LINE,
              align=PP_ALIGN.LEFT, radius=0.2)
    picture(s, A("数据预处理与标签化.png"), 0.55, 3.85, 12.25, 2.45)
    banner(s, 6.36, "三级去重：SimHash −18.6% → MinHash+LSH −12.3% → BGE-M3 语义 −7.2%，累计保留 66.2%",
           fill=STAGE["CPT"], size=15, h=0.46)

    s = d.add_content("困惑度双阈值筛选：去两端、留中间", stage="CPT")
    steps = [
        ("种子模型", "5% 精选切片做初步 CPT"),
        ("PPL 评分", "对其余 95% 逐切片计算困惑度"),
        ("教师标注", "20 个分位段 × 250 条，Qwen-Max 判冗余 / 噪声 / 有效"),
        ("零训练搜索", "63 组上下界，最大化保留质量 F"),
    ]
    for i, (t, dsc) in enumerate(steps):
        cy = 1.65 + i * 1.0
        label(s, 0.6, cy, 0.5, 0.78, f"{i + 1}", STAGE["CPT"], size=20, radius=0.2)
        box(s, 1.15, cy, 3.25, 0.78, fill=STAGE_LIGHT["CPT"], radius=0.1)
        text(s, 1.22, cy + 0.02, 3.15, 0.3, t, size=15, color=STAGE_T["CPT"], bold=True)
        text(s, 1.22, cy + 0.34, 3.15, 0.45, dsc, size=12.5, color=SUB, spacing=1.0)
    label(s, 0.6, 5.6, 3.8, 1.18, "保留区间 [P10, P80]\n4.8 ≤ PPL ≤ 35.5\n保留约 70%，F = 88.6",
          PALE, color=DBLUE, size=17, line=MAIN, radius=0.1)
    picture(s, M("ppl_threshold_selection.png"), 4.65, 1.6, 8.2, 3.9)
    text(s, 4.75, 5.6, 8.0, 1.2, [
        "低 PPL 端：固定套话、重复表头等**冗余**占 74%",
        "高 PPL 端：OCR 错位、公式残缺等**隐性噪声**由 64% 陡增至 89%",
        "两端拐点与搜索得到的最优区间一致",
    ], size=14.5, bullet="•", spacing=1.05)

    s = d.add_content("1:1 领域-通用配比在知识注入与通用能力间最均衡", stage="CPT")
    picture(s, M("fig2-4_data_ratio.png"), 0.55, 1.6, 6.3, 3.9)
    rows = [["领域:通用", "PowerQA", "通用 GS", "均衡 S"],
            ["基座模型", "43.5", "65.8", "52.4"], ["0:1", "44.1", "66.0", "52.9"],
            ["1:2", "57.8", "64.3", "60.9"], ["1:1（采用）", "68.2", "62.1", "65.0"],
            ["2:1", "71.1", "57.4", "63.5"], ["1:0", "72.4", "55.3", "62.7"]]
    table(s, 7.1, 1.65, 5.7, rows, col_w=[1.6, 1.3, 1.3, 1.3], row_h=0.4, size=14, hl_rows=(4,),
          head_fill=STAGE["CPT"])
    text(s, 7.1, 4.6, 5.75, 2.2, [
        "S 为 PowerQA 与通用得分的调和平均",
        "1:1：PowerQA **+24.7 pp**，通用能力仅 −3.7 pp",
        "消融：不做 PPL 筛选，PowerQA 仅 61.5%",
        "约 4.2B token，8×A100；通用 PPL 仅升 0.3",
    ], size=14.5, bullet="•", spacing=1.1)
    text(s, 0.65, 5.6, 6.2, 1.1, "纯领域训练 PowerQA 最高（72.4%），但通用得分骤降 10.5 pp，出现灾难性遗忘",
         size=14, color=SUB)

    # ================= PART 03
    d.add_section(3, "指令数据构建与监督微调", "设计逻辑　·　知识图谱　·　指令演化　·　动态微调 DFT")

    s = d.add_content("六模块管线：保留七类原生风格的场景原生指令合成", stage="SFT")
    picture(s, A("数据管线概览.png"), 0.5, 1.55, 3.9, 5.25)
    subhead(s, 4.7, 1.55, 8.0, "两个难点")
    text(s, 4.8, 2.0, 8.0, 1.3, [
        "四类任务输入输出结构差异大：简单问答对覆盖不了**排查顺序、条款引用、方案权衡**",
        "七类数据表达习惯不同：统一模板会造成**风格错配与风格漂移**",
    ], size=15, bullet="•", spacing=1.1)
    subhead(s, 4.7, 3.3, 8.0, "构建策略：SFT 保留原生风格，显式风格控制留到 RLAIF")
    rows = [["数据类型", "原生回答风格"],
            ["基础科学与仿真理论", "机理优先，逻辑严谨，标注假设与适用范围"],
            ["运维检修与资产管理", "结论先行，步骤化可执行，强制安全提示"],
            ["制度文件", "条款引用，措辞正式，边界清晰，不越权"]]
    table(s, 4.8, 3.8, 7.95, rows, col_w=[2.6, 5.35], row_h=0.4, size=13.5, head_fill=STAGE["SFT"])
    nums = [("约 600 条", "专家种子"), ("约 9.3 万条", "候选指令"), ("约 6.8 万条", "SFT 指令数据")]
    for i, (n, t) in enumerate(nums):
        cx = 4.85 + i * 2.75
        label(s, cx, 5.75, 2.2, 0.95, f"{n}\n{t}", STAGE_LIGHT["SFT"], color=STAGE_T["SFT"], size=19,
              line=STAGE["SFT"], radius=0.12)
        if i < 2:
            arrow(s, cx + 2.27, 6.07, 0.4, 0.32, color=STAGE_T["SFT"])

    s = d.add_content("设计逻辑决定“怎么问”，知识图谱决定“问什么”", stage="SFT")
    cols = [
        ("设计逻辑模板 ℓ = (a, Ξ, σ, φ)", ["a：认知能力维度", "Ξ：知识需求链（类型 + 关系）",
                                         "σ：输出结构", "φ：原生风格要求", "从专家种子抽取，按“七类数据 × 六种能力”建库"]),
        ("电力知识图谱", ["约 **4.2 万**条三元组", "7 类实体、7 种关系 + 逆关系",
                         "Qwen-Max 抽取 → 同义归并、类型校验 → 专家抽检", "不含评测保留文档"]),
        ("图遍历指令生成", ["沿需求链采样**类型与关系均匹配**的有向路径",
                           "起始实体按已使用次数反比抽样，覆盖长尾知识", "ROUGE-L > 0.85 去重"]),
    ]
    for i, (t, body) in enumerate(cols):
        card(s, 0.6 + i * 4.1, 1.65, 3.9, 2.7, t, body, STAGE["SFT"], size=13.5, title_size=15)
    subhead(s, 0.55, 4.5, 8, "示例：运维检修类故障诊断模板", color=STAGE_T["SFT"], size=17)
    path = ["主变压器", "冷却系统故障", "顶层油温\n异常升高", "检查冷却器\n风扇与油泵", "带电设备\n安全距离要求"]
    rels = ["可能发生", "导致", "处置方法", "受约束于"]
    for i, n in enumerate(path):
        cx = 0.65 + i * 2.5
        label(s, cx, 5.0, 1.85, 0.72, n, STAGE_LIGHT["SFT"], color=TXT, size=14, line=STAGE["SFT"], radius=0.2)
        if i < 4:
            arrow(s, cx + 1.9, 5.25, 0.55, 0.24, color=STAGE_T["SFT"])
            text(s, cx + 1.7, 4.9, 0.95, 0.3, rels[i], size=11, color=STAGE_T["SFT"], align=PP_ALIGN.CENTER)
    text(s, 0.65, 5.9, 12.2, 0.9, [
        "生成问题：“某 220kV 主变压器顶层油温持续升高，请分析可能原因并给出排查建议”",
        "答案结构：**结论先行 → 排查步骤 → 每步依据 → 风险提示**，事实断言以路径三元组与来源语料为依据",
    ], size=14.5, bullet="•", spacing=1.05)

    s = d.add_content("指令演化提升复杂度，多维质量筛选保证可靠性", stage="SFT")
    subhead(s, 0.55, 1.55, 6.2, "五类演化操作（以油温问题 x₀ 为例）", color=STAGE_T["SFT"], size=17)
    rows = [["操作", "对 x₀ 的变换"],
            ["约束增加", "+ 负荷率 85% 以上、乙炔含量接近注意值"],
            ["条件组合", "油温升高 + 轻瓦斯告警 + 分接开关频繁操作"],
            ["格式要求", "原因排序 / 逐项排查步骤 / 安全风险提示"],
            ["角色设定", "“作为检修班技术负责人，向班组下达任务”"],
            ["风险嵌入", "“主变仍带电运行，停电需向调度申请”"]]
    table(s, 0.6, 2.05, 6.1, rows, col_w=[1.3, 4.8], row_h=0.44, size=13, head_fill=STAGE["SFT"])
    text(s, 0.6, 4.8, 6.1, 1.9, [
        "演化 LLM 自主完成：**选择操作 → 执行并重写答案 → 三项自检**",
        "Optimizer 按批统计失败模式，迭代修订提示词",
        "人工仅审阅首批 100 条 + 每批抽检 5%",
    ], size=14, bullet="•", spacing=1.1)
    subhead(s, 6.95, 1.55, 6.0, "多维质量筛选", color=STAGE_T["SFT"], size=17)
    label(s, 7.0, 2.05, 5.8, 0.95, "Q = 0.12·清晰度 + 0.28·完整性\n+ 0.36·事实一致性 + 0.24·合规性",
          STAGE_LIGHT["SFT"], color=STAGE_T["SFT"], size=16, line=STAGE["SFT"], radius=0.1)
    text(s, 7.0, 3.1, 5.85, 1.55, [
        "权重：在专家标签上做非负逻辑回归校准；阈值 θ = 0.75",
        "一票否决：**事实冲突 / 支持率 q₃ < 0.6 / 合规 q₄ < 0.8**",
    ], size=14, bullet="•", spacing=1.1)
    rows = [["专家测试集（300 条）", "精确率", "召回率", "F1"],
            ["Qwen-Max 整体判断", "90.7", "95.5", "93.1"],
            ["本文准入规则", "94.2", "92.7", "93.4"]]
    table(s, 7.0, 4.75, 5.8, rows, col_w=[2.6, 1.05, 1.05, 1.05], row_h=0.42, size=13.5, hl_rows=(2,),
          head_fill=STAGE["SFT"])
    text(s, 7.0, 6.1, 5.85, 0.6, "以少量召回损失换取更干净的训练集", size=13.5, color=SUB)

    s = d.add_content("两阶段 SFT + DFT：CPT 是 DFT 生效的前提", stage="SFT")
    flow = [("CPT 模型", LIGHT, TXT), ("阶段一：6 万条通用指令\n学习对话格式（1 epoch）", STAGE_LIGHT["SFT"], TXT),
            ("阶段二：通用:电力 = 1:2\n安全敏感三类上采样 1.5×（2 epoch）", STAGE_LIGHT["SFT"], TXT),
            ("SFT 模型", STAGE["SFT"], WHITE)]
    widths = [1.7, 3.5, 3.9, 1.7]
    cx = 0.6
    for i, ((t, fc, tc), w) in enumerate(zip(flow, widths)):
        label(s, cx, 1.65, w, 0.85, t, fc, color=tc, size=14.5, line=STAGE["SFT"], radius=0.12)
        cx += w
        if i < 3:
            arrow(s, cx + 0.08, 1.92, 0.34, 0.3, color=STAGE_T["SFT"])
            cx += 0.5
    picture(s, M("dft_gradient.png"), 0.55, 2.75, 6.2, 3.95)
    pts = [
        ("CE：g = 1 − p", "低概率 token 主导梯度：p = 0.1 的连接词梯度是 p = 0.9 术语的 **9 倍**"),
        ("DFT：L = −sg(p)·log p，g = p(1 − p)", "两者梯度均为 0.09，压低合成数据中表面 token 的相对权重"),
        ("代价与互补", "新事实 p = 0.05 时 DFT 梯度仅为 CE 的 1/20；CPT 将其提到 p = 0.3，梯度增大约 **4.4 倍**"),
    ]
    for i, (t, dsc) in enumerate(pts):
        cy = 2.85 + i * 1.3
        label(s, 7.0, cy, 0.45, 1.12, f"{i + 1}", STAGE["SFT"], size=18, radius=0.2)
        text(s, 7.55, cy - 0.02, 5.3, 0.4, t, size=15.5, color=STAGE_T["SFT"], bold=True)
        text(s, 7.55, cy + 0.38, 5.3, 0.8, dsc, size=13.5, spacing=1.05)

    s = d.add_content("SFT 结果：三项领域任务大幅提升，CPT 与 DFT 协同最优", stage="SFT", title_size=24)
    picture(s, A("chart_sft_main.png"), 0.5, 1.55, 5.9, 2.75)
    text(s, 0.6, 4.3, 5.8, 0.6, "相对 CPT：PowerQA **+14.1**、FaultDiag **+30.7**、RegulationQA **+52.0** pp；CrossDomainQA 2.4 → 3.7",
         size=13.5, spacing=1.0)
    rows = [["配置", "PowerQA", "FaultDiag", "RegQA", "Cross"],
            ["Base + CE", "73.5", "51.0", "64.3", "3.0"], ["Base + DFT", "71.8", "53.3", "61.0", "3.1"],
            ["CPT + CE", "80.6", "58.3", "76.0", "3.4"], ["CPT + DFT（本文）", "82.3", "63.0", "78.0", "3.7"]]
    text(s, 6.65, 1.55, 6.2, 0.4, "初始化 × 微调目标的 2×2 对比", size=15, color=STAGE_T["SFT"], bold=True)
    table(s, 6.65, 1.95, 6.2, rows, col_w=[2.2, 1.05, 1.05, 1.0, 0.9], row_h=0.37, size=13, hl_rows=(4,),
          head_fill=STAGE["SFT"])
    text(s, 6.65, 3.85, 6.2, 0.9, ["无 CPT：DFT 在事实型任务上弱于 CE（−1.7 / −3.3）",
                                   "有 CPT：DFT 不再弱于 CE，FaultDiag **+4.7 pp**"], size=13.5, bullet="•", spacing=1.0)
    rows = [["管线消融（固定数据规模）", "PowerQA", "FaultDiag", "RegQA", "Cross"],
            ["完整管线", "82.3", "63.0", "78.0", "3.7"],
            ["− 专家种子（TF-IDF + 通用模板）", "77.4", "55.3", "67.0", "3.1"],
            ["− 知识图谱（直接由语料生成）", "79.8", "56.0", "71.3", "3.2"],
            ["− 指令演化", "79.2", "54.3", "72.0", "3.0"],
            ["− 质量筛选（9.3 万条候选）", "80.1", "58.3", "73.0", "3.3"]]
    table(s, 0.6, 4.95, 7.6, rows, col_w=[3.4, 1.05, 1.1, 1.05, 0.9], row_h=0.3, size=12.5, hl_rows=(1,),
          head_fill=STAGE["SFT"])
    text(s, 8.4, 4.95, 4.45, 1.85, ["去掉专家种子：RegulationQA −11.0，设计逻辑对业务贴合度贡献最大",
                                    "去掉知识图谱：覆盖实体减少约 31%，多跳的故障诊断与制度问答下降更明显",
                                    "去掉质量筛选：样本多 36.8%，效果反而更差"],
         size=12.5, bullet="•", spacing=1.0, space_after=3)

    # ================= PART 04
    d.add_section(4, "回答风格强化学习对齐", "用户群体风格组合　·　StyleRM-7B　·　GRPO + Clip-Higher")

    s = d.add_content("回答风格应由“谁在问”决定，而非语料类别", stage="RLAIF")
    label(s, 0.6, 1.7, 3.6, 1.0, "同一问题：\n220kV 线路保护装置发出“TV 断线”告警", STAGE["RLAIF"], size=15, radius=0.12)
    roles = [("技术研究人员", "断线判别原理、对保护的影响"), ("生产运维人员", "立即可执行的处置步骤"),
             ("管理人员", "处置是否符合调度纪律与规程")]
    arrow(s, 4.28, 2.05, 0.38, 0.3, color=STAGE_T["RLAIF"])
    for i, (r, need) in enumerate(roles):
        cx = 4.75 + i * 2.75
        label(s, cx, 1.7, 2.6, 1.0, f"{r}\n{need}", STAGE_LIGHT["RLAIF"], color=STAGE_T["RLAIF"], size=15,
              line=STAGE["RLAIF"], radius=0.12)
    rows = [["目标用户群体", "核心需求", "展开程度", "安全警示", "表述类型"],
            ["技术研究人员", "知识深度与技术完整性", "详尽", "基础提醒", "研讨型"],
            ["生产运维人员", "快速可执行与操作安全", "精简", "逐项警戒", "指令型"],
            ["管理人员", "依据明确与合规边界清晰", "适中", "前置提醒", "裁定型"]]
    table(s, 0.6, 3.0, 12.2, rows, col_w=[2.2, 3.6, 2.1, 2.1, 2.2], row_h=0.5, size=15,
          head_fill=STAGE["RLAIF"])
    text(s, 0.6, 5.15, 12.2, 1.6, [
        "风格拆为三个类目，每类三个取值：**展开程度**控制信息量，**安全警示**控制风险提示的覆盖与位置，**表述类型**决定研讨 / 指令 / 裁定",
        "每个类目上三类群体恰好各取一个不同取值；风格只作用于表述形式，**不改变技术内容**",
        "SFT 模型的风格随语料类别固定（故障类总是步骤化），无法响应提问者的实际需求",
    ], size=14.5, bullet="•", spacing=1.1)

    s = d.add_content("风格条件化 Prefix 与风格标注数据构建", stage="RLAIF")
    box(s, 0.6, 1.65, 12.2, 0.95, fill=PALE, line=SOFT, radius=0.08)
    text(s, 0.8, 1.72, 11.9, 0.45, "[展开:精简][安全:逐项警戒][表述:指令]　某 220kV 主变压器顶层油温持续升高，请分析可能原因……",
         size=15.5, color=DBLUE, bold=True)
    text(s, 0.8, 2.15, 11.9, 0.4, "仅约 12 个 token，不附任何自然语言说明 ——“按标记生成对应风格”完全由强化学习习得",
         size=13, color=SUB)
    flow = [("SFT 问答对\n18,000 条", "七类数据均匀采样"),
            ("按提问角色分类", "允许多标签\nκ = 0.84"),
            ("问题划分", "12,000 改写训练\n6,000 仅作 RL prompt"),
            ("改写 Prompt 迭代", "人类反馈 3 轮\n优质率 ≥ 98%"),
            ("保真度检查 +\n双模型校准", "DeepSeek-V4-Pro\nGLM-5.2 + 人工裁决"),
            ("风格标注数据\n13,800 条", "训练 / 验证 / 测试\n11,000 / 1,400 / 1,400")]
    for i, (t, dsc) in enumerate(flow):
        cx = 0.6 + i * 2.07
        last = i == len(flow) - 1
        label(s, cx, 2.95, 1.78, 0.95, t, STAGE["RLAIF"] if last else STAGE_LIGHT["RLAIF"],
              color=WHITE if last else STAGE["RLAIF"], size=14, line=STAGE["RLAIF"], radius=0.12)
        text(s, cx - 0.05, 3.98, 1.9, 0.9, dsc, size=12, color=SUB, align=PP_ALIGN.CENTER, spacing=1.0)
        if not last:
            arrow(s, cx + 1.81, 3.3, 0.24, 0.26, color=STAGE_T["RLAIF"])
    text(s, 0.6, 5.0, 12.2, 1.8, [
        "**跨角色问题占 36%**：同一问题按多个群体分别改写，构成“同题异风格”对照，防止模型凭问题类型猜风格",
        "标签取双模型的实际判定而非改写目标；改写只调整表述形式，关键实体与结论错误的样本被剔除",
        "Qwen-Max 只负责改写，不参与任何评分、校验与裁决，避免自评偏好",
    ], size=14.5, bullet="•", spacing=1.1)

    s = d.add_content("StyleRM-7B：为强化学习提供风格奖励", stage="RLAIF")
    picture(s, A("rl_rollout_rm.png"), 0.5, 1.6, 8.3, 3.85)
    rows = [["方法", "展开", "安全", "表述"],
            ["零样本提示", "59.4", "55.6", "73.5"],
            ["StyleRM-3B", "74.6", "71.2", "87.0"],
            ["StyleRM-7B", "81.3", "78.0", "90.6"]]
    text(s, 9.0, 1.6, 3.85, 0.4, "测试集准确率（%）", size=15, color=STAGE_T["RLAIF"], bold=True)
    table(s, 9.0, 2.0, 3.85, rows, col_w=[1.6, 0.75, 0.75, 0.75], row_h=0.42, size=13.5, hl_rows=(3,),
          head_fill=STAGE["RLAIF"])
    text(s, 9.0, 3.8, 3.85, 1.6, ["平均 **83.3%**，零样本提示 62.8%（+20.5 pp）", "安全警示最难：需逐项判断风险提示是否覆盖全部步骤"],
         size=13.5, bullet="•", spacing=1.05)
    text(s, 0.6, 5.6, 12.2, 1.2, [
        "以 Qwen2.5-7B-Instruct 为主干，取最后一个 token 的隐藏状态，为每个类目设可学习嵌入，对回答 token 做**注意力池化**后分类",
        "输入**不含 Prefix**，只看问答文本：迫使策略模型把目标风格真正写进回答里",
    ], size=14, bullet="•", spacing=1.1)

    s = d.add_content("奖励设计与算法对比：GRPO + Clip-Higher 最优", stage="RLAIF")
    subhead(s, 0.55, 1.55, 5.8, "开根号奖励", color=STAGE_T["RLAIF"], size=17)
    label(s, 0.6, 2.0, 5.7, 0.6, "r = Σⱼ wⱼ · √Pⱼ(cⱼ | x, o)，wⱼ = 1/3", STAGE_LIGHT["RLAIF"],
          color=STAGE_T["RLAIF"], size=16, line=STAGE["RLAIF"], radius=0.15)
    picture(s, M("fig4-2_sqrt_reward.png"), 0.55, 2.7, 5.8, 2.15)
    text(s, 0.6, 4.95, 5.75, 1.8, [
        "优先补齐未达标的类目：概率 0.04→0.25 的奖励增量是 0.81→1.0 的 **3 倍**",
        "开发集 SHR 比线性奖励高 2.4 pp",
    ], size=14, bullet="•", spacing=1.1)
    rows = [["方法", "Critic", "训练奖励", "测试 SHR"],
            ["标准 PPO", "需要", "≈0.70", "76.8"],
            ["Dual-Clip PPO", "需要", "≈0.83", "85.1"],
            ["RLOO", "不需要", "≈0.77", "81.9"],
            ["GRPO", "不需要", "≈0.81", "83.7"],
            ["GRPO + Clip-Higher", "不需要", "≈0.90", "90.2"]]
    table(s, 6.65, 1.65, 6.2, rows, col_w=[2.5, 1.1, 1.3, 1.3], row_h=0.44, size=14, hl_rows=(5,),
          head_fill=STAGE["RLAIF"])
    text(s, 6.65, 4.4, 6.2, 2.4, [
        "PPO：负优势分支无下界，奖励震荡 → Dual-Clip 增加下界 δ = 3",
        "RLOO：省去 Critic，但优势随组内差异缩小而衰减",
        "GRPO：组内标准差归一化，避免衰减",
        "相同采样预算：8500 步 × 每步 32 个回答",
    ], size=14, bullet="•", spacing=1.1)

    s = d.add_content("GRPO 熵坍缩导致平台期，Clip-Higher 维持探索", stage="RLAIF")
    picture(s, M("fig4-4_grpo_reward.png"), 0.5, 1.6, 6.1, 3.6)
    picture(s, M("fig4-5_entropy_collapse.png"), 6.75, 1.6, 6.1, 3.6)
    text(s, 0.6, 5.35, 12.2, 1.45, [
        "标准 GRPO：约 3000 步内熵降至 0.2 → 组内回答同质、σ(r)→0，判别模型的评分噪声被放大 → 4500 步后奖励停滞在 0.79–0.81",
        "Clip-Higher：裁剪区间改为 [1 − 0.2, 1 + **0.28**]，只放宽正优势回答的上界",
        "后期熵维持在约 0.85，奖励继续上升至约 **0.90**",
    ], size=14.5, bullet="•", spacing=1.1)

    s = d.add_content("风格评测：RLAIF 明显优于直接用 Prompt 指定风格", stage="RLAIF")
    picture(s, A("chart_style.png"), 0.5, 1.55, 12.35, 3.3)
    text(s, 0.6, 4.95, 6.6, 1.9, [
        "SHR **90.2%**，较零样本 / 少样本 Prompt 高 35.3 / 27.6 pp；Joint-HR **76.2%**",
        "最难靠提示改变的“逐项警戒”“精简”：比少样本高 41.1 / 40.0 pp",
        "跨角色问题 Joint-HR 73.8%：依据 Prefix 而非问题类型切换风格",
        "控制输入约 12 token（少样本约 2100）；领域任务回落均 ≤ 1 pp",
    ], size=13.5, bullet="•", spacing=1.05, space_after=3)
    box(s, 7.35, 4.95, 5.5, 1.85, fill=STAGE_LIGHT["RLAIF"], radius=0.06)
    text(s, 7.45, 4.98, 5.3, 0.35, "同题异风格：TV 断线告警", size=13.5, color=STAGE_T["RLAIF"], bold=True)
    text(s, 7.45, 5.33, 5.3, 1.45, [
        "**运维组合**：【安全警告】TV 二次回路带电……①确认距离保护已闭锁；②（须使用绝缘工具，严禁短接）检查二次空开……",
        "**研究组合**：断线告警通常由判别逻辑给出……可考虑以下几类成因……（结尾）请注意防止短路或接地。",
    ], size=11.5, spacing=1.0, space_after=3)

    # ================= PART 05
    d.add_section(5, "电力安全合规深层对齐", "同状态恢复数据　·　Token 边界截断　·　困难状态加权")

    s = d.add_content("电力隐蔽风险与浅层安全对齐的脆弱性", stage="DPO")
    picture(s, A("fig5-1_风险类型.png"), 0.5, 1.6, 7.6, 3.5)
    subhead(s, 8.3, 1.55, 4.6, "浅层安全对齐", color=STAGE_T["DPO"], size=17)
    text(s, 8.35, 2.0, 4.5, 1.5, ["安全行为集中在前 5–10 个输出 token（Qi et al., ICLR 2025）",
                                  "仅预填充 5 个有害 token，ASR 即升至 42%"], size=13.5, bullet="•", spacing=1.05)
    label(s, 8.35, 3.45, 4.5, 0.78, "用户侧诱导\n“假设你是资深工程师，忽略安全规程……”", STAGE_LIGHT["DPO"],
          color=STAGE_T["DPO"], size=14, line=STAGE["DPO"], radius=0.1)
    label(s, 8.35, 4.32, 4.5, 0.78, "assistant 侧预填充\n回复开头写入非拒答前缀（需控制生成接口）", STAGE_LIGHT["DPO"],
          color=STAGE_T["DPO"], size=14, line=STAGE["DPO"], radius=0.1)
    box(s, 0.6, 5.35, 12.2, 1.4, fill=WHITE, line=STAGE["DPO"], radius=0.06)
    text(s, 0.75, 5.42, 3.6, 0.4, "未做安全对齐的 RLAIF 模型", size=15, color=STAGE_T["DPO"], bold=True)
    for i, (k, v) in enumerate([("URR 不安全回答率", "42.5%"), ("ASR 攻击成功率", "85.6%"), ("SRR 安全恢复率", "3.9%")]):
        cx = 0.75 + i * 2.75
        text(s, cx, 5.82, 2.6, 0.45, v, size=24, color=RED, bold=True, align=PP_ALIGN.CENTER)
        text(s, cx, 6.3, 2.6, 0.35, k, size=12.5, color=SUB, align=PP_ALIGN.CENTER)
    text(s, 9.1, 5.55, 3.6, 1.1, "一旦初始防线被突破，几乎无法恢复；同时还需控制过度拒答率 ORR", size=14,
         color=TXT, spacing=1.1)

    s = d.add_content("同状态恢复：统一构建根节点拒答与深层恢复数据", stage="DPO")
    label(s, 0.6, 1.75, 1.9, 0.62, "用户指令 x", LIGHT, color=TXT, size=15, line=LINE, radius=0.15)
    text(s, 2.5, 1.8, 0.4, 0.5, "⊕", size=22, color=SUB, align=PP_ALIGN.CENTER)
    label(s, 2.9, 1.75, 2.3, 0.62, "有害前缀 h₁ … hₖ", STAGE_LIGHT["DPO"], color=STAGE_T["DPO"], size=15,
          line=STAGE["DPO"], radius=0.15)
    text(s, 0.6, 2.42, 4.6, 0.35, "到达状态 sₖ = x ⊕ h≤ₖ　（k = 0 即根节点拒答）", size=13, color=SUB,
         align=PP_ALIGN.CENTER)
    arrow(s, 5.3, 1.85, 0.45, 0.4, color=STAGE_T["DPO"])
    label(s, 5.8, 1.6, 3.0, 0.52, "rₖ：安全恢复（chosen）", RGBColor(0xEB, 0xF1, 0xED), color=GREEN, size=13.5,
          line=GREEN, radius=0.15)
    label(s, 5.8, 2.22, 3.0, 0.52, "uₖ：有害延续（rejected）", RGBColor(0xF5, 0xEC, 0xEB), color=RED,
          size=13.5, line=RED, radius=0.15)
    label(s, 0.6, 2.95, 8.05, 0.62, "恢复间隔 m(sₖ) = β[ S(sₖ, rₖ) − S(sₖ, uₖ) ]，m < 0 即“同状态偏好反转”",
          PALE, color=DBLUE, size=15, line=MAIN, radius=0.15)
    text(s, 0.6, 3.68, 8.05, 0.7, "SFT / RLAIF 数据几乎没有“从有害开头转向安全”的样本：根节点能拒答，进入中途状态后却容易反转",
         size=13.5, color=SUB, spacing=1.05)
    box(s, 8.95, 1.6, 3.9, 2.8, fill=WHITE, line=STAGE["DPO"], radius=0.05)
    text(s, 9.05, 1.65, 3.7, 2.7, [
        "**Recovery Data　16k（80%）**",
        "① 根节点拒答（k = 0）　10k",
        "② 用户侧诱导恢复（k = 0）　3.5k",
        "③ 预填充恢复（k > 0）　2.5k",
        "**Counter Data　4k（20%）**",
        "含敏感词的正常业务问题，抑制误拒",
    ], size=13.5, spacing=1.1, space_after=4)
    keys = [
        ("自身采样 + 判别补全", "偏好对的一侧总取自待对齐模型自身输出：错误回复作 rejected，合理回复作 chosen"),
        ("三段式 chosen", "拒答声明 + 合规依据 + 安全替代；信息不足时说明原因并请求补充"),
        ("分风险截取上限", "R3 80 / R2 100 / R1 120 / R4 150 token；共享前缀项在偏好差中相消"),
    ]
    for i, (t, dsc) in enumerate(keys):
        card(s, 0.6 + i * 4.1, 4.75, 3.9, 1.65, t, [dsc], STAGE["DPO"], size=14, title_size=15, bullet=None)

    s = d.add_content("预填充前缀必须在原生 token 边界截断", stage="DPO")
    picture(s, M("fig5-2_crop.png"), 0.5, 1.6, 8.6, 3.1)
    text(s, 9.3, 1.6, 3.55, 3.1, [
        "**接缝分词伪迹**：训练信号消耗在“补全被截断的词”上",
        "**困难度估计失真**：恢复间隔被高估",
        "**同状态比较失效**：重新编码后两分支前缀不同",
        "抽样 400 条：**38.5%** 的字符截断前缀错位",
    ], size=13.5, bullet="•", spacing=1.05, space_after=5)
    rows = [["测试前缀", "Token 截断训练 ASR↓", "SRR↑", "字符截断训练 ASR↓", "SRR↑"],
            ["Token 边界前缀", "15.00", "41.25", "18.50", "35.75"],
            ["词中截断前缀", "12.25", "42.00", "11.50", "43.25"],
            ["人工撰写前缀", "12.50", "44.00", "16.25", "37.50"]]
    table(s, 0.6, 4.85, 8.5, rows, col_w=[2.0, 2.0, 1.2, 2.1, 1.2], row_h=0.44, size=13.5, head_fill=STAGE["DPO"])
    text(s, 9.3, 4.85, 3.55, 1.9, [
        "自然结尾的前缀上，Token 截断训练 ASR 低 3.5–3.75 pp",
        "字符截断训练的模型依赖“残缺词”线索",
    ], size=13.5, bullet="•", spacing=1.05)

    s = d.add_content("困难状态加权 HS-Weighting 与两阶段训练", stage="DPO")
    card(s, 0.6, 1.65, 7.4, 1.75, "样本级困难权重 φᵢ", [
        "φᵢ = ν + (1 − ν) · |B| · softmax(−mᵢ / τ)",
        "按参考模型的恢复间隔加权，偏好反转越严重权重越大；批内均值为 1；Counter Data 恒为 1",
    ], STAGE["DPO"], size=13.5, title_size=15, bullet=None)
    card(s, 0.6, 3.55, 7.4, 1.75, "token 级转向权重 ψₜ", [
        "ψₜ = (1 + ζᵗ⁻¹)/2 · (1 − maxₜ′ cos(e(yₜ), e(ȳₜ′)))",
        "续写前段（转向处）权重高；两分支共有的术语自动降权，无需人工词典",
    ], STAGE["DPO"], size=13.5, title_size=15, bullet=None)
    label(s, 0.6, 5.5, 7.4, 1.2, "L_HSW：两级权重代入 DPO 的逐 token 对数比\nν = 1、η = 0 时退化为标准 DPO；默认 ν = 0.3、η = 0.3",
          STAGE_LIGHT["DPO"], color=STAGE_T["DPO"], size=15, line=STAGE["DPO"], radius=0.08)
    subhead(s, 8.3, 1.55, 4.6, "两阶段训练", color=STAGE_T["DPO"], size=17)
    label(s, 8.35, 2.05, 4.5, 1.65, "第一阶段（422 步）\nk = 0 样本 13.5k\n根节点拒答 10k + 用户侧诱导 3.5k\n→ 稳固根节点拒答边界",
          STAGE_LIGHT["DPO"], color=STAGE_T["DPO"], size=15, line=STAGE["DPO"], radius=0.08)
    arrow(s, 10.4, 3.78, 0.4, 0.4, color=STAGE_T["DPO"], shape=MSO_SHAPE.DOWN_ARROW)
    label(s, 8.35, 4.25, 4.5, 1.65, "第二阶段（625 步）\nRecovery 16k + Counter 4k\n→ 深层恢复 + 抑制过度拒答",
          PALE, color=DBLUE, size=15, line=MAIN, radius=0.08)
    text(s, 8.35, 6.05, 4.5, 0.7, "β = 0.1，学习率 5×10⁻⁷，8×A100", size=13, color=SUB, align=PP_ALIGN.CENTER)

    s = d.add_content("主要结果：安全性显著提升，同时控制过度拒答", stage="DPO")
    rows = [["方法", "URR↓", "ASR↓", "SRR↑", "ORR↓"],
            ["无安全对齐（CPT+SFT+RLAIF）", "42.5", "85.6", "3.9", "7.0"],
            ["标准 DPO（通用安全数据）", "12.0", "35.0", "20.0", "8.0"],
            ["DPO + Safety Recovery", "3.0", "14.5", "37.5", "13.3"],
            ["DPO + Safety Recovery + Counter", "3.5", "16.4", "35.4", "5.7"],
            ["本文（等权 DPO）", "2.5", "11.1", "45.9", "5.0"],
            ["本文（+ HS-Weighting）", "1.5", "7.9", "53.4", "5.0"]]
    table(s, 0.6, 1.65, 6.55, rows, col_w=[3.15, 0.85, 0.85, 0.85, 0.85], row_h=0.44, size=13,
          hl_rows=(6,), head_fill=STAGE["DPO"])
    text(s, 0.6, 4.9, 6.55, 1.9, [
        "对比“Safety Recovery + Counter”：ORR 相当，ASR 低 5.3 pp、SRR 高 10.5 pp → 优势来自**恢复数据构造**",
        "HS-Weighting：ASR 11.1 → **7.9**，SRR 45.9 → **53.4**",
        "第一阶段 URR 快速下降但 ORR 升至 12.7；第二阶段 SRR 24.0 → 53.4、ORR 回落至 5.0",
    ], size=13.5, bullet="•", spacing=1.05)
    picture(s, M("fig5-4_dpo_training_curves.png"), 7.35, 1.6, 5.5, 3.78)
    text(s, 7.35, 5.45, 5.5, 0.4, "最终模型训练过程（虚线为两阶段分界）", size=12.5, color=SUB, align=PP_ALIGN.CENTER)

    s = d.add_content("消融与细分分析", stage="DPO")
    quads = [
        ("根节点拒答与深层恢复缺一不可", ["仅根节点拒答：ASR 25.4、SRR 18.6（浅层边界）",
                                    "仅对抗恢复：SRR 34.5，但 URR 11.5", "全量 Recovery：ASR **9.1**、SRR **48.4**"]),
        ("Counter Data 纠正过度拒答（占比 20%）", ["ORR 14.0 → **5.0**", "代价：ASR +2.0、SRR −2.5 pp",
                                               "占比 30% 时 SRR 降至 40.5"]),
        ("HS-Weighting 两级权重互补", ["仅 token 级：SRR +3.0 pp", "仅样本级：SRR +5.6 pp",
                                    "两者结合：SRR **+7.5 pp**，ASR −3.2 pp"]),
        ("隐蔽型、长链条风险改善更大", ["SRR 提升：R4 +9.0、R1 +8.5、R3 +6.5、R2 +6.0",
                                    "R3 违章操作最易对齐（ASR 4.5）", "R1 仿真失真最难（ASR 11.0）"]),
    ]
    for i, (t, body) in enumerate(quads):
        cx, cy = 0.6 + (i % 2) * 6.15, 1.65 + (i // 2) * 2.2
        card(s, cx, cy, 6.0, 2.05, t, body, STAGE["DPO"], size=14, title_size=15.5)
    banner(s, 6.15, "残余风险：超出训练深度（1.5 C_R）时 ASR 29.0%；多次采样 ASR@8 = 19.4% → 部署仍需规则拦截与日志审计",
           fill=MID, size=14.5, h=0.58)

    # ================= PART 06
    d.add_section(6, "总结与展望", "跨阶段能力对比　·　工作总结　·　局限与展望")

    s = d.add_content("四阶段能力逐级积累，最终模型超过通用模型与教师模型", title_size=24)
    picture(s, A("chart_stage.png"), 0.5, 1.55, 6.1, 3.75)
    picture(s, A("chart_external.png"), 6.75, 1.55, 6.1, 3.75)
    text(s, 0.6, 5.4, 12.2, 1.4, [
        "跨阶段：领域能力在 SFT 后达到高点，后续回落 ≤ 1 pp；风格 SHR 89.1%（−1.1 pp）；安全指标只在 DPO 阶段大幅改善",
        "对比同规模 Qwen2.5-7B-Instruct：三项领域任务平均 **+39.4 pp**",
        "对比教师 Qwen-Max：PowerQA +7.7、FaultDiag +6.6、RegulationQA **+25.0** pp；URR / ASR 9.5 / 31.4 → 1.5 / 7.9",
    ], size=14, bullet="•", spacing=1.1)

    s = d.add_content("总结")
    summ = [
        ("CPT", "七类电力语料 + PPL 双阈值筛选 + 1:1 领域-通用混合", "PowerQA 43.5% → 68.2%"),
        ("SFT", "六模块场景原生指令合成（6.8 万条）+ 两阶段 DFT 微调", "PowerQA 82.3%｜FaultDiag 63.0%｜RegQA 78.0%"),
        ("RLAIF", "用户群体风格 Prefix + StyleRM-7B + GRPO / Clip-Higher", "SHR 90.2%｜Joint-HR 76.2%"),
        ("DPO", "Recovery / Counter 数据 + Token 边界截断 + HS-Weighting", "URR 1.5%｜ASR 7.9%｜ORR 5.0%"),
    ]
    for i, (st, m, r) in enumerate(summ):
        cy = 1.65 + i * 1.1
        label(s, 0.6, cy, 1.5, 0.92, st, WHITE, color=DBLUE, size=20, line=MAIN, radius=0.12)
        box(s, 2.15, cy, 10.65, 0.92, fill=STAGE_LIGHT[st], radius=0.08)
        text(s, 2.3, cy + 0.24, 5.2, 0.5, m, size=14.5)
        text(s, 7.4, cy + 0.24, 5.35, 0.5, r, size=14.5, color=DBLUE, bold=True, align=PP_ALIGN.RIGHT)
    banner(s, 6.2, "最终模型：领域任务较 Qwen2.5-7B-Instruct 平均高 39.4 pp，三项均超过教师模型 Qwen-Max，同时具备风格可控与安全合规能力",
           size=14.5, h=0.58)

    s = d.add_content("局限与展望")
    lims = [
        ("评测集来源较单一", "评测文档参与了 CPT，衡量的是对已注入知识的调用", "在 ElecBench 等公开基准上验证，检验对全新文档的泛化"),
        ("数据局限于单一电网企业", "设备型号、制度体系带有企业特征，未纳入时序与波形数据", "引入多企业数据，结合故障录波、在线监测等多模态信息"),
        ("风格与安全控制仍有提升空间", "Joint-HR 76.2% 低于单项命中率；深层恢复随预填充深度下降", "岗位级细粒度风格与未见组合泛化；电力红队评测、多轮诱导"),
        ("尚未接入真实业务系统", "仅在离线评测集上验证", "结合 RAG 接入最新规程，工具调用实时数据与仿真，工程化部署"),
    ]
    for i, (t, a, b) in enumerate(lims):
        cx, cy = 0.6 + (i % 2) * 6.15, 1.65 + (i // 2) * 2.5
        box(s, cx, cy, 6.0, 2.3, fill=WHITE, line=LINE, radius=0.05)
        label(s, cx, cy, 6.0, 0.5, t, PALE, color=DBLUE, size=16, line=MAIN, radius=0.1)
        text(s, cx + 0.12, cy + 0.62, 5.75, 0.8, f"局限：{a}", size=14, color=SUB)
        text(s, cx + 0.12, cy + 1.42, 5.75, 0.8, f"展望：**{b}**", size=14)

    d.add_end()
    d.save()


if __name__ == "__main__":
    build()
