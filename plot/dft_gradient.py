# -*- coding: utf-8 -*-
"""
图3-x：CE 与 DFT 在目标 logit 上的梯度幅值
g_CE(p) = 1 - p,  g_DFT(p) = p (1 - p)
对应正文 DFT 推导第 (4)(5) 步：p = 0.1 / 0.9 的对比，以及 CPT 将 p 由 0.05 提升至 0.3
"""

import os
import numpy as np
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

p = np.linspace(0.001, 0.999, 500)
g_ce = 1 - p
g_dft = p * (1 - p)

c_ce, c_dft = "#d62728", "#1f77b4"

fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=300)
ax.plot(p, g_ce, color=c_ce, linewidth=2.3, label=r"CE：$g_{\mathrm{CE}}(p) = 1 - p$")
ax.plot(p, g_dft, color=c_dft, linewidth=2.3, label=r"DFT：$g_{\mathrm{DFT}}(p) = p\,(1 - p)$")

for pv, name in [(0.1, "表面连接词 $p_b$"), (0.9, "专业术语 $p_a$")]:
    ax.vlines(pv, 0, 1 - pv, colors="#999999", linestyles=":", linewidth=1.1)
    ax.plot(pv, 1 - pv, "o", color=c_ce, markersize=7, zorder=5)
    ax.plot(pv, pv * (1 - pv), "o", color=c_dft, markersize=7, zorder=5)
    ax.text(pv, -0.075, name, ha="center", va="top", fontsize=9.5, color="#444444")

ax.annotate("0.9", (0.1, 0.9), xytext=(10, 4), textcoords="offset points", fontsize=9.5, color=c_ce)
ax.annotate("0.1", (0.9, 0.1), xytext=(8, 4), textcoords="offset points", fontsize=9.5, color=c_ce)
ax.annotate("0.09", (0.1, 0.09), xytext=(8, -12), textcoords="offset points", fontsize=9.5, color=c_dft)
ax.annotate("0.09", (0.9, 0.09), xytext=(-30, -12), textcoords="offset points", fontsize=9.5, color=c_dft)

p0, p1 = 0.05, 0.3
ax.plot([p0, p1], [p0 * (1 - p0), p1 * (1 - p1)], "s", color="#2ca02c", markersize=6, zorder=6)
ax.annotate("", xy=(p1, p1 * (1 - p1)), xytext=(p0, p0 * (1 - p0)),
            arrowprops=dict(arrowstyle="-|>", color="#2ca02c", lw=1.8, connectionstyle="arc3,rad=-0.25"))
ax.text(0.33, 0.30, "CPT：$p$ 0.05→0.3\nDFT 梯度 0.048→0.21", fontsize=9.5, color="#2E6B2E", va="bottom")

ax.set_xlim(0, 1)
ax.set_ylim(0, 1.02)
ax.set_xlabel("目标 token 预测概率 $p$", fontsize=11, labelpad=18)
ax.set_ylabel("目标 logit 梯度幅值", fontsize=11)
ax.grid(True, linestyle="--", alpha=0.45)
ax.legend(loc="upper right", fontsize=10, framealpha=0.95)

plt.tight_layout()
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.savefig(os.path.join(base_dir, "figures", "dft_gradient.png"), dpi=300, bbox_inches="tight")
plt.savefig(os.path.join(base_dir, "plot", "dft_gradient.pdf"), bbox_inches="tight")
print("Saved dft_gradient.png successfully.")
