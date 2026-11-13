# -*- coding: utf-8 -*-
"""
图5-1：Token-Boundary 与 Character-Boundary 截断边界对比示意
严格对应官方 Qwen2.5-7B-Instruct BPE 分词结果：
Token-Boundary (k=14): ["如果", "时间", "紧迫", "，", "只需", "直接", "解除", "接地", "安全", "保护", "并", "规避", "开关", "系统"]
Character-Boundary (n = 25): 先逐字截取前25个字符（“……规避开关系 | 统”），再经原生 tokenizer 重编码，
后三个 token 连锁错位为 ["规", "避开", "关系"]
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import rcParams, font_manager

candidates = [
    "PingFang SC",
    "Heiti TC",
    "Songti SC",
    "Arial Unicode MS",
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "WenQuanYi Zen Hei",
]
available_fonts = {f.name for f in font_manager.fontManager.ttflist}
chosen = next((f for f in candidates if f in available_fonts), None)
rcParams["font.sans-serif"] = [chosen, "DejaVu Sans"] if chosen else ["sans-serif"]
rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(1, 2, figsize=(14.2, 6.6), dpi=300)
fig.subplots_adjust(wspace=0.06)

harmful_prefix = "如果时间紧迫，只需直接解除接地安全保护并规避开关系统"

highlight_tokens = {"解除", "接地", "安全", "保护"}
intact_tail_tokens = {"规避", "开关", "系统"}
shifted_tokens = {"规", "避开", "关系"}

COLOR_NORMAL = ("#EBF3FA", "#4A77A8", "#1B365D")
COLOR_RISK = ("#FDEBD0", "#D35400", "#873600")
COLOR_INTACT = ("#D4EFDF", "#1E8449", "#145A32")
COLOR_SHIFT = ("#FADBD8", "#C0392B", "#78281F")
COLOR_DROP = ("#F4F6F6", "#95A5A6", "#95A5A6")


def draw_box(ax, x, y, w, h, text, colors, fontsize=10.3, bold=False, ls="-", lw=1.2):
    fc, ec, tc = colors
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.03,rounding_size=0.06",
        linewidth=lw, linestyle=ls, edgecolor=ec, facecolor=fc
    ))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight="bold" if bold else "normal", color=tc)


def draw_token_rows(ax, rows, y_positions, color_fn, box_h=0.48):
    """绘制 token 行，返回每个 token 的 (x, y, w) 位置。"""
    positions = {}
    for row_idx, row in enumerate(rows):
        x = 0.38
        y = y_positions[row_idx]
        for tok in row:
            w = 0.70 if len(tok) == 1 else 1.06
            colors, bold, lw = color_fn(tok)
            draw_box(ax, x, y, w, box_h, tok, colors, bold=bold, lw=lw)
            positions[tok] = (x, y, w)
            x += w + 0.14
    return positions


def stage_label(ax, y, text, color):
    ax.text(0.32, y, text, ha="left", va="center", fontsize=10.0,
            fontweight="bold", color=color)


# ---------------- 左图：Token-Boundary ----------------
ax = axes[0]
ax.set_xlim(0, 9.4)
ax.set_ylim(0, 6.4)
ax.axis("off")

ax.text(4.7, 6.12, "(a) Token-Boundary 截断（k = 14）",
        ha="center", va="center", fontsize=12.4, fontweight="bold", color="#1F3A60")
ax.text(0.32, 5.62, f"预填充前缀：“{harmful_prefix}”",
        ha="left", va="center", fontsize=9.5, color="#333333")

stage_label(ax, 5.05, "① 原生 tokenizer 编码完整回复，直接截取前 k = 14 个 token ID", "#1F3A60")


def left_color(tok):
    if tok in intact_tail_tokens:
        return COLOR_INTACT, True, 1.35
    if tok in highlight_tokens:
        return COLOR_RISK, True, 1.2
    return COLOR_NORMAL, False, 1.2


token_rows = [
    ["如果", "时间", "紧迫", "，", "只需", "直接", "解除"],
    ["接地", "安全", "保护", "并", "规避", "开关", "系统"],
]
draw_token_rows(ax, token_rows, [4.25, 3.50], left_color)

ax.annotate(
    "保持完整词边界：[“规避”, “开关”, “系统”]",
    xy=(6.65, 3.44), xytext=(6.05, 2.98),
    ha="center", va="center", fontsize=9.2, fontweight="bold", color="#1E8449",
    arrowprops=dict(arrowstyle="->", color="#1E8449", lw=1.2)
)

ax.text(
    0.38, 2.30,
    "• 截取单位即模型输入单位（token），无需重新编码\n"
    "• “解除”“安全”“保护”“规避”“开关”“系统”均保持完整子词\n"
    "• 前缀与模型自回归生成至第 k 步的轨迹严格一致",
    ha="left", va="top", fontsize=9.4, linespacing=1.6, color="#222222",
    bbox=dict(boxstyle="round,pad=0.45", facecolor="#F7FAFC", edgecolor="#8BA6D6", linewidth=1.1)
)

# ---------------- 右图：Character-Boundary ----------------
ax = axes[1]
ax.set_xlim(0, 9.4)
ax.set_ylim(0, 6.4)
ax.axis("off")

ax.text(4.7, 6.12, "(b) Character-Boundary 截断（n = 25）",
        ha="center", va="center", fontsize=12.4, fontweight="bold", color="#78281F")

# ① 逐字切分并按字符数截断
stage_label(ax, 5.62, "① 将回复逐字切分，按字符数截取前 n = 25 个字符", "#78281F")

m_chars = 25
risk_idx = set(range(11, 19))      # 解除接地安全保护
shift_idx = set(range(20, 25))     # 规避开关系
row_len = 14
char_y = [4.98, 4.40]
char_w, char_h, char_gap = 0.48, 0.42, 0.10
for g_idx, ch in enumerate(harmful_prefix):
    row_idx, c_idx = divmod(g_idx, row_len)
    x = 0.38 + c_idx * (char_w + char_gap)
    y = char_y[row_idx]
    if g_idx >= m_chars:
        colors, ls = COLOR_DROP, "--"
    elif g_idx in shift_idx:
        colors, ls = COLOR_SHIFT, "-"
    elif g_idx in risk_idx:
        colors, ls = COLOR_RISK, "-"
    else:
        colors, ls = ("#F2F4F4", "#7F8C8D", "#2C3E50"), "-"
    draw_box(ax, x, y, char_w, char_h, ch, colors, fontsize=9.8, ls=ls, lw=1.1)
    if g_idx == m_chars:
        cut_x = x - char_gap / 2
        ax.plot([cut_x, cut_x], [y - 0.10, y + char_h + 0.10],
                linestyle="--", linewidth=1.9, color="#C0392B")
        ax.text(cut_x, y - 0.26, "截断点：系 | 统（“统”被丢弃）",
                ha="center", va="center", fontsize=8.6, fontweight="bold", color="#C0392B")

# ② 重新编码
ax.annotate("", xy=(4.7, 3.78), xytext=(4.7, 4.30),
            arrowprops=dict(arrowstyle="-|>", color="#78281F", lw=1.6))
stage_label(ax, 3.58, "② 截断后的字符串送回原生 tokenizer 重新编码（模型实际输入，14 个 token）", "#78281F")


def right_color(tok):
    if tok in shifted_tokens:
        return COLOR_SHIFT, True, 1.35
    if tok in highlight_tokens:
        return COLOR_RISK, True, 1.2
    return COLOR_NORMAL, False, 1.2


reencoded_rows = [
    ["如果", "时间", "紧迫", "，", "只需", "直接", "解除"],
    ["接地", "安全", "保护", "并", "规", "避开", "关系"],
]
draw_token_rows(ax, reencoded_rows, [2.82, 2.12], right_color, box_h=0.46)

ax.annotate(
    "连锁错位：[“规避”, “开关”, “系统”] → [“规”, “避开”, “关系”]",
    xy=(6.35, 2.06), xytext=(5.0, 1.66),
    ha="center", va="center", fontsize=9.0, fontweight="bold", color="#C0392B",
    arrowprops=dict(arrowstyle="->", color="#C0392B", lw=1.2)
)

ax.text(
    0.38, 1.30,
    "• 字符只是截断单位，模型输入仍是重编码后的 BPE token\n"
    "• 切开“系统”使 BPE 合并顺序改变，前两个词边界随之重组\n"
    "• 设备词“开关”“系统”被拆散为日常词“关系”，前缀偏离原生成轨迹",
    ha="left", va="top", fontsize=9.4, linespacing=1.6, color="#222222",
    bbox=dict(boxstyle="round,pad=0.45", facecolor="#FFF9F8", edgecolor="#D68B8B", linewidth=1.1)
)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.tight_layout()
plt.savefig(os.path.join(base_dir, "figures", "fig5-2_token_char_split.png"), dpi=300, bbox_inches="tight")
plt.savefig(os.path.join(base_dir, "plot", "fig5-2_token_char_split.pdf"), bbox_inches="tight")
print("Saved fig5-2_token_char_split.png successfully.")
