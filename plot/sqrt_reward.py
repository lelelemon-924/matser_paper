# -*- coding: utf-8 -*-
"""
图：线性奖励 r = p 与开根号奖励 r = sqrt(p) 的对比（第 4 章式 eq:intensity-reward）
(a) 奖励映射：标注 0.04→0.25 与 0.81→1.0 两段概率提升带来的奖励增量
(b) 斜率 dr/dp：开根号在 p < 0.25 时放大、p > 0.25 时抑制
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
rcParams["mathtext.fontset"] = "stix"

C_LIN = "#8C8C8C"
C_SQRT = "#2C6CA2"
C_LOW = "#D64545"
C_HIGH = "#C49618"

p = np.linspace(1e-4, 1.0, 600)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0))

# (a) 奖励映射
ax1.plot(p, p, "--", color=C_LIN, lw=1.8, label=r"线性：$r = p$")
ax1.plot(p, np.sqrt(p), "-", color=C_SQRT, lw=2.2, label=r"开根号：$r = \sqrt{p}$")
for (a, b), c in [((0.04, 0.25), C_LOW), ((0.81, 1.0), C_HIGH)]:
    ax1.axvspan(a, b, color=c, alpha=0.10, lw=0)
    ax1.plot([a, b], [np.sqrt(a), np.sqrt(b)], "o", color=c, ms=4.5, zorder=5)

ax1.annotate("", xy=(0.25, 0.5), xytext=(0.25, 0.2),
             arrowprops=dict(arrowstyle="<->", color=C_LOW, lw=1.4))
ax1.text(0.30, 0.12, "0.04→0.25\n" + r"$\Delta\sqrt{p}=0.30$" + "\n" + r"$\Delta p=0.21$",
         color=C_LOW, fontsize=9, va="center")
ax1.annotate("", xy=(0.79, 1.0), xytext=(0.79, 0.9),
             arrowprops=dict(arrowstyle="<->", color=C_HIGH, lw=1.4))
ax1.text(0.985, 0.55, "0.81→1.0\n" + r"$\Delta\sqrt{p}=0.10$" + "\n" + r"$\Delta p=0.19$",
         color=C_HIGH, fontsize=9, va="center", ha="right")

ax1.set_xlim(0, 1.0)
ax1.set_ylim(0, 1.05)
ax1.set_xlabel(r"目标类别概率 $p = P_k(c_k \mid x, o)$")
ax1.set_ylabel(r"单类目奖励 $r$")
ax1.set_title("(a) 奖励映射", fontsize=11)
ax1.legend(loc="upper left", frameon=False, fontsize=9)
ax1.grid(alpha=0.25)

# (b) 斜率
ax2.plot(p, np.ones_like(p), "--", color=C_LIN, lw=1.8, label=r"线性：$\mathrm{d}r/\mathrm{d}p = 1$")
ax2.plot(p, 0.5 / np.sqrt(p), "-", color=C_SQRT, lw=2.2,
         label=r"开根号：$\mathrm{d}r/\mathrm{d}p = 1/(2\sqrt{p})$")
ax2.axvspan(0, 0.25, color=C_LOW, alpha=0.10, lw=0)
ax2.axvspan(0.25, 1.0, color=C_HIGH, alpha=0.08, lw=0)
ax2.axvline(0.25, color="black", lw=0.8, ls=":")
ax2.text(0.125, 3.3, "放大区\n斜率 > 1", color=C_LOW, fontsize=9.5, ha="center")
ax2.text(0.62, 3.3, "抑制区\n斜率 < 1", color=C_HIGH, fontsize=9.5, ha="center")
ax2.text(0.262, 0.15, r"$p = 0.25$", fontsize=9)

ax2.set_xlim(0, 1.0)
ax2.set_ylim(0, 4.0)
ax2.set_xlabel(r"目标类别概率 $p$")
ax2.set_ylabel(r"奖励对概率的斜率 $\mathrm{d}r/\mathrm{d}p$")
ax2.set_title("(b) 奖励灵敏度", fontsize=11)
ax2.legend(loc="upper right", frameon=False, fontsize=9, bbox_to_anchor=(1.0, 0.78))
ax2.grid(alpha=0.25)

fig.tight_layout()
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
fig.savefig(os.path.join(out_dir, "fig4_sqrt_reward.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(out_dir, "fig4_sqrt_reward.png"), dpi=200, bbox_inches="tight")
print("saved")
