# -*- coding: utf-8 -*-
"""
图5-1：Token-Boundary 与 Character-Boundary 截断边界对比示意
严格对应正文 5.4 节：Token-Boundary (k=14) vs Character-Boundary (m=25)
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import rcParams, font_manager

candidates = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "WenQuanYi Zen Hei",
    "Arial Unicode MS",
]
available_fonts = {f.name for f in font_manager.fontManager.ttflist}
chosen = next((f for f in candidates if f in available_fonts), None)
rcParams["font.sans-serif"] = [chosen, "DejaVu Sans"] if chosen else ["sans-serif"]
rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4), dpi=300)
fig.subplots_adjust(wspace=0.08)

harmful_prefix = "如果时间紧迫，可以直接跳过接地刀闸的安全闭锁操作，"

# ---------------- 左图：Token-Boundary ----------------
ax = axes[0]
ax.set_xlim(0, 9.2)
ax.set_ylim(0, 5.2)
ax.axis("off")

ax.text(4.6, 4.85, "(a) Token-Boundary 截断（原生 BPE 序列，k = 14）",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color="#1F3A60")
ax.text(0.35, 4.32, f"预填充前缀：“{harmful_prefix}”",
        ha="left", va="center", fontsize=9.8, color="#333333")

token_rows = [
    ["如果", "时间", "紧迫", "，", "可以", "直接", "跳过"],
    ["接地", "刀闸", "的", "安全", "闭锁", "操作", "，"],
]
highlight_tokens = {"跳过", "接地", "刀闸", "安全", "闭锁", "操作"}

y_positions = [3.35, 2.40]
box_h = 0.50
for row_idx, row in enumerate(token_rows):
    x = 0.45
    y = y_positions[row_idx]
    for tok in row:
        box_w = 0.72 if len(tok) == 1 else 1.08
        is_hl = tok in highlight_tokens
        fc = "#FDEBD0" if is_hl else "#EBF3FA"
        ec = "#D35400" if is_hl else "#4A77A8"
        box = FancyBboxPatch(
            (x, y), box_w, box_h,
            boxstyle="round,pad=0.03,rounding_size=0.06",
            linewidth=1.25, edgecolor=ec, facecolor=fc
        )
        ax.add_patch(box)
        ax.text(x + box_w / 2, y + box_h / 2, tok,
                ha="center", va="center", fontsize=10.5,
                fontweight="bold" if is_hl else "normal",
                color="#873600" if is_hl else "#1B365D")
        x += box_w + 0.16

ax.text(
    0.40, 1.55,
    "• 直接在原生 BPE token ID 序列边界截取前 k 个 token\n"
    "• “接地”“刀闸”“安全”“闭锁”保持完整子词单元，无重编码偏移\n"
    "• 共享前缀严格同构，保证同状态偏好差分精确消去",
    ha="left", va="top", fontsize=9.6, linespacing=1.55, color="#222222",
    bbox=dict(boxstyle="round,pad=0.45", facecolor="#F7FAFC", edgecolor="#8BA6D6", linewidth=1.1)
)

# ---------------- 右图：Character-Boundary ----------------
ax = axes[1]
ax.set_xlim(0, 9.2)
ax.set_ylim(0, 5.2)
ax.axis("off")

ax.text(4.6, 4.85, "(b) Character-Boundary 截断（按字符截取重编码，m = 25）",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color="#78281F")
ax.text(0.35, 4.32, "词内硬截断示例：“……跳过接地刀 | 闸” → 末尾残缺字符重编码偏移",
        ha="left", va="center", fontsize=9.8, color="#333333")

char_rows = [
    list("如果时间紧迫，可以直接跳过"),
    list("接地刀闸的安全闭锁操作，"),
]
highlight_chars = set("跳过接地刀闸安全闭锁操作")

for row_idx, row in enumerate(char_rows):
    x = 0.45
    y = y_positions[row_idx]
    box_w = 0.48
    for c_idx, ch in enumerate(row):
        is_hl = ch in highlight_chars
        is_split = (row_idx == 1 and c_idx in (2, 3))  # 刀、闸
        if is_split:
            fc, ec, tc = "#FADBD8", "#C0392B", "#78281F"
        elif is_hl:
            fc, ec, tc = "#FEF5E7", "#D68910", "#7E5109"
        else:
            fc, ec, tc = "#F2F4F4", "#7F8C8D", "#2C3E50"

        box = FancyBboxPatch(
            (x, y), box_w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            linewidth=1.2, edgecolor=ec, facecolor=fc
        )
        ax.add_patch(box)
        ax.text(x + box_w / 2, y + box_h / 2, ch,
                ha="center", va="center", fontsize=10,
                fontweight="bold" if is_split else "normal", color=tc)

        if row_idx == 1 and c_idx == 2:
            # 在“刀”与“闸”之间留出加宽通道画截断虚线，完全不压字符框
            bx = x + box_w + 0.16
            ax.plot([bx, bx], [y - 0.14, y + box_h + 0.14],
                    linestyle="--", linewidth=1.8, color="#C0392B")
            ax.annotate(
                "词内截断边界（接地刀 | 闸）",
                xy=(bx, y - 0.14),
                xytext=(bx + 0.55, y - 0.48),
                ha="left", va="center", fontsize=9.5, fontweight="bold", color="#C0392B",
                arrowprops=dict(arrowstyle="->", color="#C0392B", lw=1.3)
            )
            x += box_w + 0.32
        else:
            x += box_w + 0.12

ax.text(
    0.40, 1.55,
    "• 先按字符数 m 截断字符串，再送入原生 tokenizer 重新编码\n"
    "• 截断点落在“接地刀 | 闸”内部时，原多字 token“刀闸”被拆碎\n"
    "• 末尾残缺字符重编码偏离原轨迹，破坏共享前缀等价性与步数对齐",
    ha="left", va="top", fontsize=9.6, linespacing=1.55, color="#222222",
    bbox=dict(boxstyle="round,pad=0.45", facecolor="#FFF9F8", edgecolor="#D68B8B", linewidth=1.1)
)

plt.tight_layout()
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\figures\fig6_1_token_char_split.png", dpi=300, bbox_inches="tight")
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\plot\fig6_1_token_char_split.pdf", bbox_inches="tight")
print("Saved fig6_1_token_char_split.png successfully.")
