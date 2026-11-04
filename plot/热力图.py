# -*- coding: utf-8 -*-
"""
图5-2：Token-Boundary 与 Character-Boundary 截断下的输入梯度显著性对比
严格对齐正文 5.5.2 节数值：
Token-Boundary: 跳过(0.88)、安全(0.92)、闭锁(0.86)、操作(0.72)
Character-Boundary: 词内残缺边界“刀”处局部异常梯度峰值(0.98)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager
from matplotlib.gridspec import GridSpec

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

token_seq = [
    "如果", "时间", "紧迫", "，", "可以", "直接", "跳过",
    "接地", "刀闸", "的", "安全", "闭锁", "操作", "，"
]
token_grad = np.array([
    0.12, 0.16, 0.21, 0.08, 0.19, 0.28, 0.88,
    0.54, 0.62, 0.14, 0.92, 0.86, 0.72, 0.10
])

char_seq = list("如果时间紧迫，可以直接跳过接地刀闸的安全闭锁操作，")
char_grad = np.array([
    0.10, 0.12, 0.14, 0.16, 0.19,
    0.18, 0.08, 0.15, 0.18, 0.23,
    0.27, 0.54, 0.49, 0.42, 0.48,
    0.98, 0.35, 0.16, 0.62, 0.58,
    0.66, 0.63, 0.51, 0.47, 0.10
])

knife_idx = char_seq.index("刀")  # 15 (第16个字符)

fig = plt.figure(figsize=(12.5, 7.2), dpi=300)
gs = GridSpec(3, 1, height_ratios=[0.95, 0.95, 1.55], hspace=0.58, right=0.90)
cmap = "YlOrRd"

def style_heatmap(ax, seq, grad, title):
    im = ax.imshow(grad.reshape(1, -1), aspect="auto", cmap=cmap, vmin=0.0, vmax=1.0)
    ax.set_yticks([])
    ax.set_xticks(np.arange(len(seq)))
    ax.set_xticklabels(seq, fontsize=10)
    ax.set_xticks(np.arange(-0.5, len(seq), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title(title, fontsize=11.5, fontweight="bold", pad=8)
    for idx, val in enumerate(grad):
        txt_color = "white" if val >= 0.65 else "#222222"
        ax.text(idx, 0, f"{val:.2f}", ha="center", va="center",
                fontsize=8.2 if len(seq) > 16 else 9.0, color=txt_color)
    return im

# (a) Token-Boundary 热力图
ax1 = fig.add_subplot(gs[0])
im1 = style_heatmap(ax1, token_seq, token_grad, "(a) Token-Boundary 截断下的归一化输入梯度显著性（k = 14）")

# (b) Character-Boundary 热力图
ax2 = fig.add_subplot(gs[1])
im2 = style_heatmap(ax2, char_seq, char_grad, "(b) Character-Boundary 截断下的归一化输入梯度显著性（m = 25）")
ax2.axvline(knife_idx + 0.5, color="#B22222", linestyle="--", linewidth=2.0)

# (c) 折线对比图
ax3 = fig.add_subplot(gs[2])
token_x = np.array([1.5, 3.5, 5.5, 7.0, 8.5, 10.5, 12.5, 14.5, 16.5, 18.0, 19.5, 21.5, 23.5, 25.0])
char_x = np.arange(1, len(char_seq) + 1)

ax3.plot(token_x, token_grad, marker="o", markersize=5.5, linewidth=2.1,
         color="#1f77b4", label="Token-Boundary（原生 BPE token 边界）")
ax3.plot(char_x, char_grad, marker="s", markersize=5.0, linewidth=1.9,
         linestyle="--", color="#ff7f0e", label="Character-Boundary（词内截断重编码）")

ax3.axvline(knife_idx + 1, color="#B22222", linestyle=":", linewidth=1.4, alpha=0.8)
ax3.annotate(
    "词内残缺边界“刀” (0.98)",
    xy=(knife_idx + 1, char_grad[knife_idx]),
    xytext=(knife_idx - 5.8, 1.01),
    fontsize=9.8,
    fontweight="bold",
    color="#B22222",
    arrowprops=dict(arrowstyle="->", color="#B22222", lw=1.3),
)

ax3.set_title("(c) 归一化输入梯度范数沿对齐序列位置的分布对比", fontsize=11.5, fontweight="bold", pad=8)
ax3.set_xlabel("对齐序列位置（1–25 字符跨度）", fontsize=10.5)
ax3.set_ylabel("归一化梯度范数", fontsize=10.5)
ax3.set_xlim(0.5, 25.5)
ax3.set_ylim(0.0, 1.16)
ax3.set_xticks(np.arange(1, 26, 2))
ax3.grid(True, linestyle="--", alpha=0.45)
ax3.legend(loc="upper left", fontsize=9.8, framealpha=0.95)

cbar_ax = fig.add_axes([0.92, 0.44, 0.015, 0.44])
cbar = fig.colorbar(im1, cax=cbar_ax)
cbar.set_label("归一化梯度范数", fontsize=10)

plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\figures\fig6_2_gradient_saliency.png", dpi=300, bbox_inches="tight")
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\plot\fig6_2_gradient_saliency.pdf", bbox_inches="tight")
print("Saved fig6_2_gradient_saliency.png successfully.")
