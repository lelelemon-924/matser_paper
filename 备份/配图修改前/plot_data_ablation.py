# -*- coding: utf-8 -*-
"""
图2-4：不同领域-通用数据配比下的 CPT 性能对比
严格对齐正文表 tab:data-ratio 数值（DA、GS、S 均为百分比，共用同一纵轴）：
λ = [0, 0.33, 0.5, 0.67, 1]
DA = [44.1, 57.8, 68.2, 71.1, 72.4]
GS = [66.0, 64.3, 62.1, 57.4, 55.3]
S(λ) = [52.9, 60.9, 65.0, 63.5, 62.7]
（基座模型 DA 43.5、GS 65.8 单列于表中，不在本图绘出）
"""

import os
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager

candidates = [
    "PingFang SC",
    "Heiti TC",
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
da = [44.1, 57.8, 68.2, 71.1, 72.4]
gs = [66.0, 64.3, 62.1, 57.4, 55.3]
s = [52.9, 60.9, 65.0, 63.5, 62.7]

fig, ax = plt.subplots(figsize=(8.8, 5.2), dpi=300)

ax.plot(lambdas, da, marker="o", markersize=7, color="#1f77b4",
        linewidth=2.2, label="PowerQA 得分")
ax.plot(lambdas, gs, marker="s", markersize=7, color="#d62728",
        linewidth=2.2, linestyle="--", label="通用得分 GS")
ax.plot(lambdas, s, marker="^", markersize=7.5, color="#2ca02c",
        linewidth=2.3, label="均衡得分 $S(\\lambda)$")

for x, y in zip(lambdas, s):
    ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, -15),
                ha="center", fontsize=9, color="#2ca02c",
                fontweight="bold" if x == 0.5 else "normal")

ax.axvline(x=0.5, color="gray", linestyle=":", linewidth=1.3, alpha=0.8)

ax.set_xlabel("领域数据比例 $\\lambda$", fontsize=11.5)
ax.set_ylabel("得分（%）", fontsize=11.5)
ax.set_xlim(-0.04, 1.04)
ax.set_ylim(40, 76)
ax.set_xticks(lambdas)
ax.grid(True, linestyle="--", alpha=0.45)
ax.legend(loc="lower right", fontsize=10, framealpha=0.95)

plt.tight_layout()
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.savefig(os.path.join(base_dir, "figures", "fig3-4_data_ratio.png"), dpi=300, bbox_inches="tight")
plt.savefig(os.path.join(base_dir, "plot", "fig3-4_data_ratio.png"), dpi=300, bbox_inches="tight")
print("Saved fig3-4_data_ratio.png successfully.")
