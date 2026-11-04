# -*- coding: utf-8 -*-
"""
图2-4：不同领域-通用数据配比下的 CPT 性能对比
严格对齐正文表 tab:data-ratio 数值：
λ = [0, 0.33, 0.5, 0.67, 1]
DA = [43.5, 57.8, 68.2, 71.1, 72.4]
GS = [65.8, 64.3, 62.1, 57.4, 55.3]
S(λ) = [52.4, 60.9, 65.0, 63.5, 62.7]
"""

import matplotlib.pyplot as plt
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

lambdas = [0, 0.33, 0.5, 0.67, 1.0]
da = [43.5, 57.8, 68.2, 71.1, 72.4]
gs = [65.8, 64.3, 62.1, 57.4, 55.3]
s = [52.4, 60.9, 65.0, 63.5, 62.7]

fig, ax1 = plt.subplots(figsize=(8.8, 5.2), dpi=300)

color_da = "#1f77b4"
color_gs = "#d62728"
color_s = "#2ca02c"

ax1.set_xlabel("领域数据比例 $\\lambda$", fontsize=11.5)
ax1.set_ylabel("领域综合得分 DA (%)", color=color_da, fontsize=11.5)
line1 = ax1.plot(
    lambdas, da, marker="o", markersize=7, color=color_da,
    linewidth=2.2, label="领域综合得分 DA (%)"
)
ax1.tick_params(axis="y", labelcolor=color_da)
ax1.set_ylim(40, 80)
ax1.set_xlim(-0.04, 1.04)

ax2 = ax1.twinx()
ax2.set_ylabel("通用得分 GS / 综合得分 $S(\\lambda)$", color="#333333", fontsize=11.5)
line2 = ax2.plot(
    lambdas, gs, marker="s", markersize=7, color=color_gs,
    linewidth=2.2, linestyle="--", label="通用得分 GS"
)
line3 = ax2.plot(
    lambdas, s, marker="^", markersize=7.5, color=color_s,
    linewidth=2.3, label="综合得分 $S(\\lambda)$"
)
ax2.tick_params(axis="y", labelcolor="#333333")
ax2.set_ylim(50, 72)

# 垂直参考线标识 λ = 0.5 均衡配比
ax1.axvline(x=0.5, color="gray", linestyle=":", linewidth=1.3, alpha=0.8)

lines = line1 + line2 + line3
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc="lower center", fontsize=10, framealpha=0.95)

ax1.grid(True, linestyle="--", alpha=0.45)
ax1.set_xticks(lambdas)

plt.tight_layout()
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\figures\fig3-4_data_ratio.png", dpi=300, bbox_inches="tight")
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\plot\fig3-4_data_ratio.png", dpi=300, bbox_inches="tight")
print("Saved fig3-4_data_ratio.png successfully.")
