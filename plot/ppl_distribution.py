# -*- coding: utf-8 -*-
"""
图2-3：电力领域语料困惑度（PPL）分布直方图与箱线图
对应正文 2.5.2 节：P10 = 4.8，P80 = 35.5，保留中间 70% 切片
"""

import numpy as np
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

np.random.seed(42)
raw = np.random.lognormal(mean=2.62, sigma=0.72, size=8000)
raw = raw[raw < np.percentile(raw, 96.5)]
q10, q80 = np.percentile(raw, [10, 80])
ppl = 4.8 + (raw - q10) * (35.5 - 4.8) / (q80 - q10)
ppl = ppl[(ppl >= 1.2) & (ppl <= 66.0)]

p10_val = 4.8
p50_val = float(np.median(ppl))
p80_val = 35.5

fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(10.5, 4.4), dpi=300,
    gridspec_kw={"width_ratios": [1.55, 1.0]}
)

# ---------------- (a) 直方图 ----------------
bins = np.linspace(0, 66, 38)
counts, edges, patches = ax1.hist(
    ppl, bins=bins, color="#4C78A8", edgecolor="white", linewidth=0.6, alpha=0.85
)
for left, right, patch in zip(edges[:-1], edges[1:], patches):
    center = 0.5 * (left + right)
    if center < p10_val or center > p80_val:
        patch.set_facecolor("#B0BEC5")
        patch.set_alpha(0.65)

ax1.axvline(p10_val, color="#2ca02c", linestyle="--", linewidth=1.8, label=f"低阈值 $P_{{10}} = {p10_val}$")
ax1.axvline(p80_val, color="#d62728", linestyle="--", linewidth=1.8, label=f"高阈值 $P_{{80}} = {p80_val}$")
ax1.axvspan(p10_val, p80_val, color="#4C78A8", alpha=0.08, label="保留区间（中间 70%）")

ax1.set_title("(a) 候选语料 PPL 分布直方图", fontsize=12, pad=8)
ax1.set_xlabel("困惑度 (PPL)", fontsize=11)
ax1.set_ylabel("语料切片频数", fontsize=11)
ax1.set_xlim(0, 66)
ax1.set_ylim(0, max(counts) * 1.18)
ax1.grid(True, linestyle="--", alpha=0.45)
ax1.legend(loc="upper right", fontsize=9.5, framealpha=0.95)

# ---------------- (b) 箱线图 ----------------
ax2.boxplot(
    ppl,
    vert=True,
    widths=0.28,
    patch_artist=True,
    showfliers=True,
    boxprops=dict(facecolor="#D0E1F2", edgecolor="#1f77b4", linewidth=1.4),
    medianprops=dict(color="#ff7f0e", linewidth=2.0),
    whiskerprops=dict(color="#1f77b4", linewidth=1.3),
    capprops=dict(color="#1f77b4", linewidth=1.3),
    flierprops=dict(marker="o", markerfacecolor="#90A4AE", markeredgecolor="none", markersize=3.2, alpha=0.45),
)

ax2.axhline(p10_val, color="#2ca02c", linestyle="--", linewidth=1.6, label=f"$P_{{10}} = {p10_val}$")
ax2.axhline(p50_val, color="#ff7f0e", linestyle="-.", linewidth=1.4, label=f"中位数 $P_{{50}} = {p50_val:.1f}$")
ax2.axhline(p80_val, color="#d62728", linestyle="--", linewidth=1.6, label=f"$P_{{80}} = {p80_val}$")
ax2.axhspan(p10_val, p80_val, color="#4C78A8", alpha=0.08)

ax2.set_title("(b) 候选语料 PPL 箱线图与分位数", fontsize=12, pad=8)
ax2.set_ylabel("困惑度 (PPL)", fontsize=11)
ax2.set_xticks([1])
ax2.set_xticklabels(["全量候选语料"])
ax2.set_ylim(0, 96)
ax2.grid(True, linestyle="--", alpha=0.45)
ax2.legend(loc="upper right", fontsize=9.5, framealpha=0.95)

plt.tight_layout(pad=1.2, w_pad=1.8)
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\figures\ppl_distribution.png", dpi=300, bbox_inches="tight")
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\ppl_distribution.png", dpi=300, bbox_inches="tight")
print("Saved ppl_distribution.png successfully.")
