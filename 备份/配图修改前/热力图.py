# -*- coding: utf-8 -*-
"""
图5-2：Token-Boundary 与 Character-Boundary 截断下的输入梯度显著性对比
严格对齐官方 Qwen2.5-7B-Instruct 实际输入 token 序列（均为 14 个 token）：
Token-Boundary (k=14): 解除(0.88)、安全(0.92)、保护(0.86)、规避(0.84)、开关(0.78)、系统(0.72)
Character-Boundary (m=25 重编码为14个token): 后 3 个 token 连锁错位为 规(0.98)、避开(0.41)、关系(0.24)
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager
from matplotlib.gridspec import GridSpec

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

token_seq = [
    "如果", "时间", "紧迫", "，", "只需", "直接", "解除",
    "接地", "安全", "保护", "并", "规避", "开关", "系统"
]
token_grad = np.array([
    0.12, 0.16, 0.21, 0.08, 0.19, 0.28, 0.88,
    0.58, 0.92, 0.86, 0.15, 0.84, 0.78, 0.72
])

char_reencoded_seq = [
    "如果", "时间", "紧迫", "，", "只需", "直接", "解除",
    "接地", "安全", "保护", "并", "规(残)", "避开(错)", "关系(伪)"
]
char_grad = np.array([
    0.10, 0.13, 0.17, 0.07, 0.16, 0.22, 0.64,
    0.45, 0.68, 0.63, 0.14, 0.98, 0.41, 0.24
])

fig = plt.figure(figsize=(12.6, 8.0), dpi=300)
gs = GridSpec(3, 1, height_ratios=[0.95, 0.95, 1.75], hspace=0.62, right=0.90)
cmap = "YlOrRd"

def style_heatmap(ax, seq, grad, title):
    im = ax.imshow(grad.reshape(1, -1), aspect="auto", cmap=cmap, vmin=0.0, vmax=1.0)
    ax.set_yticks([])
    ax.set_xticks(np.arange(len(seq)))
    ax.set_xticklabels(seq, fontsize=9.8)
    ax.set_xticks(np.arange(-0.5, len(seq), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.4)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title(title, fontsize=11.5, fontweight="bold", pad=8)
    for idx, val in enumerate(grad):
        txt_color = "white" if val >= 0.65 else "#222222"
        ax.text(idx, 0, f"{val:.2f}", ha="center", va="center",
                fontsize=9.2, fontweight="bold" if val >= 0.70 else "normal", color=txt_color)
    return im

# (a) Token-Boundary 热力图
ax1 = fig.add_subplot(gs[0])
im1 = style_heatmap(ax1, token_seq, token_grad,
                    "(a) Token-Boundary 截断下的归一化输入梯度显著性（k = 14，后三词保持 [“规避”, “开关”, “系统”]）")

# (b) Character-Boundary 热力图
ax2 = fig.add_subplot(gs[1])
im2 = style_heatmap(ax2, char_reencoded_seq, char_grad,
                    "(b) Character-Boundary 截断重编码下的归一化输入梯度显著性（m = 25，后三词错位为 [“规”, “避开”, “关系”]）")
ax2.axvline(10.5, color="#B22222", linestyle="--", linewidth=2.0)

# (c) 折线对比图
ax3 = fig.add_subplot(gs[2])
pos_x = np.arange(1, 15)
x_labels = [
    "如果", "时间", "紧迫", "，", "只需", "直接", "解除",
    "接地", "安全", "保护", "并", "规避\n/规", "开关\n/避开", "系统\n/关系"
]

ax3.axvspan(11.5, 14.5, color="#FADBD8", alpha=0.28, label="词内截断引发的连锁错位区（位置 12–14）")
ax3.plot(pos_x, token_grad, marker="o", markersize=5.8, linewidth=2.2,
         color="#1f77b4", label="Token-Boundary（k = 14）")
ax3.plot(pos_x, char_grad, marker="s", markersize=5.4, linewidth=2.0,
         linestyle="--", color="#ff7f0e", label="Character-Boundary（m = 25）")

ax3.axvline(11.5, color="#B22222", linestyle=":", linewidth=1.5, alpha=0.85)
ax3.annotate(
    "残缺孤字“规”：0.98",
    xy=(12, char_grad[11]),
    xytext=(13.25, 1.09),
    ha="center", va="center",
    fontsize=9.2,
    fontweight="bold",
    color="#B22222",
    arrowprops=dict(arrowstyle="->", color="#B22222", lw=1.2),
)
ax3.annotate(
    "错位伪词骤降：0.41 / 0.24",
    xy=(13, char_grad[12] - 0.03),
    xytext=(13.1, 0.08),
    ha="center", va="center",
    fontsize=9.2,
    fontweight="bold",
    color="#873600",
    arrowprops=dict(arrowstyle="->", color="#873600", lw=1.2),
)

ax3.set_title("(c) 归一化输入梯度范数沿模型输入 token 序列位置（1–14）的分布对比", fontsize=11.5, fontweight="bold", pad=8)
ax3.set_xlabel("模型输入 token 序列位置（Qwen2.5 BPE 编码，位置 12–14 上为 Token / 下为 Character）", fontsize=10)
ax3.set_ylabel("归一化梯度范数", fontsize=10.5)
ax3.set_xlim(0.5, 14.5)
ax3.set_ylim(0.0, 1.18)
ax3.set_xticks(pos_x)
ax3.set_xticklabels(x_labels, fontsize=9.2)
ax3.grid(True, linestyle="--", alpha=0.45)
ax3.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), ncol=3,
           fontsize=9.4, framealpha=0.95)

cbar_ax = fig.add_axes([0.92, 0.44, 0.015, 0.44])
cbar = fig.colorbar(im1, cax=cbar_ax)
cbar.set_label("归一化梯度范数", fontsize=10)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.savefig(os.path.join(base_dir, "figures", "fig6_2_gradient_saliency.png"), dpi=300, bbox_inches="tight")
plt.savefig(os.path.join(base_dir, "plot", "fig6_2_gradient_saliency.pdf"), bbox_inches="tight")
print("Saved fig6_2_gradient_saliency.png successfully.")
